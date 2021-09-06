# Generated by Django 3.2.6 on 2021-09-06 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='thread',
            name='weight',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='thread weight'),
        ),
    ]
