from rest_framework.pagination import CursorPagination as BaseCursorPagination


class CursorPagination(BaseCursorPagination):
    """Custom CursorPagination that handles our models.

    Many Kegbot models have a "created" column, except it's unfortunately
    not named consistently; so we can't use the stock implementation.

    For now, use `id` everywhere. This mostly defeats the point of cursor
    pagination since result sets may be unstable, but will at least get
    API callers used to the contract of fetching/supplying an opaque
    cursor. We can fix the implementation later.
    """

    def get_ordering(self, request, queryset, view):
        return ("-id",)
