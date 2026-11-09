from django.db import migrations


OLD_LABEL = '반려견 회원등록'
NEW_LABEL = '반려견 회원가입'


def update_label(apps, schema_editor):
    ContentItem = apps.get_model('partners', 'ContentItem')
    SiteSetting = apps.get_model('partners', 'SiteSetting')

    ContentItem.objects.filter(
        kind='hero',
        hero_button1_text=OLD_LABEL,
    ).update(
        hero_button1_text=NEW_LABEL,
    )

    SiteSetting.objects.filter(
        hero_button1_text=OLD_LABEL,
    ).update(
        hero_button1_text=NEW_LABEL,
    )


def restore_label(apps, schema_editor):
    ContentItem = apps.get_model('partners', 'ContentItem')
    SiteSetting = apps.get_model('partners', 'SiteSetting')

    ContentItem.objects.filter(
        kind='hero',
        hero_button1_text=NEW_LABEL,
    ).update(
        hero_button1_text=OLD_LABEL,
    )

    SiteSetting.objects.filter(
        hero_button1_text=NEW_LABEL,
    ).update(
        hero_button1_text=OLD_LABEL,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0036_partner_registration_discount_range'),
    ]

    operations = [
        migrations.RunPython(
            update_label,
            restore_label,
        ),
    ]
