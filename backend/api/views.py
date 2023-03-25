from django.contrib.auth import get_user_model
from django.db.models import Subquery, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework import viewsets, status

from recipes.models import (
    Tag, Ingredient, Recipe, Favorite, ShoppingCart, RecipeAmount)
from users.models import Follow
from .filters import IngredientFilter, RecipeFilter
from .serializers import (
    UserSerializer, TagSerializer, IngredientSerializer,
    RecipeReadSerializer, RecipeWriteSerializer, FavoriteSerializer,
    ShoppingCartSerializer, SubsctiptionListSerializer)
from .pagination import CustomPagination
from .permissions import IsAuthorPermission
from .utilities.download_pdf import make_pdf


User = get_user_model()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = (IngredientFilter, )
    search_fields = ('^name', )
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeReadSerializer
    permission_classes = (IsAuthorPermission,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    queryset = Recipe.objects.all()
    filter_fields = ('is_favorite', 'is_in_shopping_cart')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        else:
            return RecipeWriteSerializer

    @action(detail=False, methods=["GET"])
    def download_shopping_cart(self, request):
        recipes_in_cart = ShoppingCart.objects.filter(user=request.user)
        ingredients = RecipeAmount.objects.filter(
            recipe__in=Subquery(recipes_in_cart.values("pk"))
            ).order_by("ingredient__name").values(
            "ingredient__name", "ingredient__measurement_unit"
            ).annotate(amount=Sum("amount"))
        return FileResponse(
            make_pdf(ingredients),
            as_attachment=True,
            filename='shopping_cart.pdf')

    @action(
            detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated],
            name='Add to Favorite'
            )
    def favorite(self, request, pk):
        context = {'request': request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = FavoriteSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def destroy_favorite(self, request, pk):
        get_object_or_404(
            Favorite, user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
            detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated],
            name='Add to ShoppingCart'
            )
    def shopping_cart(self, request, pk):
        context = {'request': request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = ShoppingCartSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def destroy_shopping_cart(self, request, pk):
        get_object_or_404(
            ShoppingCart,
            user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)).delete()
        return Response(status.HTTP_204_NO_CONTENT)


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated],
        )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            serializer = SubsctiptionListSerializer(
                author, data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            get_object_or_404(
                Follow, user=user, author=author
                ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubsctiptionListSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)
