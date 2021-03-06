# Generated by Django 3.1.5 on 2021-02-16 14:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profileId', models.CharField(db_index=True, max_length=100)),
                ('campaignId', models.CharField(db_index=True, max_length=100)),
                ('adGroupId', models.CharField(db_index=True, max_length=100)),
                ('name', models.CharField(max_length=200)),
                ('defaultBid', models.DecimalField(decimal_places=2, max_digits=8)),
                ('state', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profileId', models.CharField(db_index=True, max_length=100)),
                ('portfolioId', models.CharField(db_index=True, max_length=100)),
                ('campaignId', models.CharField(db_index=True, max_length=100)),
                ('name', models.CharField(max_length=200)),
                ('tags', models.JSONField(null=True)),
                ('campaignType', models.CharField(max_length=200)),
                ('targetingType', models.CharField(max_length=200)),
                ('state', models.CharField(max_length=200)),
                ('dailyBudget', models.IntegerField(default=0)),
                ('startDate', models.CharField(max_length=200)),
                ('endDate', models.CharField(max_length=200)),
                ('premiumBidAdjustment', models.BooleanField(default=False)),
                ('bidding', models.JSONField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profileId', models.CharField(db_index=True, max_length=100)),
                ('campaignId', models.CharField(db_index=True, max_length=100)),
                ('adGroupId', models.CharField(db_index=True, max_length=100)),
                ('keywordId', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=200)),
                ('keywordText', models.CharField(max_length=200)),
                ('matchType', models.CharField(max_length=200)),
                ('bid', models.DecimalField(decimal_places=2, max_digits=8)),
            ],
        ),
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profileId', models.CharField(db_index=True, max_length=100)),
                ('portfolioId', models.CharField(db_index=True, max_length=100)),
                ('name', models.CharField(max_length=200)),
                ('budget', models.JSONField(null=True)),
                ('inBudget', models.BooleanField(default=False)),
                ('state', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accessToken', models.CharField(max_length=1000)),
                ('expirTime', models.IntegerField(default=0)),
                ('refreshToken', models.CharField(max_length=1000)),
                ('tokenType', models.CharField(max_length=200)),
                ('lastUpdateTime', models.IntegerField(default=0)),
                ('advertiser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profileId', models.CharField(db_index=True, max_length=100)),
                ('countryCode', models.CharField(max_length=200)),
                ('currencyCode', models.CharField(max_length=200)),
                ('dailyBudget', models.IntegerField(default=0)),
                ('timezone', models.CharField(max_length=200)),
                ('accountInfo', models.JSONField(null=True)),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.shop')),
            ],
        ),
    ]
