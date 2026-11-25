from django.db import migrations
from django.utils import timezone


TITLE = '경상남도 반려견 협회 회원가입 및 이용 문의 안내'

NOTICE_BODY = """경상남도 반려견 협회 홈페이지를 이용해 주셔서 감사합니다.

회원가입 및 협회 이용과 관련하여 궁금하신 사항이 있으신 경우 아래 연락처로 문의해 주세요.

[문의 가능 내용]
- 일반회원 및 정회원 가입 문의
- 회원가입 절차 및 회원정보 관련 문의
- 반려견 등록 및 홈페이지 이용 문의
- 제휴업체 등록 및 제휴 관련 문의
- 회원 혜택 및 협회 활동 관련 문의
- 기타 경상남도 반려견 협회 관련 문의

[가입 및 이용 문의]
010-3556-8603
010-6622-3454

궁금한 사항이 있으시면 편하게 문의해 주세요.

경상남도 반려견 협회는 회원 여러분께 보다 편리하고 정확한 안내를 드릴 수 있도록 노력하겠습니다.

경상남도 반려견 협회
thepetkorea.co.kr"""

POPUP_BODY = """회원가입, 정회원 가입, 제휴업체 등록,
회원혜택 및 홈페이지 이용에 대해 궁금하신가요?

아래 연락처로 문의해 주세요.

010-3556-8603
010-6622-3454

경상남도 반려견 협회가 안내해 드리겠습니다."""


def create_contact_notice_and_popup(apps, schema_editor):
    BoardCategory = apps.get_model('partners', 'BoardCategory')
    BoardPost = apps.get_model('partners', 'BoardPost')
    ContentItem = apps.get_model('partners', 'ContentItem')

    category, _ = BoardCategory.objects.get_or_create(
        board_type='notice',
        slug='notice',
        defaults={
            'name': '공지사항',
            'sort_order': 0,
            'is_active': True,
        },
    )

    post = BoardPost.objects.filter(
        board_type='notice',
        title=TITLE,
    ).order_by('pk').first()

    now = timezone.now()

    if post is None:
        post = BoardPost.objects.create(
            board_type='notice',
            category=category,
            title=TITLE,
            body=NOTICE_BODY,
            display_type='text',
            is_published=True,
            is_pinned=True,
            is_important=True,
            is_featured=False,
            is_hidden=False,
            allow_comments=True,
            published_at=now,
        )
    else:
        post.category = category
        post.body = NOTICE_BODY
        post.display_type = 'text'
        post.is_published = True
        post.is_pinned = True
        post.is_important = True
        post.is_hidden = False
        post.allow_comments = True
        if not post.published_at:
            post.published_at = now
        post.save()

    popup = ContentItem.objects.filter(
        kind='popup',
        label='contact-notice',
    ).order_by('pk').first()

    defaults = {
        'title': '회원가입 · 협회 이용 문의',
        'body': POPUP_BODY,
        'link': f'/board/{post.pk}/',
        'media_type': 'image',
        'is_published': True,
        'sort_order': -10000,
        'popup_start': now,
        'popup_end': None,
    }

    if popup is None:
        ContentItem.objects.create(
            kind='popup',
            label='contact-notice',
            **defaults,
        )
    else:
        for field, value in defaults.items():
            setattr(popup, field, value)
        popup.save()


def remove_contact_notice_and_popup(apps, schema_editor):
    BoardPost = apps.get_model('partners', 'BoardPost')
    ContentItem = apps.get_model('partners', 'ContentItem')

    ContentItem.objects.filter(
        kind='popup',
        label='contact-notice',
    ).delete()

    BoardPost.objects.filter(
        board_type='notice',
        title=TITLE,
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0034_trafficvisit_classification'),
    ]

    operations = [
        migrations.RunPython(
            create_contact_notice_and_popup,
            remove_contact_notice_and_popup,
        ),
    ]
