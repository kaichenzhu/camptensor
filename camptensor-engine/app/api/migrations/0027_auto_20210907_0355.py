# Generated by Django 3.1.5 on 2021-09-06 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_shop_region'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='region',
            field=models.CharField(default='NA', max_length=200),
        ),
    ]
