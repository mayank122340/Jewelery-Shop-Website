from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Sirf wahi fields rakho jo naye models.py mein hain
    list_display = ('name', 'metal_type', 'category', 'net_weight', 'huid')
    search_fields = ('name', 'huid', 'sub_category')
    list_filter = ('metal_type', 'category')
    prepopulated_fields = {'slug': ('name',)}