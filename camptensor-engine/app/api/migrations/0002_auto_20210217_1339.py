# Generated by Django 3.1.5 on 2021-02-17 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='endDate',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
