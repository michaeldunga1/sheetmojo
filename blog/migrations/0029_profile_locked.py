from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0028_channelmembership"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="profile_locked",
            field=models.BooleanField(default=False, help_text="If true, profile is hidden from public view."),
        ),
    ]
