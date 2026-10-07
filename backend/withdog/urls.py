from partners import website_views
from partners import views as partner_views
from partners import mypage_views
from pathlib import Path

from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from django.conf import settings
from django.http import HttpResponse, FileResponse, Http404
from django.utils.html import escape
from django.views.decorators.cache import never_cache

ROOT = Path(__file__).resolve().parents[2]


@never_cache
def public_home(request):
    """Serve the live homepage without allowing stale HTML to mask deployed UI fixes."""
    from partners.models import SiteSetting
    s=SiteSetting.get_solo()
    import re
    import json
    html=(ROOT / 'index.html').read_text(encoding='utf-8')
    html=re.sub(r'<title[^>]*>.*?</title>', '', html, count=1, flags=re.I|re.S)
    html=re.sub(r"""<meta\s+name=["']description["'][^>]*>""", '', html, count=1, flags=re.I)
    title=escape(s.site_name or '경상남도 반려견 협회')
    desc=escape(s.meta_description or s.site_subtitle or '')
    canonical=escape(s.canonical_url or request.build_absolute_uri('/'))
    tags=[
        f'<title>{title}</title>',
        f'<meta name="description" content="{desc}">',
        f'<link rel="canonical" href="{canonical}">',
        f'<meta property="og:title" content="{escape(s.og_title or s.site_name or "")}">',
        f'<meta property="og:description" content="{escape(s.og_description or s.meta_description or s.site_subtitle or "")}">',
        f'<meta property="og:url" content="{canonical}">',
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="'+title+'">',
        '<meta name="robots" content="index,follow,max-image-preview:large">',
        '<meta name="twitter:card" content="summary_large_image">',
    ]
    if s.meta_keywords: tags.append(f'<meta name="keywords" content="{escape(s.meta_keywords)}">')
    if s.naver_site_verification: tags.append(f'<meta name="naver-site-verification" content="{escape(s.naver_site_verification)}">')
    if s.google_site_verification: tags.append(f'<meta name="google-site-verification" content="{escape(s.google_site_verification)}">')
    if s.og_image_url: tags.append(f'<meta property="og:image" content="{escape(s.og_image_url)}">')
    organization={'@context':'https://schema.org','@type':'Organization','name':str(s.site_name or '경상남도 반려견 협회'),'url':str(s.canonical_url or 'https://thepetkorea.co.kr/')}
    tags.append('<script type="application/ld+json">'+json.dumps(organization,ensure_ascii=False).replace('</','<\\/')+'</script>')
    if s.favicon:
        tags.append('<link rel="icon" href="/favicon.ico">')
        tags.append('<link rel="shortcut icon" href="/favicon.ico">')
    seo='\n'.join(tags)
    pos=html.lower().find('</head>')
    if pos >= 0: html=html[:pos]+seo+'\n'+html[pos:]
    response = HttpResponse(html, content_type='text/html; charset=utf-8')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response



def favicon(request):
    """Stable root favicon URL backed by the favicon selected in Site Settings."""
    from partners.models import SiteSetting
    s = SiteSetting.get_solo()
    if not s.favicon:
        raise Http404('favicon not configured')
    try:
        handle = s.favicon.open('rb')
    except (ValueError, FileNotFoundError):
        raise Http404('favicon not found')
    name = (s.favicon.name or '').lower()
    if name.endswith('.png'):
        content_type = 'image/png'
    elif name.endswith(('.jpg', '.jpeg')):
        content_type = 'image/jpeg'
    elif name.endswith('.webp'):
        content_type = 'image/webp'
    elif name.endswith('.svg'):
        content_type = 'image/svg+xml'
    else:
        content_type = 'image/x-icon'
    response = FileResponse(handle, content_type=content_type)
    response['Cache-Control'] = 'public, max-age=86400'
    return response


def sitemap_xml(request):
    """Standards-compliant public sitemap for Google and Naver crawlers."""
    from xml.etree.ElementTree import Element, SubElement, tostring
    from django.utils import timezone
    from partners.models import BoardPost, DogBreed, SiteSetting

    s = SiteSetting.get_solo()
    base = (s.canonical_url or 'https://thepetkorea.co.kr/').strip().rstrip('/')
    if not base.startswith('https://'):
        base = 'https://thepetkorea.co.kr'

    paths = [
        '/', '/about.html', '/benefits.html', '/partners.html',
        '/board.html', '/community.html', '/breeds/',
    ]
    static_lastmod = timezone.localdate().isoformat()
    entries = [(p, static_lastmod) for p in paths]
    entries += [
        (f'/board/{x.pk}/', x.updated_at.date().isoformat())
        for x in BoardPost.objects.filter(board_type='notice', is_published=True, is_hidden=False).only('pk', 'updated_at')
    ]
    entries += [
        (f'/breeds/{x.slug}/', x.updated_at.date().isoformat())
        for x in DogBreed.objects.filter(is_published=True).only('slug', 'updated_at')
    ]

    urlset = Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    seen = set()
    for path_value, lastmod in entries:
        loc_value = base + path_value
        if loc_value in seen:
            continue
        seen.add(loc_value)
        url = SubElement(urlset, 'url')
        SubElement(url, 'loc').text = loc_value
        SubElement(url, 'lastmod').text = lastmod

    body = b'<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(urlset, encoding='utf-8')
    response = HttpResponse(body, content_type='application/xml; charset=utf-8')
    response['X-Robots-Tag'] = 'noindex'
    response['Cache-Control'] = 'public, max-age=300'
    return response

def robots_txt(request):
    from partners.models import SiteSetting
    s = SiteSetting.get_solo()
    base = (s.canonical_url or 'https://thepetkorea.co.kr/').strip().rstrip('/')
    if not base.startswith('https://'):
        base = 'https://thepetkorea.co.kr'
    body = (
        'User-agent: *\n'
        'Allow: /\n'
        'Disallow: /dashboard/\n'
        'Disallow: /admin/\n'
        f'Sitemap: {base}/sitemap.xml\n'
    )
    return HttpResponse(body, content_type='text/plain; charset=utf-8')

urlpatterns = [
    path('favicon.ico', favicon, name='favicon'),
    path('sitemap.xml', sitemap_xml, name='sitemap_xml'),
    path('robots.txt', robots_txt, name='robots_txt'),
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

    # collectstatic으로 수집한 정적 파일. 운영 nginx 설정과 무관하게
    # Django가 /static/ 요청을 확실히 처리하도록 명시한다.
    re_path(
        r'^static/(?P<path>.*)$',
        serve,
        {'document_root': settings.STATIC_ROOT},
    ),

    # 업로드 파일
    re_path(
        r'^media/(?P<path>.*)$',
        serve,
        {'document_root': settings.MEDIA_ROOT},
    ),

    # 홈페이지 첫 화면: / 와 /index.html 모두 최신 HTML을 즉시 제공
    path('', public_home, name='home'),
    path('index.html', public_home, name='home_index'),

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
