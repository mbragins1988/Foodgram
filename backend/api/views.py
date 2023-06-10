from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from api.filters import NameFilter, RecipeFilter
from api.pagination import LimitPagesPaginator
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (AddRecipeSerializer, FollowSerializer,
                             IngredientSerializer, ShortRecipeSerializer,
                             ShowRecipeSerializer, TagSerializer,
                             UserSerializer)
from api.shopping_cart import shopping_cart
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart)
from tag.models import Tag
from users.models import Follow, User


class UserViewSet(UserViewSet):
    """Вьюсет пользователя."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPagesPaginator

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            serializer = FollowSerializer(author,
                                          data=request.data,
                                          context={'request': request})
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        follow = get_object_or_404(Follow,
                                   user=user,
                                   author=author)
        follow.delete()
        return Response(
            f'Вы отписались от {follow.author}',
            status=status.HTTP_204_NO_CONTENT,
        )


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет тэгов к рецептам."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (NameFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitPagesPaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return ShowRecipeSerializer
        return AddRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def add_or_delete(self, model, where, request, user, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        obj = model.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if obj.exists():
                return Response(
                    {'errors': f'Рецепт уже есть {where}'},
                    status=status.HTTP_400_BAD_REQUEST)
            model.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('post', 'delete'),
        detail=True,
    )
    def favorite(self, request, pk=None):
        user = request.user
        where = 'в избранном'
        return self.add_or_delete(FavoriteRecipe, where, request, user, pk)

    @action(
        methods=('post', 'delete'),
        detail=True,
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        where = 'в списке покупок'
        return self.add_or_delete(ShoppingCart, where, request, user, pk)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shopping_cart__user=request.user
            )
            .values(
                'ingredient__name',
                'ingredient__measurement_unit',
            )
            .annotate(sum_ingredients=Sum('amount'))
        )
        return shopping_cart(ingredients)
