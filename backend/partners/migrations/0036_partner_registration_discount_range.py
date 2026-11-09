from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0035_membership_contact_notice_popup'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='discount_min_percent',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='최소 회원 할인율(%)'),
        ),
        migrations.AddField(
            model_name='partner',
            name='representative_name',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='대표자명'),
        ),
        migrations.AddField(
            model_name='partner',
            name='contact_email',
            field=models.EmailField(blank=True, default='', max_length=254, verbose_name='이메일'),
        ),
        migrations.AddField(
            model_name='partner',
            name='application_note',
            field=models.TextField(blank=True, default='', verbose_name='제휴 신청 내용'),
        ),
        migrations.AddField(
            model_name='partner',
            name='application_status',
            field=models.CharField(
                choices=[('approved','승인'),('pending','승인대기'),('rejected','반려')],
                db_index=True,
                default='approved',
                max_length=20,
                verbose_name='제휴 등록 상태',
            ),
        ),
        migrations.AlterField(
            model_name='partner',
            name='discount_percent',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='최대 회원 할인율(%)'),
        ),
    ]
