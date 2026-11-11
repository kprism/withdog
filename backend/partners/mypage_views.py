from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render

from .models import MemberProfile, MembershipCardGrant, SiteSetting


def _safe_file_url(field):
    """Return a media URL only when the backing file really exists."""
    try:
        if field and field.name and field.storage.exists(field.name):
            return field.url
    except (OSError, ValueError):
        pass
    return ""


@login_required(login_url='/')
def mypage_home(request):
    if request.user.is_staff:
        return redirect('/dashboard/')
    return redirect('public_membership_card')


@login_required(login_url='/')
def membership_card(request):
    if request.user.is_staff:
        return redirect('/dashboard/')

    try:
        profile = MemberProfile.objects.get(user=request.user)
    except MemberProfile.DoesNotExist as exc:
        raise Http404('회원 프로필을 찾을 수 없습니다.') from exc

    try:
        grant = MembershipCardGrant.objects.get(
            user=request.user,
            is_active=True,
        )
    except MembershipCardGrant.DoesNotExist:
        return render(
            request,
            'website/mypage.html',
            {
                'card_allowed': False,
                'membership_label': dict(MemberProfile.STATUSES).get(
                    profile.membership_status,
                    profile.membership_status,
                ),
            },
        )

    site_setting = SiteSetting.get_solo()
    membership_label = dict(MemberProfile.STATUSES).get(
        profile.membership_status,
        profile.membership_status,
    )

    return render(
        request,
        'website/mypage.html',
        {
            'card_allowed': True,
            'grant_source': grant.source,
            'member_name': profile.name or request.user.get_username(),
            'member_no': f'GN-{profile.pk:05d}',
            'joined_date': grant.valid_from.strftime('%Y.%m.%d'),
            'expiry_date': grant.valid_to.strftime('%Y.%m.%d'),
            'membership_label': membership_label,
            'birth_date': (
                profile.birth_date.strftime('%Y.%m.%d')
                if profile.birth_date
                else '-'
            ),
            'address_short': ' '.join(
                (profile.region or profile.address_detail or '').split()[:2]
            ),
            'phone': profile.phone or '-',
            'gender_code': (
                profile.gender
                if profile.gender in ('M', 'F')
                else '-'
            ),
            'kakao_javascript_key': site_setting.kakao_javascript_key,
        },
    )
