from django.db import migrations, models


DEFAULT_CONTACTS = [
    ('주소', '경남 창원시 성산구 용지로 159, iM뱅크(대구은행) 4층 405호', 1),
    ('대표자', '심규진', 2),
    ('고유번호', '539-80-02508', 3),
    ('전화', '010-3556-8603', 4),
    ('이메일', 'shim194200@gmail.com', 5),
    ('운영시간', '평일 09:00 ~ 18:00', 6),
]


def seed_contact_items(apps, schema_editor):
    AboutContactItem = apps.get_model('partners', 'AboutContactItem')

    if AboutContactItem.objects.exists():
        return

    for label, value, sort_order in DEFAULT_CONTACTS:
        AboutContactItem.objects.create(
            label=label,
            value=value,
            sort_order=sort_order,
            is_visible=True,
        )


def remove_seeded_contact_items(apps, schema_editor):
    AboutContactItem = apps.get_model('partners', 'AboutContactItem')
    labels = [item[0] for item in DEFAULT_CONTACTS]
    AboutContactItem.objects.filter(label__in=labels).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0037_hero_member_join_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='aboutpagesetting',
            name='contact_eyebrow',
            field=models.CharField(default='CONTACT', max_length=100),
        ),
        migrations.AddField(
            model_name='aboutpagesetting',
            name='contact_title',
            field=models.CharField(default='찾아오시는 길', max_length=150),
        ),
        migrations.CreateModel(
            name='AboutContactItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=500)),
                ('sort_order', models.IntegerField(default=0)),
                ('is_visible', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['sort_order', 'pk'],
            },
        ),
        migrations.RunPython(
            seed_contact_items,
            remove_seeded_contact_items,
        ),
    ]
