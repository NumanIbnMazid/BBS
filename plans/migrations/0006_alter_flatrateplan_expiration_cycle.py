# Generated by Django 3.2.6 on 2022-02-07 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0005_auto_20211107_0923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flatrateplan',
            name='expiration_cycle',
            field=models.SmallIntegerField(choices=[(0, 'Monthly'), (1, 'Yearly'), (2, 'Half-Yearly')], default=0),
        ),
    ]
