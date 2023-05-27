from django_filters import rest_framework as filters

from recipes.models import Recipes
from tag.models import Tag


class RecipeFilter(filters.FilterSet):
    """Фильтр по избранному, автору, списку покупок и тэгам"""

    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        queryset=Tag.objects.all(),
        to_field_name="slug",
    )
    is_favorited = filters.BooleanFilter(method="get_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(
        method="get_is_in_shopping_cart"
    )

    class Meta:
        model = Recipes
        fields = ("tags", "author", "is_favorited", "is_in_shopping_cart")

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(favorites__user=user)
        return Recipes.objects.all()

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(shopping_cart__user=user)
        return Recipes.objects.all()
