# Generated by Django 5.0.3 on 2024-04-12 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appli_visualisation', '0006_alter_employee_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='message_id',
            field=models.CharField(default='', max_length=50, unique=True),
        ),
    ]