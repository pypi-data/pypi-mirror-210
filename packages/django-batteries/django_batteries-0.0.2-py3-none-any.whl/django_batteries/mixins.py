class ListSerializerMixin:
    """Use this mixin to be able to define list_serializer_class that
    will be used only for list action"""

    list_serializer_class = None
    serializer_class = None

    list_queryset = None
    queryset = None

    def get_serializer_class(self):
        assert self.list_serializer_class, "Use must set 'list_serializer_class' in order to use ListSerializerMixin"
        if self.action == "list":
            return self.list_serializer_class
        else:
            return super().get_serializer_class()

    def get_queryset(self):
        if self.action == "list" and self.list_queryset is not None:
            return self.list_queryset
        else:
            return super().get_queryset()
