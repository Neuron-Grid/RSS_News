# Generated by Django 4.2.3 on 2023-07-04 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reader', '0002_alter_entry_feed_alter_entry_pub_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feed',
            name='title',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]