from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0038_about_contact_items'),
    ]

    operations = [
        migrations.CreateModel(
            name='AboutCongratulatoryMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(blank=True, upload_to='about/congratulations/')),
                ('position', models.CharField(blank=True, max_length=150)),
                ('name', models.CharField(blank=True, max_length=120)),
                ('message', models.TextField(blank=True)),
                ('sort_order', models.IntegerField(default=0)),
                ('is_visible', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['sort_order', 'pk'],
            },
        ),
    ]
