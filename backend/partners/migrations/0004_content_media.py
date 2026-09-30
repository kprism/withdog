from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies=[('partners','0003_management_models')]
    operations=[
        migrations.AlterField(model_name='contentitem',name='kind',field=models.CharField(choices=[('notice','공지사항'),('community','자유게시판'),('breed','전 세계 견종'),('intro','인트로 갤러리'),('hero','메인 비주얼'),('popup','팝업')],db_index=True,max_length=20)),
        migrations.AddField(model_name='contentitem',name='media_type',field=models.CharField(choices=[('image','이미지'),('video_file','영상 파일'),('video_url','영상 링크')],default='image',max_length=20)),
        migrations.AddField(model_name='contentitem',name='video',field=models.FileField(blank=True,upload_to='content/video/%Y/%m/')),
        migrations.AddField(model_name='contentitem',name='video_url',field=models.URLField(blank=True,max_length=1000)),
        migrations.AddField(model_name='contentitem',name='autoplay',field=models.BooleanField(default=True)),
        migrations.AddField(model_name='contentitem',name='muted',field=models.BooleanField(default=True)),
        migrations.AddField(model_name='contentitem',name='loop',field=models.BooleanField(default=True)),
    ]
