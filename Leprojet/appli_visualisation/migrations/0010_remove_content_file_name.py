# Generated by Django 5.0.3 on 2024-04-13 15:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appli_visualisation', '0009_remove_reciever_path'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='content',
            name='file_name',
        ),
    ]
