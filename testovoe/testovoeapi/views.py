from django.shortcuts import render
from .models import Category, Product, Subcategory
# Create your views here.
from .serializers import ProductSerializer, CategorySerializer, SubcategorySerializer
from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import ValidationError
from .models import Cart
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class SubcategoryList(ListCreateAPIView):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Subcategory.objects.all()
        category_id = self.request.query_params.get('category', None)
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)
        return queryset

class ProductList(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        subcategory_id = self.request.query_params.get('subcategory', None)
        if subcategory_id is not None:
            queryset = queryset.filter(subcategory_id=subcategory_id)
        return queryset


class CategoryList(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination


class ProductDetail(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


# ...


@api_view(["POST"])
def add_product_to_cart(request):
    if request.method != "POST":
        return Response({"status": "error", "message": "Method Not Allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    user_id = request.data.get("user_id")
    product_id = request.data.get("product_id")
    quantity = request.data.get("quantity", 1)

    product = get_object_or_404(Product, id=product_id)

    try:
        # If the product already exists in the cart, increase the quantity
        cart_item = Cart.objects.get(user_id=user_id, product_id=product_id)
        cart_item.quantity += quantity
        cart_item.save()
    except Cart.DoesNotExist:
        # If the product is not in the cart, create a new cart item
        cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
        cart_item.save()

    return Response({"status": "success"})