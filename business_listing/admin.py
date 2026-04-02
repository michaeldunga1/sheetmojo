from django.contrib import admin
from .models import BusinessDetails, Product

@admin.register(BusinessDetails)
class BusinessDetailsAdmin(admin.ModelAdmin):
	list_display = ('business_name', 'category', 'country', 'city', 'created_on', 'created_by')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ('product_name', 'business', 'product_category', 'price', 'currency', 'terms_of_sale', 'posted_on')
	list_filter = ('currency', 'terms_of_sale', 'product_category', 'posted_on')
	search_fields = ('product_name', 'product_category', 'business__business_name')
