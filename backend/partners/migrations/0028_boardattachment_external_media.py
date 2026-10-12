from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0027_advertisement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boardattachment',
            name='file',
            field=models.FileField(blank=True, upload_to='board/%Y/%m/%d/'),
        ),
        migrations.AddField(
            model_name='boardattachment',
            name='external_url',
            field=models.URLField(blank=True, default='', max_length=2000),
        ),
        migrations.AddField(
            model_name='boardattachment',
            name='external_provider',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', '파일'),
                    ('youtube', 'YouTube'),
                    ('vimeo', 'Vimeo'),
                    ('video', '직접 영상 링크'),
                    ('link', '외부 링크'),
                ],
                default='',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='boardattachment',
            name='external_media_id',
            field=models.CharField(blank=True, default='', max_length=128),
        ),
    ]
}
