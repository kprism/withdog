from django.urls import path
from . import dashboard_views

app_name = 'operator_dashboard'

urlpatterns = [
    path('', dashboard_views.dashboard_home, name='home'),
    path('partners/', dashboard_views.partner_list, name='partners'),
    path('partners/upload/', dashboard_views.partner_upload, name='partner_upload'),
]
