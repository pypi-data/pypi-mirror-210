# Django-batteries

This package contains useful utilities for django/drf project

## Models

Contains set of abstract models to enforce DRY principle for most common use cases

### `django_batteries.models.TimeStampedModel`

- `created`
- `modified`

### `django_batteries.models.TimeFramedModel`

- `start`
- `end`

  For time bound entities

### `django_batteries.models.DescriptionModel`

- `description`

### `django_batteries.models.TitleModel`

- `title`

### `django_batteries.models.TitleDescriptionModel`

- `title`
- `description`

## Fields

### Monitor field

A DateTimeField that monitors another field on the same model and sets itself to the current date/time whenever the monitored field
changes.
use it like this in your models:
class MyMode(models.Model):

    title = models.Charfield(max_length=50)
    title_changed = MonitorField(_('title changed'), monitor='title')

## Mixins

### `django_batteries.mixins.ListSerializerMixin`

Allow you to specify `list_serializer_class` that will be used only in list action

## Paginators

### django_batteries.paginators.ResultSetPagination

Paginator with `page_size` as query parameter for setting page size

### django_batteries.paginators.SingleResultPaginator

Custom paginator class that returns not paginated(detail result) if qs result have only 1 item

## Utils

### django_batteries.utils.qs_admin_or_author

Return all objects if user is staff, otherwise return objects owned by user
