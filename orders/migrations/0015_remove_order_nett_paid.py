# Generated by Django 3.1 on 2022-04-11 04:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0014_auto_20220405_1708'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='nett_paid',
        ),
    ]
