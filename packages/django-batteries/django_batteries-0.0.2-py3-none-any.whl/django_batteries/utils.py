import contextlib


def qs_admin_or_author(view, qs):
    """qs_admin_or_author
    Returns all models if the user is an admin, otherwise returns
    only the current user's model instance without pagination.

    Args:
        request: HttpRequest object representing the current request.
        model: Django model class representing targeted model.

    """
    # * If admin user return all
    if view.request.user.is_staff:
        return qs
    # * Return only current user data and remove pagination
    with contextlib.suppress(AttributeError):
        view.list_serializer_class = view.serializer_class
    return qs.filter(user=view.request.user)
