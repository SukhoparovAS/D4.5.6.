# Generated by Django 4.0.3 on 2022-03-30 13:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_alter_author_rating_alter_comment_rating_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='author',
            old_name='userName',
            new_name='user',
        ),
    ]
