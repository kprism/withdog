import hashlib
import ipaddress
import re
from datetime import timedelta
from urllib.parse import parse_qs, urlparse

from django.utils import timezone


BOT_PATTERN = re.compile(
    r'(bot|crawler|spider|slurp|bingpreview|googlebot|naverbot|'
    r'daumoa|yeti|yandex|facebookexternalhit|twitterbot|kakaotalk)',
    re.I,
)

EXCLUDED_PREFIXES = (
    '/dashboard/',
    '/admin/',
    '/api/',
    '/static/',
    '/media/',
)

EXCLUDED_PATHS = {
    '/favicon.ico',
    '/robots.txt',
    '/sitemap.xml',
}

SEARCH_ENGINES = (
    ('naver.', '네이버', ('query', 'q', 'keyword')),
    ('google.', '구글', ('q',)),
    ('daum.net', '다음', ('q', 'query')),
    ('bing.com', '빙', ('q',)),
    ('yahoo.', '야후', ('p', 'q')),
    ('zum.com', '줌', ('query', 'q')),
)

SOCIAL_HOSTS = (
    ('instagram.com', 'Instagram'),
    ('facebook.com', 'Facebook'),
    ('m.facebook.com', 'Facebook'),
    ('youtube.com', 'YouTube'),
    ('youtu.be', 'YouTube'),
    ('kakao.com', 'Kakao'),
    ('pf.kakao.com', 'Kakao Channel'),
    ('t.co', 'X'),
    ('twitter.com', 'X'),
    ('x.com', 'X'),
    ('blog.naver.com', 'Naver Blog'),
)


def get_client_ip(request):
    candidates = []

    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        candidates.extend(
            item.strip()
            for item in forwarded.split(',')
            if item.strip()
        )

    real_ip = request.META.get('HTTP_X_REAL_IP', '').strip()
    if real_ip:
        candidates.append(real_ip)

    remote = request.META.get('REMOTE_ADDR', '').strip()
    if remote:
        candidates.append(remote)

    for value in candidates:
        try:
            return ipaddress.ip_address(value).compressed
        except ValueError:
            continue

    return ''


def is_public_ip(value):
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return False

    return not (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_multicast
        or address.is_reserved
        or address.is_unspecified
    )



def location_from_request_headers(request):
    """
    Read approximate geo metadata only when the hosting proxy/CDN supplies it.
    No visitor IP is sent to any third-party lookup API.
    """
    from urllib.parse import unquote

    country = (
        request.META.get('HTTP_CF_IPCOUNTRY')
        or request.META.get('HTTP_CLOUDFRONT_VIEWER_COUNTRY')
        or request.META.get('HTTP_X_APPENGINE_COUNTRY')
        or request.META.get('HTTP_X_GEO_COUNTRY')
        or ''
    ).strip()

    region = (
        request.META.get('HTTP_CLOUDFRONT_VIEWER_COUNTRY_REGION_NAME')
        or request.META.get('HTTP_CF_REGION')
        or request.META.get('HTTP_X_APPENGINE_REGION')
        or request.META.get('HTTP_X_GEO_REGION')
        or ''
    ).strip()

    city = (
        request.META.get('HTTP_CLOUDFRONT_VIEWER_CITY')
        or request.META.get('HTTP_CF_IPCITY')
        or request.META.get('HTTP_X_APPENGINE_CITY')
        or request.META.get('HTTP_X_GEO_CITY')
        or ''
    ).strip()

    city = unquote(city)
    region = unquote(region)

    if not any((country, region, city)):
        return {}

    return {
        'country_code': country[:8],
        'country': country[:100],
        'region': region[:120],
        'city': city[:120],
        'geo_resolved': True,
        'geo_checked_at': timezone.now(),
    }


def _host_without_port(value):
    value = str(value or '').strip().lower()
    if value.startswith('['):
        return value
    return value.split(':', 1)[0]


