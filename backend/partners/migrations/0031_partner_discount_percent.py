from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0030_community_event_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='discount_percent',
            field=models.PositiveSmallIntegerField(
                default=0,
                verbose_name='회원 할인율(%)',
            ),
        ),
    ]
