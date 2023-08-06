from django.db.models import Model
from django.db.models.query import BaseIterable
from django.db.models.sql import Query

from .typing import Any, Callable, Optional, TypeVar

__all__ = [
    "PostFetchModelMixin",
    "PostFetchQuerySetMixin",
]


TModel = TypeVar("TModel", bound=Model)
NestedDict = dict[str, "NestedDict"]


class PostFetchQuerySetMixin:
    """Patches QuerySet so that results can be modified right after they are fetched but before they are cached."""

    model: type[TModel]
    query: Query
    _result_cache: list[Any]
    _prefetch_related_lookups: dict[str, Any]
    _iterable_class: type[BaseIterable]
    _prefetch_done: bool
    _prefetch_related_objects: Callable[[], None]

    def _fetch_all(self) -> None:
        if self._result_cache is None:
            results: list[Any] = list(self._iterable_class(self))  # type: ignore
            select_related = self._get_select_related_fields()
            self._result_cache = self._post_fetch(results, select_related)
        if self._prefetch_related_lookups and not self._prefetch_done:  # pragma: no cover
            self._prefetch_related_objects()

    def _get_select_related_fields(self) -> NestedDict:
        select_related: NestedDict = {}
        if isinstance(self.query.select_related, dict):
            select_related = self.query.select_related
        elif self.query.select_related is True:
            select_related = {field.name: {} for field in self.model._meta.fields if field.is_relation}
        return select_related

    def _post_fetch(self, rows: list[Any], select_related: NestedDict) -> list[Any]:
        for i, row in enumerate(rows):
            if isinstance(row, dict):
                rows[i] = self.model.post_fetch_values_hook(row, getattr(self, "_fields", ()))
            elif isinstance(row, tuple):
                rows[i] = self.model.post_fetch_values_list_hook(row, getattr(self, "_fields", ()))
            elif isinstance(row, Model):
                rows[i] = self.model.post_fetch_hook(row)
                self._related_post_fetch(rows[i], select_related)
            else:
                rows[i] = self.model.post_fetch_values_list_flat_hook(row, getattr(self, "_fields", (None,))[0])
        return rows

    def _related_post_fetch(self, model: Model, select_related: NestedDict) -> None:
        for field, nested_select_related in select_related.items():
            related_model: Optional[Model] = getattr(model, field, None)
            if related_model is None:  # null or invalid relations
                continue
            related_model_post_fetch_hook = getattr(related_model, "post_fetch_hook", None)
            if callable(related_model_post_fetch_hook):
                setattr(model, field, related_model_post_fetch_hook(related_model))
            if nested_select_related:
                self._related_post_fetch(related_model, nested_select_related)


class PostFetchModelMixin:
    @classmethod
    def post_fetch_hook(cls, model: TModel) -> TModel:
        """If model instance is accessed with model.objects.get(), model.objects.all(), etc.."""
        return model  # pragma: no cover

    @classmethod
    def post_fetch_values_hook(cls, values: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
        """If model values are accessed with qs.values()."""
        return values  # pragma: no cover

    @classmethod
    def post_fetch_values_list_hook(cls, values: tuple[Any, ...], fields: tuple[str, ...]) -> tuple[Any, ...]:
        """If model values are accessed with qs.values_list()."""
        return values  # pragma: no cover

    @classmethod
    def post_fetch_values_list_flat_hook(cls, value: Any, field: str) -> Any:
        """If model values are accessed with qs.values_list(flat=True)"""
        return value  # pragma: no cover
