# Generated by Django 3.0.6 on 2020-06-06 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projection', '0005_auto_20200606_1123'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parameter',
            name='output_url',
        ),
        migrations.AddField(
            model_name='output',
            name='_date_updated',
            field=models.DateField(null=True, verbose_name='date updated'),
        ),
    ]
