# Generated by Django 2.2.3 on 2020-02-14 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imagesapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TagsModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tagname', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='imagemodel',
            name='tag',
            field=models.ManyToManyField(null=True, related_name='tags', to='imagesapp.TagsModel'),
        ),
    ]