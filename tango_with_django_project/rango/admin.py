from django.contrib import admin
from rango.models import Category, Page 
from rango.models import PageAdmin


# Add in this class to customise the Admin Interface
class CategoryAdmin(admin.ModelAdmin):
    # Update the registration to include this customised interface
    prepopulated_fields = {'slug':('name',)}


# Register your models here.
admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)

