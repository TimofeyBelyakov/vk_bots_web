# Generated by Django 4.2.1 on 2023-05-28 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_alter_minmaxfile_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='modelfile',
            name='draft',
            field=models.BooleanField(default=False, verbose_name='Использовать'),
        ),
    ]