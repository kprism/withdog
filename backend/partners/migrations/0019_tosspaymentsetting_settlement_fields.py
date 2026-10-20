from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies=[('partners','0018_tosspaymentsetting_paymentrecord')]
    operations=[
        migrations.AddField(model_name='tosspaymentsetting',name='settlement_bank',field=models.CharField(max_length=80,blank=True,default='')),
        migrations.AddField(model_name='tosspaymentsetting',name='settlement_account',field=models.CharField(max_length=100,blank=True,default='')),
        migrations.AddField(model_name='tosspaymentsetting',name='settlement_holder',field=models.CharField(max_length=100,blank=True,default='')),
        migrations.AddField(model_name='tosspaymentsetting',name='settlement_cycle',field=models.CharField(max_length=100,blank=True,default='')),
        migrations.AddField(model_name='tosspaymentsetting',name='card_fee_rate',field=models.DecimalField(max_digits=5,decimal_places=2,default=0)),
    ]
