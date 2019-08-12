# Generated by Django 2.2.4 on 2019-08-01 14:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('openbook_posts', '0038_postcommentusermention_postusermention'),
        ('openbook_notifications', '0012_auto_20190623_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('PR', 'Post Reaction'), ('PC', 'Post Comment'), ('PCR', 'Post Comment Reply'), ('PCRA', 'Post Comment Reaction'), ('CR', 'Connection Request'), ('CC', 'Connection Confirmed'), ('F', 'Follow'), ('CI', 'Community Invite'), ('PUM', 'Post user mention'), ('PCUM', 'Post comment user mention')], max_length=5),
        ),
        migrations.CreateModel(
            name='PostUserMentionNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_user_mention', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='openbook_posts.PostUserMention')),
            ],
        ),
        migrations.CreateModel(
            name='PostCommentUserMentionNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_comment_user_mention', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='openbook_posts.PostCommentUserMention')),
            ],
        ),
    ]
