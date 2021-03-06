# Generated by Django 2.2.4 on 2019-12-24 08:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=500, verbose_name='Comment')),
                ('is_approved', models.BooleanField(default=True)),
                ('is_rejected', models.BooleanField(default=False)),
                ('commented_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
            ],
        ),
        migrations.CreateModel(
            name='Replies',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reply', models.CharField(max_length=500)),
                ('is_approved', models.BooleanField(default=True)),
                ('is_rejected', models.BooleanField(default=False)),
                ('commented_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parent', to='social.Comment')),
                ('parent_reply', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='social.Replies')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default='default_pic.png', upload_to='profile/')),
                ('country', models.CharField(default='', max_length=100)),
                ('state', models.CharField(default='', max_length=100)),
                ('city', models.CharField(default='', max_length=100)),
                ('fullAddress', models.CharField(default='', max_length=100)),
                ('pin', models.CharField(default='', max_length=100)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(max_length=1)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(blank=True, choices=[('adventure', 'Adventure'), ('fitness', 'Fitness'), ('health', 'Health'), ('food', 'Food'), ('sports', 'Sports')], max_length=256, null=True)),
                ('subcategory', models.CharField(blank=True, max_length=256, null=True)),
                ('title', models.CharField(max_length=200)),
                ('text', models.TextField()),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('published_date', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='social.Post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Dislike',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dislikes', to='social.Post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social.Post'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
