# Generated by Django 5.1.2 on 2024-10-31 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_rename_date_of_birth_healthdata_birthdate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='healthdata',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female')], max_length=10, null=True),
        ),
    ]