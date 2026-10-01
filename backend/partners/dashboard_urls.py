from django.contrib.auth import views as auth_views
from django.urls import path
from . import dashboard_views as v
from . import website_views as w
app_name='operator_dashboard'
urlpatterns=[
 path('login/',auth_views.LoginView.as_view(template_name='dashboard/login.html',redirect_authenticated_user=True),name='login'),path('logout/',auth_views.LogoutView.as_view(next_page='/dashboard/login/'),name='logout'),path('',v.dashboard_home,name='home'),
 path('partners/',v.partner_list,name='partners'),path('partners/new/',v.partner_edit,name='partner_new'),path('partners/<int:pk>/edit/',v.partner_edit,name='partner_edit'),path('partners/<int:pk>/delete/',v.partner_delete,name='partner_delete'),path('partners/upload/',v.partner_upload,name='partner_upload'),
 path('manage/<slug:section>/',v.manage_section,name='manage_section'),path('manage/<slug:section>/new/',v.section_edit,name='section_new'),path('manage/<slug:section>/<int:pk>/edit/',v.section_edit,name='section_edit'),path('manage/<slug:section>/<int:pk>/delete/',v.section_delete,name='section_delete'),
 path('members/new/',v.member_edit,name='member_new'),path('members/<int:pk>/edit/',v.member_edit,name='member_edit'),path('members/<int:pk>/withdraw/',v.member_withdraw,name='member_withdraw'),path('admins/new/',v.admin_edit,name='admin_new'),path('admins/<int:pk>/edit/',v.admin_edit,name='admin_edit'),
 path('content/<slug:kind>/',v.content_list,name='content_list'),path('content/<slug:kind>/new/',v.content_edit,name='content_new'),path('content/<slug:kind>/<int:pk>/edit/',v.content_edit,name='content_edit'),path('content/<slug:kind>/<int:pk>/delete/',v.content_delete,name='content_delete'),
 path('website/<slug:kind>/',w.media_list,name='website_media'),path('website/<slug:kind>/new/',w.media_edit,name='website_media_new'),path('website/<slug:kind>/<int:pk>/edit/',w.media_edit,name='website_media_edit'),path('website/<slug:kind>/<int:pk>/delete/',w.media_delete,name='website_media_delete')]
