# Generated by Django 3.2.20 on 2023-09-06 09:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20230906_0812'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='ingrecdients',
            new_name='ingredients',
        ),
    ]
