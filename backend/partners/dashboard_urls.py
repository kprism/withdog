from django.contrib.auth import views as auth_views
from django.urls import path
from . import dashboard_views as v
from . import website_views as w
from . import payment_views as p
app_name='operator_dashboard'
urlpatterns=[
 path('payments/settings/',p.payment_settings,name='payment_settings'),
 path('payments/settlements/',p.settlements,name='settlements'),
 path('website/chatbot/',w.chatbot_editor,name='chatbot_editor'),
 path('website/boards/<str:board_type>/',v.board_admin_list,name='board_admin_list'),
 path('website/boards/<str:board_type>/create/',v.board_admin_create,name='board_admin_create'),
 path('website/boards/<str:board_type>/<int:pk>/update/',v.board_admin_update,name='board_admin_update'),
 path('website/boards/<str:board_type>/<int:pk>/delete/',v.board_admin_delete,name='board_admin_delete'),
 path('website/boards/<str:board_type>/bulk-action/',v.board_admin_bulk_action,name='board_admin_bulk_action'),
 path('website/boards/<str:board_type>/categories/',v.board_category_admin,name='board_category_admin'),
 path('website/boards/<str:board_type>/categories/<int:pk>/update/',v.board_category_update,name='board_category_update'),
 path('website/boards/<str:board_type>/categories/<int:pk>/delete/',v.board_category_delete,name='board_category_delete'),
 path('website/breeds/',v.breed_page_editor,name='breed_page_editor'),
 path('website/breeds/create/',v.breed_page_create,name='breed_page_create'),
 path('website/breeds/database/create/',v.dogbreed_create,name='dogbreed_create'),
 path('website/breeds/database/<int:pk>/update/',v.dogbreed_update,name='dogbreed_update'),
 path('website/breeds/database/<int:pk>/delete/',v.dogbreed_delete,name='dogbreed_delete'),
 path('website/breeds/database/bulk-delete/',v.dogbreed_bulk_delete,name='dogbreed_bulk_delete'),
 path('website/breeds/<int:pk>/update/',v.breed_page_update,name='breed_page_update'),
 path('website/breeds/bulk-delete/',v.breed_page_bulk_delete,name='breed_page_bulk_delete'),
 path('website/partners/',v.partner_page_editor,name='partner_page_editor'),
 path('website/partners/category/add/',v.partner_category_create,name='partner_category_create'),
 path('website/partners/category/<int:pk>/update/',v.partner_category_update,name='partner_category_update'),
 path('website/partners/category/<int:pk>/delete/',v.partner_category_delete,name='partner_category_delete'),
 path('website/partners/<int:pk>/advertising/',v.partner_ad_update,name='partner_ad_update'),
 path('website/',w.site_settings,name='website_settings'),
 path('site-settings/',w.seo_site_settings,name='seo_site_settings'),
 path('website/about/',w.about_editor,name='about_editor'),
 path('login/',auth_views.LoginView.as_view(template_name='dashboard/login.html',redirect_authenticated_user=True),name='login'),path('logout/',auth_views.LogoutView.as_view(next_page='/dashboard/login/'),name='logout'),path('',v.dashboard_home,name='home'),
 path('partners/',v.partner_list,name='partners'),path('partners/new/',v.partner_edit,name='partner_new'),path('partners/<int:pk>/edit/',v.partner_edit,name='partner_edit'),path('partners/<int:pk>/delete/',v.partner_delete,name='partner_delete'),path('partners/upload/',v.partner_upload,name='partner_upload'),
 path('manage/<slug:section>/',v.manage_section,name='manage_section'),path('manage/<slug:section>/new/',v.section_edit,name='section_new'),path('manage/<slug:section>/<int:pk>/edit/',v.section_edit,name='section_edit'),path('manage/<slug:section>/<int:pk>/delete/',v.section_delete,name='section_delete'),
 path('members/new/',v.member_edit,name='member_new'),path('members/<int:pk>/edit/',v.member_edit,name='member_edit'),path('members/<int:pk>/withdraw/',v.member_withdraw,name='member_withdraw'),path('members/<int:pk>/delete/',v.member_delete,name='member_delete'),path('admins/new/',v.admin_edit,name='admin_new'),path('admins/<int:pk>/edit/',v.admin_edit,name='admin_edit'),
 path('content/<slug:kind>/',v.content_list,name='content_list'),path('content/<slug:kind>/new/',v.content_edit,name='content_new'),path('content/<slug:kind>/<int:pk>/edit/',v.content_edit,name='content_edit'),path('content/<slug:kind>/<int:pk>/delete/',v.content_delete,name='content_delete'),
 path('website/<slug:kind>/',w.media_list,name='website_media'),path('website/<slug:kind>/new/',w.media_edit,name='website_media_new'),path('website/<slug:kind>/<int:pk>/edit/',w.media_edit,name='website_media_edit'),path('website/<slug:kind>/<int:pk>/delete/',w.media_delete,name='website_media_delete'),
 path(
     'community/reports/',
     v.board_report_admin_list,
     name='board_report_admin_list'
 ),
 path(
     'community/reports/<int:pk>/',
     v.board_report_admin_detail,
     name='board_report_admin_detail'
 )
]
