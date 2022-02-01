# Generated by Django 3.1.7 on 2022-01-28 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_episodio_serie'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='channel',
            name='program',
        ),
        migrations.AddField(
            model_name='movie',
            name='selected',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='Program',
        ),
    ]
