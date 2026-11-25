from datetime import timedelta
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

def seed_existing_regular(apps, schema_editor):
    MemberProfile=apps.get_model('partners','MemberProfile')
    Grant=apps.get_model('partners','MembershipCardGrant')
    # Migration-time snapshot: only members already marked regular before
    # payment-gated issuance is introduced receive the legacy exception.
    for p in MemberProfile.objects.filter(membership_status='regular').select_related('user'):
        start=p.joined_at.date()
        try: end=start.replace(year=start.year+1)
        except ValueError: end=start.replace(year=start.year+1,month=2,day=28)
        Grant.objects.get_or_create(user_id=p.user_id,defaults={'source':'legacy','valid_from':start,'valid_to':end,'is_active':True})

class Migration(migrations.Migration):
    dependencies=[('partners','0019_tosspaymentsetting_settlement_fields'),migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[
        migrations.CreateModel(
            name='MembershipCardGrant',
            fields=[
                ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
                ('source',models.CharField(choices=[('legacy','기존 정회원 예외발급'),('payment','토스 연회비 결제')],max_length=20)),
                ('issued_at',models.DateTimeField(auto_now_add=True)),
                ('valid_from',models.DateField()),
                ('valid_to',models.DateField()),
                ('is_active',models.BooleanField(default=True)),
                ('payment',models.OneToOneField(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,related_name='membership_card_grant',to='partners.paymentrecord')),
                ('user',models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,related_name='membership_card_grant',to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RunPython(seed_existing_regular,migrations.RunPython.noop),
    ]
