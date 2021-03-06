# Generated by Django 2.2.5 on 2019-09-26 12:11

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='openvas_results',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('report', models.CharField(max_length=50, null=True)),
                ('output', models.TextField(null=True)),
                ('finish_date', models.DateTimeField(null=True, verbose_name='date created')),
            ],
        ),
        migrations.CreateModel(
            name='openvas_requests',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('state', models.CharField(choices=[('On Hold', 'On Hold'), ('Running', 'Running'), ('Finished', 'Finished'), ('Blocked', 'Blocked'), ('Deleted', 'Deleted'), ('Scheduled', 'Scheduled')], max_length=20)),
                ('config', models.CharField(choices=[('Discovery', 'Discovery'), ('Full and fast', 'Full and fast'), ('Full and fast ultimate', 'Full and fast ultimate'), ('Full and very deep', 'Full and very deep'), ('Full and very deep ultimate', 'Full and very deep ultimate')], max_length=30)),
                ('percentage', models.IntegerField()),
                ('target', models.CharField(max_length=100)),
                ('mail', models.CharField(max_length=100, null=True)),
                ('insert_date', models.DateTimeField(default=datetime.datetime.now, verbose_name='date created')),
                ('modify_date', models.DateTimeField(null=True, verbose_name='date modified')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
