# Generated by Django 2.2.4 on 2020-01-02 13:39

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0011_auto_20200102_1635'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='timestamp_st',
        ),
        migrations.AddField(
            model_name='profile',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2020, 1, 2, 13, 39, 46, 881818, tzinfo=utc)),
        ),
    ]
