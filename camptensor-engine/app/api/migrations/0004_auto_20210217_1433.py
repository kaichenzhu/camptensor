# Generated by Django 3.1.5 on 2021-02-17 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20210217_1341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adgroup',
            name='defaultBid',
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='dailyBudget',
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='keyword',
            name='bid',
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True),
        ),
    ]
