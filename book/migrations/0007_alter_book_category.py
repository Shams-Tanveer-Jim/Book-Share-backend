# Generated by Django 4.2.13 on 2024-06-30 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0006_alter_bookimage_book'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='category',
            field=models.ManyToManyField(blank=True, related_name='books', to='book.category'),
        ),
    ]
