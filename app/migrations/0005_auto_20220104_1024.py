# Generated by Django 3.1.7 on 2022-01-04 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20220104_1009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='link_m3u8',
            field=models.TextField(blank=True, null=True),
        ),
    ]
