# Generated by Django 2.2.5 on 2019-10-01 16:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('openbook_posts', '0063_auto_20191001_1302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='toppost',
            name='post',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='top_post', to='openbook_posts.Post'),
        ),
    ]