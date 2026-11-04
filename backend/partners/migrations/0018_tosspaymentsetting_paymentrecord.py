from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies=[('partners','0017_sitesetting_seo_fields'),migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[
        migrations.CreateModel(name='TossPaymentSetting',fields=[('id',models.PositiveSmallIntegerField(primary_key=True,serialize=False,default=1,editable=False)),('test_client_key',models.CharField(max_length=255,blank=True,default='')),('test_secret_key',models.CharField(max_length=255,blank=True,default='')),('live_client_key',models.CharField(max_length=255,blank=True,default='')),('live_secret_key',models.CharField(max_length=255,blank=True,default='')),('live_enabled',models.BooleanField(default=False)),('annual_fee',models.PositiveIntegerField(default=30000)),('updated_at',models.DateTimeField(auto_now=True))]),
        migrations.CreateModel(name='PaymentRecord',fields=[('id',models.BigAutoField(primary_key=True,serialize=False)),('environment',models.CharField(max_length=10,choices=[('test','테스트'),('live','라이브')],default='test',db_index=True)),('order_id',models.CharField(max_length=64,unique=True)),('payment_key',models.CharField(max_length=200,blank=True,default='',db_index=True)),('order_name',models.CharField(max_length=100,default='정회원 연회비')),('amount',models.PositiveIntegerField(default=30000)),('status',models.CharField(max_length=30,default='READY',db_index=True)),('method',models.CharField(max_length=50,blank=True,default='')),('approved_at',models.DateTimeField(null=True,blank=True)),('raw_response',models.JSONField(default=dict,blank=True)),('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),('user',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='payment_records',to=settings.AUTH_USER_MODEL))],options={'ordering':['-created_at']})
    ]
