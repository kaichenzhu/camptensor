# Generated by Django 3.1.5 on 2021-03-14 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_adgroup_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='target',
            name='expressionValue',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
