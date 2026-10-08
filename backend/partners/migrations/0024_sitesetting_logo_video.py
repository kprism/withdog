from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0023_intro_presentation_controls'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesetting',
            name='logo_video',
            field=models.FileField(blank=True, upload_to='site/logo/video/'),
        ),
    ]
