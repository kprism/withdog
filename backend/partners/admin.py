from django.contrib import admin
from .models import Partner,PartnerCategory,PartnerBenefit
@admin.register(PartnerCategory)
class PartnerCategoryAdmin(admin.ModelAdmin): list_display=('name','code','sort_order')
@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display=('name','category','city','phone','is_affiliated','is_active')
    list_filter=('category','city','is_affiliated','is_active')
    search_fields=('name','address','phone')
admin.site.register(PartnerBenefit)
