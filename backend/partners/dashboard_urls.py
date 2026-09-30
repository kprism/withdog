from django.contrib.auth import views as auth_views
from django.urls import path
from . import dashboard_views

app_name = 'operator_dashboard'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='dashboard/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/dashboard/login/'), name='logout'),
    path('', dashboard_views.dashboard_home, name='home'),
    path('partners/', dashboard_views.partner_list, name='partners'),
    path('partners/upload/', dashboard_views.partner_upload, name='partner_upload'),
    path('manage/<slug:section>/', dashboard_views.manage_section, name='manage'),
]
