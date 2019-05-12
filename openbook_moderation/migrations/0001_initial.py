# Generated by Django 2.2 on 2019-05-12 16:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ModeratedObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=1000, null=True, verbose_name='description')),
                ('approved', models.BooleanField(default=False, verbose_name='approved')),
                ('verified', models.BooleanField(default=False, verbose_name='verified')),
                ('submitted', models.BooleanField(default=False, verbose_name='submitted')),
                ('object_type', models.CharField(choices=[('P', 'Post'), ('PC', 'Post Comment'), ('C', 'Community'), ('U', 'User'), ('MO', 'MO')], max_length=5)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='ModeratedObjectApprovedChangedLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changed_from', models.BooleanField(verbose_name='changed from')),
                ('changed_to', models.BooleanField(verbose_name='changed to')),
            ],
        ),
        migrations.CreateModel(
            name='ModeratedObjectDescriptionChangedLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changed_from', models.CharField(max_length=1000, verbose_name='changed from')),
                ('changed_to', models.CharField(max_length=1000, verbose_name='changed to')),
            ],
        ),
        migrations.CreateModel(
            name='ModeratedObjectSubmittedChangedLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changed_from', models.BooleanField(verbose_name='changed from')),
                ('changed_to', models.BooleanField(verbose_name='changed to')),
            ],
        ),
        migrations.CreateModel(
            name='ModeratedObjectVerifiedChangedLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changed_from', models.BooleanField(verbose_name='changed from')),
                ('changed_to', models.BooleanField(verbose_name='changed to')),
            ],
        ),
        migrations.CreateModel(
            name='ModerationCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='name')),
                ('title', models.CharField(max_length=32, verbose_name='title')),
                ('description', models.CharField(max_length=255, verbose_name='description')),
                ('created', models.DateTimeField(db_index=True, editable=False)),
                ('severity', models.CharField(choices=[('C', 'Critical'), ('H', 'High'), ('M', 'Medium'), ('L', 'Low')], max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='ModerationReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=1000, null=True, verbose_name='description')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='openbook_moderation.ModerationCategory')),
                ('overview', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='openbook_moderation.ModeratedObject')),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='moderation_reports', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ModerationPenalty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.DateTimeField(editable=False)),
                ('moderated_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='penalties', to='openbook_moderation.ModeratedObject')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='moderation_penalties', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ModeratedObjectLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_type', models.CharField(choices=[('DC', 'Description Changed'), ('AC', 'Approved Changed'), ('TC', 'Type Changed'), ('SC', 'Submitted Changed'), ('VC', 'Verified Changed'), ('CC', 'Category Changed')], max_length=5)),
                ('object_id', models.PositiveIntegerField()),
                ('created', models.DateTimeField(db_index=True, editable=False)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('moderated_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='openbook_moderation.ModeratedObject')),
            ],
        ),
        migrations.CreateModel(
            name='ModeratedObjectCategoryChangedLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changed_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='openbook_moderation.ModerationCategory')),
                ('changed_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='openbook_moderation.ModerationCategory')),
            ],
        ),
    ]
