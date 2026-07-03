from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0006_alter_notification_source_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='due_date',
            field=models.DateField(
                blank=True,
                help_text='Scheduled activity date for calendar views',
                null=True,
            ),
        ),
    ]
