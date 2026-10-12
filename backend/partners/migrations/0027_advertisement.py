from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0026_payment_member_snapshot'),
    ]

    operations = [
        migrations.CreateModel(
            name='Advertisement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('advertiser_name', models.CharField(max_length=160, verbose_name='광고주 업체명')),
                ('representative_name', models.CharField(blank=True, default='', max_length=100, verbose_name='대표자명')),
                ('business_number', models.CharField(blank=True, default='', max_length=40, verbose_name='사업자번호')),
                ('title', models.CharField(blank=True, default='', max_length=180, verbose_name='광고 제목')),
                ('target_page', models.CharField(choices=[('all', '전체 공개페이지'), ('home', '인트로/메인'), ('about', '협회ㆍ임원진 소개'), ('benefits', '회원혜택'), ('partners', '후원업체/관련업체'), ('doglife', '견생(Dog Life)'), ('board', '공지사항'), ('community', '커뮤니티'), ('breeds', '전 세계 견종'), ('mypage', '마이페이지')], db_index=True, default='home', max_length=30)),
                ('placement', models.CharField(choices=[('right', '우측 광고 섹션'), ('section_top', '섹션 사이 · 상단'), ('section_middle', '섹션 사이 · 중단'), ('section_bottom', '섹션 사이 · 하단'), ('popup', '팝업 광고')], db_index=True, default='right', max_length=30)),
                ('start_date', models.DateField(verbose_name='게재 시작일')),
                ('end_date', models.DateField(verbose_name='게재 종료일')),
                ('fee', models.PositiveIntegerField(default=0, verbose_name='광고비')),
                ('media_type', models.CharField(choices=[('image', '이미지'), ('video', 'MP4/영상')], default='image', max_length=20)),
                ('media_file', models.FileField(blank=True, upload_to='ads/%Y/%m/')),
                ('link_url', models.URLField(blank=True, default='', max_length=1000)),
                ('alt_text', models.CharField(blank=True, default='', max_length=220)),
                ('is_active', models.BooleanField(default=True)),
                ('sort_order', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['target_page', 'placement', 'sort_order', '-created_at']},
        ),
        migrations.AddIndex(model_name='advertisement', index=models.Index(fields=['target_page', 'placement', 'is_active'], name='partners_ad_target_061be6_idx')),
        migrations.AddIndex(model_name='advertisement', index=models.Index(fields=['start_date', 'end_date'], name='partners_ad_start_d_8d9683_idx')),
    ]
}
