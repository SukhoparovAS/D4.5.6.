# Generated by Django 4.0.3 on 2022-04-08 13:34

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('news', '0009_alter_ssubscriber_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='ssubscriber',
            unique_together={('user', 'category')},
        ),
    ]
