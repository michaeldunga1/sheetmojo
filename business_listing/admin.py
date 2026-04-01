from django.contrib import admin
from .models import BusinessDetails

@admin.register(BusinessDetails)
class BusinessDetailsAdmin(admin.ModelAdmin):
	list_display = ('business_name', 'category', 'country', 'city', 'created_on', 'created_by')
