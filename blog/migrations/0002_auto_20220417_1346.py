# Generated by Django 3.2.10 on 2022-04-17 13:46

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blogpost',
            old_name='ID',
            new_name='id',
        ),
        migrations.RemoveField(
            model_name='blogmedia',
            name='editor_name',
        ),
        migrations.AddField(
            model_name='blogmedia',
            name='media_category',
            field=models.CharField(default=django.utils.timezone.now, max_length=40),
            preserve_default=False,
        ),
    ]
