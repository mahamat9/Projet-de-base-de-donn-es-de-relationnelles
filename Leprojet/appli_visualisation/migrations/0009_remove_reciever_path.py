# Generated by Django 5.0.3 on 2024-04-12 22:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appli_visualisation', '0008_remove_message_message_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reciever',
            name='path',
        ),
    ]
