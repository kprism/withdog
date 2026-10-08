from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0021_alter_paymentrecord_id'),
    ]

    operations = [
        migrations.AddField(model_name='sitesetting', name='header_logo_size', field=models.PositiveSmallIntegerField(default=48)),
        migrations.AddField(model_name='sitesetting', name='header_site_name_size', field=models.PositiveSmallIntegerField(default=17)),
        migrations.AddField(model_name='sitesetting', name='header_site_name_weight', field=models.PositiveSmallIntegerField(default=800)),
        migrations.AddField(model_name='sitesetting', name='header_subtitle_size', field=models.PositiveSmallIntegerField(default=12)),
        migrations.AddField(model_name='sitesetting', name='header_subtitle_weight', field=models.PositiveSmallIntegerField(default=500)),
        migrations.AddField(model_name='sitesetting', name='intro_stage_height', field=models.PositiveIntegerField(default=864)),
        migrations.AddField(model_name='sitesetting', name='intro_stage_width', field=models.PositiveIntegerField(default=1920)),
        migrations.CreateModel(
            name='IntroLayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='새 레이어', max_length=100)),
                ('layer_type', models.CharField(choices=[('text', '텍스트'), ('image', '이미지'), ('video', '동영상'), ('button', '버튼'), ('overlay', '오버레이')], default='text', max_length=20)),
                ('text', models.TextField(blank=True, default='')),
                ('link', models.CharField(blank=True, default='', max_length=500)),
                ('image', models.FileField(blank=True, upload_to='intro/layers/')),
                ('video', models.FileField(blank=True, upload_to='intro/layers/video/')),
                ('x_px', models.IntegerField(default=120)),
                ('y_px', models.IntegerField(default=220)),
                ('width_px', models.PositiveIntegerField(default=520)),
                ('height_px', models.PositiveIntegerField(default=120)),
                ('opacity', models.PositiveSmallIntegerField(default=100)),
                ('z_index', models.PositiveSmallIntegerField(default=2)),
                ('font_size', models.PositiveSmallIntegerField(default=40)),
                ('font_weight', models.PositiveSmallIntegerField(default=800)),
                ('color', models.CharField(default='#ffffff', max_length=40)),
                ('background', models.CharField(blank=True, default='transparent', max_length=80)),
                ('border_radius', models.PositiveSmallIntegerField(default=0)),
                ('object_fit', models.CharField(choices=[('contain', 'Contain'), ('cover', 'Cover')], default='contain', max_length=10)),
                ('animation', models.CharField(choices=[('fade-up', 'Fade Up'), ('fade', 'Fade In'), ('slide-left', 'Slide Left'), ('slide-right', 'Slide Right'), ('zoom-in', 'Zoom In'), ('none', '없음')], default='fade-up', max_length=20)),
                ('animation_delay_ms', models.PositiveIntegerField(default=200)),
                ('animation_duration_ms', models.PositiveIntegerField(default=700)),
                ('is_visible', models.BooleanField(default=True)),
                ('sort_order', models.IntegerField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('hero', models.ForeignKey(limit_choices_to={'kind': 'hero'}, on_delete=django.db.models.deletion.CASCADE, related_name='intro_layers', to='partners.contentitem')),
            ],
            options={'ordering': ['z_index', 'sort_order', 'pk']},
        ),
    ]
