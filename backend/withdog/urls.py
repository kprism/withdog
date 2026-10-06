from partners import website_views
from partners import views as partner_views
from partners import mypage_views
from pathlib import Path

from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from django.conf import settings

ROOT = Path(__file__).resolve().parents[2]

urlpatterns = [
    path(
        'api/intro-news/',
        website_views.public_intro_news_api,
        name='public_intro_news_api',
    ),

    path(
        'api/chatbot/config/',
        website_views.public_chatbot_config,
        name='public_chatbot_config',
    ),
    path(
        'api/chatbot/message/',
        website_views.public_chatbot_message,
        name='public_chatbot_message',
    ),
    path(
        'community/<int:pk>/comment/',
        website_views.public_community_comment_create,
        name='public_community_comment_create',
    ),
    path(
        'community/<int:pk>/comment/<int:comment_pk>/delete/',
        website_views.public_community_comment_delete,
        name='public_community_comment_delete',
    ),
    path(
        'community/<int:pk>/like/',
        website_views.public_community_like_toggle,
        name='public_community_like_toggle',
    ),
    path(
        'community/<int:pk>/report/',
        website_views.public_community_report,
        name='public_community_report',
    ),

    path('api/about-page/', website_views.about_data, name='about_data'),
    path('api/site-settings/', partner_views.site_settings_api, name='site_settings_api'),

    # 일반회원 마이페이지
    path('mypage/', mypage_views.mypage_home, name='public_mypage'),
    path(
        'mypage/membership-card/',
        mypage_views.membership_card,
        name='public_membership_card',
    ),

    # 운영자 대시보드
    path('dashboard/', include('partners.dashboard_urls')),

    # Django 기본 관리자
    path('admin/', admin.site.urls),

    # API
    path('api/', include('partners.urls')),

    # 업로드 파일
    re_path(
        r'^media/(?P<path>.*)$',
        serve,
        {'document_root': settings.MEDIA_ROOT},
    ),

    # 홈페이지 첫 화면
    path(
        '',
        serve,
        {
            'document_root': ROOT,
            'path': 'index.html',
        },
        name='home',
    ),

    # 전 세계 견종 데이터베이스
    path(
        'breeds/',
        website_views.public_breed_list,
        name='public_breed_list',
    ),
    path(
        'breeds/<slug:slug>/',
        website_views.public_breed_detail,
        name='public_breed_detail',
    ),

    # 공개 공지사항 상세
    path(
        'board/<int:pk>/',
        website_views.public_notice_detail,
        name='public_board_detail',
    ),

    # 공개 공지사항
    path(
        'board.html',
        website_views.public_notice_board,
        name='public_notice_board',
    ),

    # 자유게시판
    path(
        'community.html',
        website_views.public_community_list,
        name='public_community_list',
    ),
    path(
        'community/write/',
        website_views.public_community_create,
        name='public_community_create',
    ),
    path(
        'community/<int:pk>/',
        website_views.public_community_detail,
        name='public_community_detail',
    ),
    path(
        'community/<int:pk>/edit/',
        website_views.public_community_update,
        name='public_community_update',
    ),
    path(
        'community/<int:pk>/delete/',
        website_views.public_community_delete,
        name='public_community_delete',
    ),

    # 기존 정적 홈페이지 파일
    re_path(
        r'^(?P<path>.*)$',
        serve,
        {'document_root': ROOT},
    ),
]
