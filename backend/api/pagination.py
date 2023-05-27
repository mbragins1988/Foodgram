from rest_framework.pagination import PageNumberPagination


class LimitPagesPaginator(PageNumberPagination):
    """Пагинация с перееопределением названия поля."""

    page_size_query_param = "limit"
