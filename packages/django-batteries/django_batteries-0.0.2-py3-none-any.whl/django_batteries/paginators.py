from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ResultSetPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 200
    page_size_query_param = "page_size"


class SingleResultPaginator(ResultSetPagination):
    """SingleResultPaginator

    A custom pagination class that returns a single non-paginated response if
    the queryset being paginated only contains one item.
    """

    def get_paginated_response(self, data):
        if len(data) == 1:
            return Response(data[0])
        return super().get_paginated_response(data)
