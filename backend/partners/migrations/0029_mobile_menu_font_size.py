from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0028_boardattachment_external_media'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesetting',
            name='header_mobile_menu_font_size',
            field=models.PositiveSmallIntegerField(default=13),
        ),
    ]
