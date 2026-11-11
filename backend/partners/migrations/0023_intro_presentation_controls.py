from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0022_intro_layer_editor'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentitem',
            name='hero_meta1_font_size',
            field=models.PositiveSmallIntegerField(default=16),
        ),
        migrations.AddField(
            model_name='contentitem',
            name='hero_meta2_font_size',
            field=models.PositiveSmallIntegerField(default=16),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='header_menu_font_size',
            field=models.PositiveSmallIntegerField(default=16),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='header_menu_font_weight',
            field=models.PositiveSmallIntegerField(default=700),
        ),
        migrations.AddField(
            model_name='sitesetting',
            name='intro_header_opacity',
            field=models.PositiveSmallIntegerField(default=82),
        ),
    ]
