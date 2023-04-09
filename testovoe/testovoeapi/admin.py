from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Product, Subcategory, Order
class CategoryAdmin(admin.ModelAdmin):
    list_filter = ['name']
    actions = ['delete_selected']

class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    actions = ['delete_selected']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product)
admin.site.register(Subcategory, SubcategoryAdmin)
admin.site.register(Order)