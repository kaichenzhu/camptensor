# Generated by Django 3.1.5 on 2021-03-04 09:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_negativesearchtermlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='negativesearchtermlog',
            name='add_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='保存日期'),
        ),
    ]
