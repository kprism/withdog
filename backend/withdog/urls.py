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


def _render_public_shell(request, html):
    """Render one canonical authenticated-aware header/footer on every public HTML page."""
    import re
    from django.template.loader import render_to_string
    header = render_to_string('website/includes/public_header.html', request=request)
    footer = render_to_string('website/includes/public_footer.html', request=request)

    # Strip legacy floating chatbot / scroll controls and duplicate chatbot scripts
    # from static HTML before injecting the canonical footer. This prevents the
    # old bot from covering the admin-configured video and removes duplicate IDs.
    html = re.sub(
        r'<div\s+class=["\']bot-float["\'][^>]*>\s*<div\s+class=["\']bot-tip["\'][^>]*>.*?</div>\s*<button[^>]*id=["\']botButton["\'][^>]*>.*?</button>\s*</div>',
        '',
        html,
        flags=re.I | re.S,
    )
    html = re.sub(
        r'<div\s+class=["\']bot["\'][^>]*>\s*<span[^>]*>.*?</span>\s*<button[^>]*>.*?</button>\s*</div>',
        '',
        html,
        flags=re.I | re.S,
    )
    html = re.sub(
        r'<button\s+class=["\'](?:to-top|top)["\'][^>]*>.*?</button>',
        '',
        html,
        flags=re.I | re.S,
    )
    html = re.sub(
        r'<script[^>]+src=["\'][^"\']*assets/js/chatbot\.js[^"\']*["\'][^>]*></script>',
        '',
        html,
        flags=re.I | re.S,
    )

    html = re.sub(r'<header class="site-header".*?</header>', header, html, count=1, flags=re.I | re.S)
    html = re.sub(r'<footer class="footer".*?</footer>', footer, html, count=1, flags=re.I | re.S)
    return html



def _render_live_home_hero(request):
    """Render only the currently published hero media on the initial HTML response."""
    import re
    from partners.models import ContentItem, SiteSetting

    setting = SiteSetting.get_solo()
    slides = list(
        ContentItem.objects
        .filter(kind='hero', is_published=True)
        .order_by('sort_order', 'pk')
    )

    def media_markup(item, active):
        classes = 'hero-slide cms-hero-slide' + (' active' if active else '')
        common = (
            f'class="{classes}" '
            f'data-server-hero="1" '
            f'data-cms-id="{item.pk}"'
        )

        image_url = ''
        try:
            image_url = item.image.url if item.image else (item.image_url or '')
        except (ValueError, FileNotFoundError):
            image_url = item.image_url or ''

        video_url = ''
        try:
            video_url = item.video.url if item.video else ''
        except (ValueError, FileNotFoundError):
            video_url = ''

        if item.media_type == 'video_file' and video_url:
            return (
                f'<div {common}>'
                f'<video class="hero-media" src="{escape(video_url)}" '
                'autoplay muted loop playsinline preload="auto"></video>'
                '</div>'
            )

        if item.media_type == 'video_url' and item.video_url:
            source = str(item.video_url).strip()
            match = re.search(
                r'(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/))([^?&/]+)',
                source,
                re.I,
            )
            if match:
                media_id = escape(match.group(1))
                src = (
                    f'https://www.youtube.com/embed/{media_id}'
                    f'?autoplay=1&mute=1&loop=1&playlist={media_id}'
                    '&controls=0&playsinline=1'
                )
                return (
                    f'<div {common}>'
                    f'<iframe class="hero-media" src="{src}" '
                    'allow="autoplay; encrypted-media; picture-in-picture" '
                    'allowfullscreen></iframe>'
                    '</div>'
                )
            return (
                f'<div {common}>'
                f'<video class="hero-media" src="{escape(source)}" '
                'autoplay muted loop playsinline preload="auto"></video>'
                '</div>'
            )

        if image_url:
            safe_url = escape(image_url)
            return (
                f'<div {common} '
                f'style="--bg:url(&quot;{safe_url}&quot;)"></div>'
            )

        return f'<div {common}></div>'

    slide_markup = ''.join(
        media_markup(item, index == 0)
        for index, item in enumerate(slides)
    )

    first = slides[0] if slides else None

    if first:
        eyebrow = escape(first.hero_eyebrow or '')
        title_lines = str(first.hero_title or '').split('\n')
        title = '<br>'.join(escape(line) for line in title_lines)
        meta1 = escape(first.hero_meta1 or '')
        meta2 = escape(first.hero_meta2 or '')
        meta1_size = max(10, min(40, int(first.hero_meta1_font_size or 16)))
        meta2_size = max(10, min(40, int(first.hero_meta2_font_size or 16)))

        buttons = []
        if first.hero_button1_text:
            buttons.append(
                '<a class="btn btn-red" href="'
                + escape(first.hero_button1_link or '#')
                + '">'
                + escape(first.hero_button1_text)
                + '</a>'
            )
        if first.hero_button2_text:
            buttons.append(
                '<a class="btn btn-glass" href="'
                + escape(first.hero_button2_link or '#')
                + '">'
                + escape(first.hero_button2_text)
                + '</a>'
            )

        content = (
            '<div class="hero-content" data-server-hero-content="1">'
            f'<p class="eyebrow">{eyebrow}</p>'
            f'<h1>{title}</h1>'
            f'<p class="hero-meta" style="font-size:{meta1_size}px">{meta1}</p>'
            f'<p class="hero-meta" style="font-size:{meta2_size}px">{meta2}</p>'
            '<div class="hero-buttons">'
            + ''.join(buttons)
            + '</div></div>'
        )
    else:
        content = '<div class="hero-content" data-server-hero-content="1"></div>'

    return (
        '<section class="hero" data-live-hero="1" '
        f'data-stage-width="{setting.intro_stage_width}" '
        f'data-stage-height="{setting.intro_stage_height}">'
        + slide_markup
        + '<div class="hero-shade"></div>'
        + content
        + '</section>'
    )


