# Generated by Django 2.2.4 on 2020-01-02 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0007_auto_20200102_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='timestamp',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
