from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0020_membershipcardgrant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentrecord',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
