from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def backfill_payment_member_snapshot(apps, schema_editor):
    PaymentRecord = apps.get_model('partners', 'PaymentRecord')
    MemberProfile = apps.get_model('partners', 'MemberProfile')

    for row in PaymentRecord.objects.exclude(user_id=None).iterator():
        profile = MemberProfile.objects.filter(user_id=row.user_id).first()
        user = row.user
        row.member_name = getattr(profile, 'name', '') or ''
        row.member_birth_date = getattr(profile, 'birth_date', None)
        row.member_email = (getattr(user, 'email', '') or getattr(user, 'username', '') or '')
        row.member_region = getattr(profile, 'region', '') or ''
        row.member_address = getattr(profile, 'address_detail', '') or ''
        row.save(update_fields=[
            'member_name',
            'member_birth_date',
            'member_email',
            'member_region',
            'member_address',
        ])


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0025_policy_doglife'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentrecord',
            name='member_name',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='paymentrecord',
            name='member_birth_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='paymentrecord',
            name='member_email',
            field=models.EmailField(blank=True, default='', max_length=254),
        ),
        migrations.AddField(
            model_name='paymentrecord',
            name='member_region',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='paymentrecord',
            name='member_address',
            field=models.CharField(blank=True, default='', max_length=300),
        ),
        migrations.RunPython(
            backfill_payment_member_snapshot,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='payment_records',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
