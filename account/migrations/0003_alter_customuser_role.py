# Generated by Django 4.2.13 on 2024-06-25 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_customuser_delete_user_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('ADMIN', 'Admin'), ('ADMISTRATIVEADMIN', 'AdminstrativeAdmin'), ('USER', 'User')], default='ADMISTRATIVEADMIN', max_length=20),
        ),
    ]