from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0033_trafficvisit'),
    ]

    operations = [
        migrations.AddField(
            model_name='trafficvisit',
            name='visitor_type',
            field=models.CharField(
                choices=[
                    ('human', '실제 방문 추정'),
                    ('search_bot', '검색봇'),
                    ('scanner', '보안스캐너·자동봇'),
                ],
                db_index=True,
                default='human',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='trafficvisit',
            name='classification_reason',
            field=models.CharField(
                blank=True,
                default='',
                max_length=220,
            ),
        ),
        migrations.AddIndex(
            model_name='trafficvisit',
            index=models.Index(
                fields=['visited_at', 'visitor_type'],
                name='traffic_time_visitor_idx',
            ),
        ),
    ]
