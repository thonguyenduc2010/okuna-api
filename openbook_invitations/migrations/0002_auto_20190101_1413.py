# Generated by Django 2.1.4 on 2019-01-01 13:13

from django.conf import settings
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('openbook_invitations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInvite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invited_date', models.DateField(verbose_name='invited date')),
                ('name', models.CharField(blank=True, max_length=256, null=True)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('username', models.CharField(blank=True, error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 30 characters or fewer. Letters, digits and _ only.', max_length=30, null=True, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('badge_keyword', models.CharField(blank=True, max_length=16, null=True)),
                ('token', models.CharField(max_length=256)),
                ('invited_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invited_users', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='inviteuser',
            name='invited_by',
        ),
        migrations.DeleteModel(
            name='InviteUser',
        ),
    ]
