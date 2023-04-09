from rest_framework import serializers
from .models import Category, Product, Subcategory


class CategorySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    id = serializers.IntegerField()
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    subcategory = serializers.StringRelatedField()
    description = serializers.CharField()
    image = serializers.ImageField()
    subcategory_id = serializers.IntegerField(source='subcategory.id', allow_null=True)
    class Meta:
        model = Product
        fields = '__all__'


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'category']