from django.core.exceptions import ValidationError
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (FavoriteRecipe, Ingredients, RecipeIngredient,
                            Recipes, ShoppingCart)
from tag.models import Tag
from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user.id
        return Follow.objects.filter(
            author=obj.id, user=user).exists()


class FollowSerializer(UserSerializer):
    """Сериализатор подписoк."""

    recipes_count = serializers.IntegerField(source='recipes.count',
                                             read_only=True)
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(default=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'recipes_count', 'recipes',
                  'is_subscribed')
        read_only_fields = ('email', 'username',
                            'first_name', 'last_name')

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        serializer = ShortRecipeSerializer(recipes, many=True)
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredients
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор краткого отображения рецепта."""

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class ShowIngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор отоброжения ингридиента при создание рецепта."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 'name', 'measurement_unit', 'amount'
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиентов."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class AddRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления рецепта."""

    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = (
            'id', 'ingredients', 'tags', 'image', 'name',
            'text', 'cooking_time', 'author',
        )

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError('Добавьте ингредиенты')
        for i in value:
            if i['amount'] <= 0:
                raise ValidationError(
                    'Добавьте один или несколько ингредиентов'
                )
        return value

    @staticmethod
    def __add_ingredients(ingredients, recipe):
        ingredients_to_add = [
            RecipeIngredient(
                ingredient=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount'),
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(ingredients_to_add)

    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        image = validated_data.pop('image')
        recipe = Recipes.objects.create(
            image=image, author=author, **validated_data
        )
        self.__add_ingredients(ingredients_data, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self.__add_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)

    def to_representation(self, recipe):
        return ShowRecipeSerializer(
            recipe, context={"request": self.context.get("request")}
        ).data


class ShowRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор отображения рецепта."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    @staticmethod
    def get_ingredients(obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return ShowIngredientsInRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            recipe=obj, user=request.user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверяем в корзине ли рецепт."""
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            recipe=obj, user=request.user
        ).exists()


# class FavoriteRecipeSerializer(serializers.ModelSerializer):
#     """Сериализатор избранного."""

#     user = serializers.HiddenField(
#         default=UserSerializer(read_only=True)
#     )
#     recipe = ShortRecipeSerializer(read_only=True)

#     class Meta:

#         model = FavoriteRecipe
#         fields = ("user", "recipe")
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=FavoriteRecipe.objects.all(),
#                 fields=("user", "recipe"),
#                 message="Рецепт уже в избранном",
#             )
#         ]


# class ShoppingCartSerializer(serializers.ModelSerializer):
#     """Сериализатор списка покупок."""

#     user = serializers.HiddenField(
#         default=UserSerializer(read_only=True)
#     )
#     recipe = ShortRecipeSerializer(read_only=True)

#     class Meta:
#         model = ShoppingCart
#         fields = ("user", "recipe")
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=ShoppingCart.objects.all(),
#                 fields=("user", "recipe"),
#                 message="Рецепт уже в списке покупок",
#             )
#         ]
