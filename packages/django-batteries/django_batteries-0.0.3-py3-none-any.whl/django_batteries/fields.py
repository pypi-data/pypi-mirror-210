from django.db import models
from django.utils.timezone import now


class AutoCreatedField(models.DateTimeField):
    """
    A DateTimeField that automatically populates itself at
    object creation.
    By default, sets editable=False, default=datetime.now.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("editable", False)
        kwargs.setdefault("default", now)
        super().__init__(*args, **kwargs)


class AutoLastModifiedField(AutoCreatedField):
    """
    A DateTimeField that updates itself on each save() of the model.
    By default, sets editable=False and default=datetime.now.
    """

    def get_default(self):
        """Return the default value for this field."""
        if not hasattr(self, "_default"):
            self._default = self._get_default()
        return self._default

    def pre_save(self, model_instance, add):
        value = now()
        if add:
            current_value = getattr(model_instance, self.attname, self.get_default())
            if current_value != self.get_default():
                # when creating an instance and the modified date is set
                # don't change the value, assume the developer wants that
                # control.
                value = getattr(model_instance, self.attname)
            else:
                for field in model_instance._meta.get_fields():
                    if isinstance(field, AutoCreatedField):
                        value = getattr(model_instance, field.name)
                        break
        setattr(model_instance, self.attname, value)
        return value


class MonitorField(models.DateTimeField):
    """
    A DateTimeField that monitors another field on the same model and
    sets itself to the current date/time whenever the monitored field
    changes.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("default", now)
        monitor = kwargs.pop("monitor", None)
        if not monitor:
            raise TypeError(f'{self.__class__.__name__} requires a "monitor" argument')
        self.monitor = monitor
        when = kwargs.pop("when", None)
        if when is not None:
            when = set(when)
        self.when = when
        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        self.monitor_attname = f"_monitor_{name}"
        models.signals.post_init.connect(self._save_initial, sender=cls)
        super().contribute_to_class(cls, name)

    def get_monitored_value(self, instance):
        return getattr(instance, self.monitor)

    def _save_initial(self, sender, instance, **kwargs):
        if self.monitor in instance.get_deferred_fields():
            # Fix related to issue #241 to avoid recursive error on double monitor fields
            return
        setattr(instance, self.monitor_attname, self.get_monitored_value(instance))

    def pre_save(self, model_instance, add):
        value = now()
        previous = getattr(model_instance, self.monitor_attname, None)
        current = self.get_monitored_value(model_instance)
        if previous != current and (self.when is None or current in self.when):
            setattr(model_instance, self.attname, value)
            self._save_initial(model_instance.__class__, model_instance)
        return super().pre_save(model_instance, add)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["monitor"] = self.monitor
        if self.when is not None:
            kwargs["when"] = self.when
        return name, path, args, kwargs
