# Generated by Django 5.1.2 on 2024-10-31 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_remove_customuser_gender_healthdata_gender'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='date_of_birth',
        ),
        migrations.AddField(
            model_name='healthdata',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
    ]
