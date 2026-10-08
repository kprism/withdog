from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies=[('partners','0016_chatbotsetting')]
    operations=[
        migrations.AddField(model_name='sitesetting',name='favicon',field=models.ImageField(blank=True,upload_to='site/favicon/')),
        migrations.AddField(model_name='sitesetting',name='meta_description',field=models.CharField(blank=True,default='',max_length=320)),
        migrations.AddField(model_name='sitesetting',name='meta_keywords',field=models.CharField(blank=True,default='',max_length=500)),
        migrations.AddField(model_name='sitesetting',name='canonical_url',field=models.URLField(blank=True,default='https://thepetkorea.co.kr/',max_length=500)),
        migrations.AddField(model_name='sitesetting',name='naver_site_verification',field=models.CharField(blank=True,default='',max_length=255)),
        migrations.AddField(model_name='sitesetting',name='google_site_verification',field=models.CharField(blank=True,default='',max_length=255)),
        migrations.AddField(model_name='sitesetting',name='og_title',field=models.CharField(blank=True,default='',max_length=200)),
        migrations.AddField(model_name='sitesetting',name='og_description',field=models.CharField(blank=True,default='',max_length=320)),
        migrations.AddField(model_name='sitesetting',name='og_image_url',field=models.URLField(blank=True,default='',max_length=1000)),
    ]