@never_cache
def public_home(request):
    """Serve the live homepage without allowing stale HTML to mask deployed UI fixes."""
    from partners.models import SiteSetting
    s=SiteSetting.get_solo()
    import re
    import json
    html=(ROOT / 'index.html').read_text(encoding='utf-8')
    html=_render_public_shell(request, html)

    # Replace the legacy static hero before the response leaves Django.
    # This prevents deleted/old images from flashing before cms.js loads.
    html=re.sub(
        r'<section class="hero"[^>]*>.*?</section>',
        _render_live_home_hero(request),
        html,
        count=1,
        flags=re.I|re.S,
    )

    # Dog Life homepage feed.
    # Default is popularity; users can switch to latest without leaving the homepage.
    from django.db.models import Count, ExpressionWrapper, F, IntegerField
    from django.template.loader import render_to_string
    from partners.models import BoardPost

    doglife_sort=(request.GET.get('doglife_sort') or 'popular').strip().lower()
    if doglife_sort not in {'popular','latest'}:
        doglife_sort='popular'

    doglife_base=(
        BoardPost.objects
        .filter(board_type='doglife',is_published=True,is_hidden=False)
        .select_related('category','author')
        .prefetch_related('attachments')
        .annotate(like_count=Count('likes',distinct=True))
        .annotate(
            popularity_score=ExpressionWrapper(
                F('view_count') + F('like_count') * 12,
                output_field=IntegerField(),
            )
        )
    )
    popular_qs=doglife_base.order_by(
        '-popularity_score','-view_count','-published_at','-created_at'
    )
    if doglife_sort == 'latest':
        selected_qs=doglife_base.order_by('-published_at','-created_at')
    else:
        selected_qs=popular_qs

    doglife_posts=list(selected_qs[:15])
    home_featured_posts=doglife_posts[:5]
    home_feed_posts=doglife_posts[5:15]
    home_rank_posts=list(popular_qs[:5])

    feed=render_to_string(
        'website/includes/doglife_home_feed.html',
        {
            'doglife_sort':doglife_sort,
            'home_featured_posts':home_featured_posts,
            'home_feed_posts':home_feed_posts,
            'home_rank_posts':home_rank_posts,
        },
        request=request,
    )
    html=re.sub(
        r'<section class="web-magazine[^"]*" id="doglife">.*?</section>',
        feed,
        html,
        count=1,
        flags=re.I|re.S,
    )

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



