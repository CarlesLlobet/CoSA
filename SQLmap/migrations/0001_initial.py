# Generated by Django 2.2.5 on 2019-10-07 13:32

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
            name='sqlmap_results',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('output', models.TextField(null=True)),
                ('report', models.TextField(null=True)),
                ('finish_date', models.DateTimeField(null=True, verbose_name='date created')),
            ],
        ),
        migrations.CreateModel(
            name='sqlmap_requests',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('target', models.CharField(max_length=100)),
                ('charset', models.CharField(choices=[('UTF-8', 'Eight-bit UCS Transformation Format'), ('ISO-8859-1', 'ISO Latin Alphabet No. 1, a.k.a. ISO-LATIN-1'), ('US-ASCII', 'Seven-bit ASCII, a.k.a. ISO646-US, a.k.a. the Basic Latin block of the Unicode character set'), ('UTF-16BE', 'Sixteen-bit UCS Transformation Format, big-endian byte order'), ('UTF-16LE', 'Sixteen-bit UCS Transformation Format, little-endian byte order'), ('UTF-16', 'Sixteen-bit UCS Transformation Format, byte order identified by an optional byte-order mark')], max_length=10)),
                ('verbosity', models.IntegerField(choices=[(0, 'errors'), (1, 'warnings'), (2, 'debug'), (3, 'payloads'), (4, 'requests'), (5, 'resp.headers'), (6, 'resp.content')])),
                ('level', models.IntegerField(choices=[(1, 'get&post'), (2, 'cookie'), (3, 'user-agent'), (4, 'almost_everything'), (5, 'everything')])),
                ('risk', models.IntegerField(choices=[(1, 'low'), (2, 'long_time'), (3, 'or_queries')])),
                ('depth', models.IntegerField(choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10')])),
                ('state', models.CharField(choices=[('On Hold', 'On Hold'), ('Running', 'Running'), ('Finished', 'Finished'), ('Blocked', 'Blocked'), ('Deleted', 'Deleted'), ('Saved', 'Saved')], max_length=20)),
                ('mail', models.CharField(max_length=100, null=True)),
                ('insert_date', models.DateTimeField(default=datetime.datetime.now, verbose_name='date created')),
                ('modify_date', models.DateTimeField(null=True, verbose_name='date modified')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
