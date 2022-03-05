# Generated by Django 3.1.7 on 2022-02-10 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_auto_20220205_0935'),
    ]

    operations = [
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('source', models.TextField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('image', models.URLField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]