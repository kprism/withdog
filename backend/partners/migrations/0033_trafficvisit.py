from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0032_sitesetting_footer_social'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrafficVisit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visited_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ip_address', models.GenericIPAddressField(db_index=True)),
                ('visitor_hash', models.CharField(db_index=True, max_length=64)),
                ('path', models.CharField(blank=True, default='', max_length=500)),
                ('query_string', models.TextField(blank=True, default='')),
                ('referrer', models.TextField(blank=True, default='')),
                ('referrer_host', models.CharField(blank=True, default='', max_length=255)),
                ('source_type', models.CharField(choices=[('direct', '직접 방문'), ('search', '검색'), ('social', 'SNS'), ('referral', '외부 링크'), ('campaign', '캠페인'), ('internal', '내부 이동')], db_index=True, default='direct', max_length=20)),
                ('source_name', models.CharField(blank=True, db_index=True, default='직접 방문', max_length=80)),
                ('keyword', models.CharField(blank=True, db_index=True, default='', max_length=255)),
                ('user_agent', models.TextField(blank=True, default='')),
                ('is_mobile', models.BooleanField(default=False)),
                ('country_code', models.CharField(blank=True, default='', max_length=8)),
                ('country', models.CharField(blank=True, default='', max_length=100)),
                ('region', models.CharField(blank=True, default='', max_length=120)),
                ('city', models.CharField(blank=True, default='', max_length=120)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('network_org', models.CharField(blank=True, default='', max_length=220)),
                ('geo_resolved', models.BooleanField(db_index=True, default=False)),
                ('geo_checked_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-visited_at'],
            },
        ),
        migrations.AddIndex(
            model_name='trafficvisit',
            index=models.Index(fields=['visited_at', 'source_type'], name='traffic_time_source_idx'),
        ),
        migrations.AddIndex(
            model_name='trafficvisit',
            index=models.Index(fields=['ip_address', 'visited_at'], name='traffic_ip_time_idx'),
        ),
    ]
