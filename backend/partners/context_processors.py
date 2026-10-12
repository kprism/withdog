from django.db.models import Q
from django.utils import timezone

from .models import Advertisement, SiteSetting


def _public_page_key(path):
    path = str(path or '/').split('?', 1)[0]
    if path in ('/', '/index.html'):
        return 'home'
    if path.startswith('/about'):
        return 'about'
    if path.startswith('/benefits'):
        return 'benefits'
    if path.startswith('/partners'):
        return 'partners'
    if path.startswith('/doglife'):
        return 'doglife'
    if path.startswith('/board'):
        return 'board'
    if path.startswith('/community'):
        return 'community'
    if path.startswith('/breeds'):
        return 'breeds'
    if path.startswith('/mypage'):
        return 'mypage'
    return 'all'


def public_site(request):
    """Site-wide branding and page-aware advertising for public pages."""
    setting = SiteSetting.get_solo()
    logo_url = ""
    try:
        if setting.logo and setting.logo.name and setting.logo.storage.exists(setting.logo.name):
            logo_url = setting.logo.url
    except (OSError, ValueError):
        logo_url = ""

    logo_video_url = ""
    try:
        if setting.logo_video and setting.logo_video.name and setting.logo_video.storage.exists(setting.logo_video.name):
            logo_video_url = setting.logo_video.url
    except (OSError, ValueError):
        logo_video_url = ""

    page_key = _public_page_key(request.path)
    ad_slots = {
        'right': [],
        'section_top': [],
        'section_middle': [],
        'section_bottom': [],
        'popup': [],
        'has_any': False,
        'reserve_right': page_key in {
            'about',
            'benefits',
            'partners',
            'doglife',
            'board',
            'community',
            'breeds',
        },
    }

    if not request.path.startswith('/dashboard/'):
        today = timezone.localdate()
        ads = (
            Advertisement.objects
            .filter(is_active=True, start_date__lte=today, end_date__gte=today)
            .filter(Q(target_page='all') | Q(target_page=page_key))
            .order_by('sort_order', '-created_at')
        )
        for ad in ads:
            ad_slots.setdefault(ad.placement, []).append(ad)
        ad_slots['has_any'] = any(ad_slots[key] for key in ('right', 'section_top', 'section_middle', 'section_bottom', 'popup'))

    return {
        'public_site': setting,
        'public_site_logo_url': logo_url,
        'public_site_logo_video_url': logo_video_url,
        'public_page_key': page_key,
        'public_ads': ad_slots,
    }
