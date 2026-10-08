from django.db import migrations, models
from django.utils import timezone


DEFAULT_POLICIES = {
    'privacy': (
        '개인정보처리방침',
        '경상남도 반려견 협회는 회원가입 및 회원관리, 본인확인, 회원증 발급과 서비스 제공을 위해 '
        '성명, 생년월일, 성별, 연락처, 이메일, 주소 등 가입 과정에서 입력한 정보를 수집·이용합니다.\n\n'
        '수집된 정보는 회원 탈퇴 시까지 보관하는 것을 원칙으로 하며, 관계 법령에 따라 보존이 필요한 '
        '정보는 해당 기간 동안 별도 보관할 수 있습니다. 개인정보 수집·이용에 동의하지 않을 수 있으나, '
        '필수정보 동의를 거부할 경우 회원가입이 제한될 수 있습니다.'
    ),
    'terms': (
        '웹사이트 이용약관',
        '회원은 정확한 정보를 제공하고 본인의 계정을 안전하게 관리해야 하며, 타인의 권리를 침해하거나 '
        '서비스 운영을 방해하는 행위를 해서는 안 됩니다.\n\n'
        '협회는 서비스 품질 개선이나 운영상 필요에 따라 웹사이트의 일부 기능과 콘텐츠를 변경할 수 있으며, '
        '중요한 변경사항은 가능한 범위에서 사전에 안내합니다.'
    ),
    'rules': (
        '[협회] 회원규칙',
        '회원은 협회의 목적과 운영질서를 존중하고 회원정보를 사실대로 유지하며, 협회와 다른 회원의 명예 '
        '또는 권익을 침해하는 행위를 하지 않아야 합니다.\n\n'
        '정회원 혜택과 온라인 회원증은 정해진 연회비 및 회원정책에 따라 제공되며, 연회비는 1년 단위로 '
        '갱신됩니다. 회원은 탈퇴를 요청할 수 있으며, 이미 납부한 연회비는 안내된 환불정책에 따릅니다.'
    ),
}

DOG_LIFE_CATEGORIES = [
    ('training-life', '훈련·생활팁'),
    ('walk-play', '산책·놀이'),
    ('health-care', '건강·돌봄'),
    ('food-nutrition', '먹거리·영양'),
    ('grooming-hygiene', '미용·위생'),
    ('behavior-bond', '행동·교감'),
    ('show-off', '반려견 자랑'),
    ('travel-outing', '여행·외출'),
    ('growth-adoption', '성장·입양일기'),
    ('association-local', '협회·지역소식'),
]


def seed_policy_and_doglife(apps, schema_editor):
    PolicyDocument = apps.get_model('partners', 'PolicyDocument')
    BoardCategory = apps.get_model('partners', 'BoardCategory')

    for key, (title, body) in DEFAULT_POLICIES.items():
        PolicyDocument.objects.update_or_create(
            key=key,
            defaults={'title': title, 'body': body, 'is_active': True},
        )

    for order, (slug, name) in enumerate(DOG_LIFE_CATEGORIES, start=1):
        BoardCategory.objects.update_or_create(
            board_type='doglife',
            slug=slug,
            defaults={
                'name': name,
                'sort_order': order,
                'is_active': True,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0024_sitesetting_logo_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='memberprofile',
            name='terms_agreed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='memberprofile',
            name='rules_agreed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='memberprofile',
            name='agreements_updated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='boardcategory',
            name='board_type',
            field=models.CharField(
                choices=[
                    ('notice', '공지사항'),
                    ('community', '자유게시판'),
                    ('doglife', '견생(Dog Life)'),
                ],
                db_index=True,
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='boardpost',
            name='board_type',
            field=models.CharField(
                choices=[
                    ('notice', '공지사항'),
                    ('community', '자유게시판'),
                    ('doglife', '견생(Dog Life)'),
                ],
                db_index=True,
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='boardpost',
            name='display_type',
            field=models.CharField(
                choices=[
                    ('text', '글'),
                    ('image_large', '이미지+글 50%'),
                    ('image_small', '이미지+글 10%'),
                    ('video_horizontal', '가로영상'),
                    ('video_vertical', '세로영상'),
                ],
                db_index=True,
                default='text',
                max_length=30,
            ),
        ),
        migrations.CreateModel(
            name='PolicyDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(choices=[('privacy', '개인정보처리방침'), ('terms', '웹사이트 이용약관'), ('rules', '[협회] 회원규칙')], max_length=30, unique=True)),
                ('title', models.CharField(max_length=120)),
                ('body', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['id']},
        ),
        migrations.RunPython(seed_policy_and_doglife, migrations.RunPython.noop),
    ]
}
