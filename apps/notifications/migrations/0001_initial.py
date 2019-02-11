# Generated by Django 2.1 on 2019-02-10 11:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NoticeType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=40, null=True, verbose_name='label')),
                ('title', models.CharField(max_length=150, verbose_name='Title')),
                ('description', models.CharField(max_length=100, verbose_name='description')),
                ('url', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('expire_at', models.DateTimeField(blank=True, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('target_usergroups', models.ManyToManyField(blank=True, help_text='User groups that a notification is sent to.', to='auth.Group')),
            ],
            options={
                'verbose_name': 'WebUpdateNotice',
                'verbose_name_plural': 'WebUpdateNotices',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seen_at', models.DateTimeField(blank=True, null=True)),
                ('deleted', models.BooleanField(default=False)),
                ('notice_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notifications.NoticeType', verbose_name='notice type')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='notification',
            unique_together={('user', 'notice_type')},
        ),
    ]
