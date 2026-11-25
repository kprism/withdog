from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0039_about_congratulatory_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatbotsetting',
            name='bot_icon',
            field=models.ImageField(blank=True, null=True, upload_to='chatbot/icon/', verbose_name='챗봇 아이콘 이미지'),
        ),
    ]
