# Generated by Django 3.1.7 on 2022-01-13 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_movie_link_m3u8'),
    ]

    operations = [
        migrations.CreateModel(
            name='Episodio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('number', models.CharField(blank=True, max_length=100, null=True)),
                ('image', models.URLField(blank=True, null=True)),
                ('url', models.URLField(blank=True, null=True)),
                ('date', models.CharField(blank=True, max_length=100, null=True)),
                ('is_assistido', models.BooleanField(default=False)),
                ('link_m3u8', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]