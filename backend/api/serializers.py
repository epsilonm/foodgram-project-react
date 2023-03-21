from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from recipes.models import (
    Tag, Ingredient, Recipe, RecipeAmount, Favorite, ShoppingCart
    )

User = get_user_model()


class UserSerializer(UserSerializer):
    """Сериализатор для вывода информации о пользователе."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
            )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода информации об ингредиентах."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeAmountSerializer(serializers.ModelSerializer):
    """Сериализатор связи ингредиентов и рецепта."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
        )

    class Meta:
        model = RecipeAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода информации о тэгах."""
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра рецептов."""
    tags = TagSerializer(many=True)
    ingredients = RecipeAmountSerializer(
        many=True, source='ingredienttorecipe'
        )
    author = UserSerializer(read_only=True)
    is_favorite = serializers.BooleanField()
    is_in_shopping_cart = serializers.BooleanField()
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'name', 'image',
            'text', 'cooking_time', 'is_favorite',
            'is_in_shopping_cart'
              )


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""
    ingredients = RecipeAmountSerializer(
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField(max_length=None)
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'name', 'image',
            'text', 'cooking_time',)

    @staticmethod
    def bound_ingredients_recipe(ingredients, recipe):
        return [
            RecipeAmount(
                ingredient=data.pop('id'),
                amount=data.pop('amount'),
                recipe=recipe) for data in ingredients
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        RecipeAmount.objects.bulk_create(
            self.bound_ingredients_recipe(ingredients, recipe)
            )
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        RecipeAmount.objects.filter(recipe=instance).delete()
        instance.tags.set(validated_data.pop('tags'))
        ingredients = validated_data.pop('ingredients')
        RecipeAmount.objects.bulk_create(
            self.bound_ingredients_recipe(ingredients, instance)
            )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance, context={'request': self.context.get('request')}).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор полей избранных рецептов и корзины с покупками."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления в избранное."""
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        if user.favorite_recipes.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное!'
                )
        return data

    def to_representation(self, inctance):
        return RecipeShortSerializer(
            inctance.recipe,
            context={'requst': self.context.get('request')}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления в корзину покупок."""
    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")

    def validate(self, data):
        user = data['user']
        if user.shopping_carts.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже имеется в корзине покупок!'
                )
        return data

    def to_representation(self, inctance):
        return RecipeShortSerializer(
            inctance.recipe,
            context={'requst': self.context.get('request')}
        ).data


class SubsctiptionListSerializer(UserSerializer):
    """Сериализатор подписок."""
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("recipes_count", "recipes")
        read_only_fields = ("email", "username", "first_name", "last_name")

    def validate(self, data):
        author_id = self.context.get(
            "request").parser_context.get("kwargs").get("id")
        author = get_object_or_404(User, id=author_id)
        user = self.context.get("request").user
        if user.follower.filter(author=author_id).exists():
            raise ValidationError(
                detail="Вы уже подписаны на данного автора",
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail="Вы не можете подписаться на себя самого",
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
