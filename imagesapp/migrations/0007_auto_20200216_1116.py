# Generated by Django 2.2.3 on 2020-02-16 05:46

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imagesapp', '0006_auto_20200214_1758'),
    ]

    operations = [
        migrations.RenameField(
            model_name='imagemodel',
            old_name='tag',
            new_name='description',
        ),
        migrations.AlterField(
            model_name='imagemodel',
            name='createdDate',
            field=models.DateField(default=datetime.date(2020, 2, 16)),
        ),
    ]
