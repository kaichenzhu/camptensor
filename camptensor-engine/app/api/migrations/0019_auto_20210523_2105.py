# Generated by Django 3.1.5 on 2021-05-23 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_shopproducts_promotiontarget'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='state',
            field=models.IntegerField(default=1),
        ),
    ]