from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0031_partner_discount_percent'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesetting',
            name='instagram_url',
            field=models.URLField(blank=True, default='', max_length=500),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='instagram_icon',
            field=models.ImageField(blank=True, upload_to='site/social/'),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='youtube_url',
            field=models.URLField(blank=True, default='', max_length=500),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='youtube_icon',
            field=models.ImageField(blank=True, upload_to='site/social/'),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='naver_blog_url',
            field=models.URLField(blank=True, default='', max_length=500),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='naver_blog_icon',
            field=models.ImageField(blank=True, upload_to='site/social/'),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='facebook_url',
            field=models.URLField(blank=True, default='', max_length=500),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='facebook_icon',
            field=models.ImageField(blank=True, upload_to='site/social/'),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='kakao_channel_url',
            field=models.URLField(blank=True, default='', max_length=500),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='kakao_channel_icon',
            field=models.ImageField(blank=True, upload_to='site/social/'),
        ),
    ]
