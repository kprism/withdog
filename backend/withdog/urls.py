from pathlib import Path
from django.contrib import admin
from django.urls import include,path,re_path
from django.views.static import serve
ROOT=Path(__file__).resolve().parents[2]
urlpatterns=[path('admin/',admin.site.urls),path('api/',include('partners.urls')),re_path(r'^(?P<path>.*)$',serve,{'document_root':ROOT})]