@never_cache
def public_partner_join(request):
    """Serve the homepage while opening the partner registration tab directly."""
    response = public_home(request)
    html = response.content.decode('utf-8', 'replace')

    # This dedicated deep link lives under /join/, so force all relative assets
    # and links in the static homepage to resolve from the site root.
    if '<base href="/">' not in html:
        html = html.replace('<head>', '<head><base href="/">', 1)

    direct = HttpResponse(
        html,
        content_type='text/html; charset=utf-8',
        status=response.status_code,
    )
    direct['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    direct['Pragma'] = 'no-cache'
    direct['Expires'] = '0'
    return direct


def public_static_page(request, filename):
    """Serve legacy public HTML through an explicit route and force the intro header/footer markup."""
    import re
    allowed={'about.html','benefits.html','partners.html','breeds.html','join.html'}
    if filename not in allowed:
        raise Http404('page not found')
    page=(ROOT / filename).read_text(encoding='utf-8')
    page=_render_public_shell(request, page)
    page=re.sub(
        r'''href=["'][^"']*assets/css/style\.css(?:\?[^"']*)?["']''',
        'href="/assets/css/style.css?v=20261020-split-hub-v9"',
        page,
        count=1,
        flags=re.I,
    )
    if 'assets/css/style.css' not in page:
        page=page.replace('</head>','<link rel="stylesheet" href="/assets/css/style.css?v=20261020-split-hub-v9"></head>',1)
    response=HttpResponse(page,content_type='text/html; charset=utf-8')
    response['Cache-Control']='no-store, no-cache, must-revalidate, max-age=0'
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
        '/board.html', '/community.html', '/doglife/', '/breeds/',
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
    from partners.models import BoardPost
    entries += [
        (f'/doglife/{x.pk}/', x.updated_at.date().isoformat())
        for x in BoardPost.objects.filter(board_type='doglife', is_published=True, is_hidden=False).only('pk', 'updated_at')
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

    path('api/policies/', website_views.public_policy_data, name='public_policy_data'),

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

    # 제휴업체 전용 회원가입 딥링크
    path('join/partner', public_partner_join, name='public_partner_join'),
    path('join/partner/', public_partner_join, name='public_partner_join_slash'),

    # 홈페이지 첫 화면: / 와 /index.html 모두 최신 HTML을 즉시 제공
    path('', public_home, name='home'),
    path('index.html', public_home, name='home_index'),

    # 견생(Dog Life)
    path('doglife/', website_views.public_doglife_list, name='public_doglife_list'),
    path('doglife/write/', website_views.public_doglife_create, name='public_doglife_create'),
    path('doglife/<int:pk>/', website_views.public_doglife_detail, name='public_doglife_detail'),
    path('doglife/<int:pk>/edit/', website_views.public_doglife_update, name='public_doglife_update'),
    path('doglife/<int:pk>/delete/', website_views.public_doglife_delete, name='public_doglife_delete'),
    path('doglife/<int:pk>/like/', website_views.public_doglife_like_toggle, name='public_doglife_like_toggle'),

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

    # 공개 정적 페이지도 catch-all에 맡기지 않고 명시적으로 라우팅한다.
    # 응답 시 인트로(index.html)의 헤더/푸터를 그대로 주입한다.
    path('about.html', public_static_page, {'filename':'about.html'}, name='public_about'),
    path('benefits.html', public_static_page, {'filename':'benefits.html'}, name='public_benefits'),
    path('partners.html', public_static_page, {'filename':'partners.html'}, name='public_partners'),
    path('breeds.html', public_static_page, {'filename':'breeds.html'}, name='public_breeds_legacy'),
    path('join.html', public_static_page, {'filename':'join.html'}, name='public_join'),

    # 기존 정적 홈페이지 파일
    re_path(
        r'^(?P<path>.*)$',
        serve,
        {'document_root': ROOT},
    ),
]
