# Generated by Django 3.1.5 on 2021-07-16 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_auto_20210523_2336'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopproducts',
            name='state',
            field=models.IntegerField(default=0),
        ),
    ]
