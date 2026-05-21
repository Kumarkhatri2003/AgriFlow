from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0004_notification_completed_at_notification_is_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='title_np',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AddField(
            model_name='notification',
            name='message_np',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='notification',
            name='action_label_np',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
