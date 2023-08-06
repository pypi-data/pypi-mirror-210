from django.db.models import Model, QuerySet
from django.db.models.manager import BaseManager

from .mixins import PostFetchModelMixin, PostFetchQuerySetMixin

__all__ = [
    "PostFetchManager",
    "PostFetchModel",
    "PostFetchQuerySet",
]


class PostFetchQuerySet(PostFetchQuerySetMixin, QuerySet):
    pass


class PostFetchManager(BaseManager.from_queryset(PostFetchQuerySet)):
    pass


class PostFetchModel(PostFetchModelMixin, Model):
    """Model with post fetch hooks."""

    objects = PostFetchManager()

    class Meta:
        abstract = True
        # Django knows to use the custom QuerySet
        # for related managers based on this setting.
        base_manager_name = "objects"
