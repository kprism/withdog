from django.urls import path
from . import views
urlpatterns=[path('partners/',views.partner_list),path('partners/import/',views.import_excel),path('partners/<int:pk>/coordinates/',views.save_coordinates),path('content/',views.content_feed)]
