from django.db import migrations


def add_community_event_category(apps, schema_editor):
    BoardCategory = apps.get_model('partners', 'BoardCategory')

    category, created = BoardCategory.objects.get_or_create(
        board_type='community',
        slug='event',
        defaults={
            'name': '행사',
            'sort_order': 90,
            'is_active': True,
        },
    )

    if not created:
        changed = False
        if category.name != '행사':
            category.name = '행사'
            changed = True
        if not category.is_active:
            category.is_active = True
            changed = True
        if changed:
            category.save(update_fields=['name', 'is_active'])


def remove_community_event_category(apps, schema_editor):
    BoardCategory = apps.get_model('partners', 'BoardCategory')
    BoardCategory.objects.filter(
        board_type='community',
        slug='event',
        name='행사',
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0029_mobile_menu_font_size'),
    ]

    operations = [
        migrations.RunPython(
            add_community_event_category,
            remove_community_event_category,
        ),
    ]
