# Generated by Django 3.1.5 on 2021-03-04 19:02

import django.contrib.postgres.fields
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20210304_1818'),
    ]

    operations = [
        migrations.CreateModel(
            name='OptimizeSearchtermLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profileId', models.CharField(db_index=True, max_length=100)),
                ('campaignId', models.CharField(db_index=True, max_length=100)),
                ('adGroupId', models.CharField(db_index=True, max_length=100)),
                ('targetId', models.CharField(db_index=True, max_length=100)),
                ('type', models.CharField(max_length=50)),
                ('campaignName', models.CharField(max_length=200)),
                ('adGroupName', models.CharField(max_length=200)),
                ('query', models.CharField(max_length=200)),
                ('selectCampaignId', models.CharField(max_length=100)),
                ('selectCampaignName', models.CharField(max_length=200)),
                ('selectAdGroupId', models.CharField(max_length=100)),
                ('selectAdGroupName', models.CharField(max_length=200)),
                ('matchType', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), null=True, size=None)),
                ('impressions', models.IntegerField(default=0)),
                ('clicks', models.IntegerField(default=0)),
                ('orders', models.IntegerField(default=0)),
                ('spends', models.DecimalField(decimal_places=2, max_digits=8, null=True)),
                ('sales', models.DecimalField(decimal_places=2, max_digits=8, null=True)),
                ('add_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
