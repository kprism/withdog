from .models import SiteSetting


def public_site(request):
    """Site-wide branding for every server-rendered public shell."""
    setting = SiteSetting.get_solo()
    logo_url = ""
    try:
        if (
            setting.logo
            and setting.logo.name
            and setting.logo.storage.exists(setting.logo.name)
        ):
            logo_url = setting.logo.url
    except (OSError, ValueError):
        logo_url = ""

    logo_video_url = ""
    try:
        if (
            setting.logo_video
            and setting.logo_video.name
            and setting.logo_video.storage.exists(setting.logo_video.name)
        ):
            logo_video_url = setting.logo_video.url
    except (OSError, ValueError):
        logo_video_url = ""

    return {
        "public_site": setting,
        "public_site_logo_url": logo_url,
        "public_site_logo_video_url": logo_video_url,
    }