def classify_traffic(request):
    referrer = (request.META.get('HTTP_REFERER') or '').strip()
    current_host = _host_without_port(request.get_host())

    utm_source = (request.GET.get('utm_source') or '').strip()
    utm_term = (
        request.GET.get('utm_term')
        or request.GET.get('keyword')
        or ''
    ).strip()

    if utm_source:
        return {
            'referrer': referrer,
            'referrer_host': '',
            'source_type': 'campaign',
            'source_name': utm_source[:80],
            'keyword': utm_term[:255],
        }

    if not referrer:
        return {
            'referrer': '',
            'referrer_host': '',
            'source_type': 'direct',
            'source_name': '직접 방문',
            'keyword': '',
        }

    try:
        parsed = urlparse(referrer)
    except ValueError:
        parsed = None

    host = _host_without_port(
        parsed.netloc
        if parsed
        else ''
    )

    if not host:
        return {
            'referrer': referrer[:2000],
            'referrer_host': '',
            'source_type': 'referral',
            'source_name': '외부 링크',
            'keyword': '',
        }

    if host == current_host or host.endswith('.' + current_host):
        return {
            'referrer': referrer[:2000],
            'referrer_host': host[:255],
            'source_type': 'internal',
            'source_name': '내부 이동',
            'keyword': '',
        }

    params = parse_qs(parsed.query) if parsed else {}

    for host_fragment, label, keys in SEARCH_ENGINES:
        if host_fragment in host:
            keyword = ''
            for key in keys:
                values = params.get(key) or []
                if values and values[0]:
                    keyword = str(values[0]).strip()
                    break

            return {
                'referrer': referrer[:2000],
                'referrer_host': host[:255],
                'source_type': 'search',
                'source_name': label,
                'keyword': keyword[:255],
            }

    for host_fragment, label in SOCIAL_HOSTS:
        if host_fragment in host:
            return {
                'referrer': referrer[:2000],
                'referrer_host': host[:255],
                'source_type': 'social',
                'source_name': label,
                'keyword': '',
            }

    return {
        'referrer': referrer[:2000],
        'referrer_host': host[:255],
        'source_type': 'referral',
        'source_name': host[:80],
        'keyword': '',
    }


class TrafficAnalyticsMiddleware:
    """
    Records one entry session per visitor fingerprint every 30 minutes.

    Location lookup is deliberately NOT performed here, so public page speed
    never depends on a third-party geo service. The admin analytics page
    resolves recent unknown IPs and stores the approximate result.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        try:
            self._track(request, response)
        except Exception:
            # Analytics must never break a public request.
            pass

        return response

    def _track(self, request, response):
        if request.method != 'GET':
            return

        if response.status_code < 200 or response.status_code >= 400:
            return

        content_type = str(
            response.get('Content-Type', '')
        ).lower()

        if not content_type.startswith('text/html'):
            return

        path = request.path or '/'

        if path in EXCLUDED_PATHS:
            return

        if any(path.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
            return

        purpose = (
            request.META.get('HTTP_PURPOSE')
            or request.META.get('HTTP_SEC_PURPOSE')
            or ''
        ).lower()

        if 'prefetch' in purpose:
            return

        user = getattr(request, 'user', None)
        if user is not None and getattr(user, 'is_staff', False):
            return

        user_agent = (
            request.META.get('HTTP_USER_AGENT')
            or ''
        ).strip()

        if BOT_PATTERN.search(user_agent):
            return

        ip_address = get_client_ip(request)
        if not ip_address:
            return

        fingerprint = hashlib.sha256(
            (
                ip_address
                + '|'
                + user_agent[:500]
            ).encode('utf-8', 'ignore')
        ).hexdigest()

        from .models import TrafficVisit

        session_start = (
            timezone.now()
            - timedelta(minutes=30)
        )

        if TrafficVisit.objects.filter(
            visitor_hash=fingerprint,
            visited_at__gte=session_start,
        ).exists():
            return

        traffic = classify_traffic(request)

        previous = (
            TrafficVisit.objects
            .filter(
                ip_address=ip_address,
                geo_resolved=True,
            )
            .order_by('-visited_at')
            .first()
        )

        location = location_from_request_headers(
            request
        )

        if not location and previous:
            location = {
                'country_code': previous.country_code,
                'country': previous.country,
                'region': previous.region,
                'city': previous.city,
                'latitude': previous.latitude,
                'longitude': previous.longitude,
                'network_org': previous.network_org,
                'geo_resolved': True,
                'geo_checked_at': previous.geo_checked_at,
            }

        query_string = (
            request.META.get('QUERY_STRING')
            or ''
        )[:2000]

        mobile_tokens = (
            'mobile',
            'android',
            'iphone',
            'ipad',
        )

        TrafficVisit.objects.create(
            ip_address=ip_address,
            visitor_hash=fingerprint,
            path=path[:500],
            query_string=query_string,
            user_agent=user_agent[:2000],
            is_mobile=any(
                token in user_agent.lower()
                for token in mobile_tokens
            ),
            **traffic,
            **location,
        )
