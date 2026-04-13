from django.db import migrations


def create_owner_follows(apps, schema_editor):
    Channel = apps.get_model("blog", "Channel")
    ChannelFollow = apps.get_model("blog", "ChannelFollow")

    for channel in Channel.objects.select_related("owner"):
        ChannelFollow.objects.get_or_create(
            follower_id=channel.owner_id,
            channel_id=channel.id,
        )


def remove_owner_follows(apps, schema_editor):
    Channel = apps.get_model("blog", "Channel")
    ChannelFollow = apps.get_model("blog", "ChannelFollow")

    for channel in Channel.objects.all():
        ChannelFollow.objects.filter(
            follower_id=channel.owner_id,
            channel_id=channel.id,
        ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0006_channel_intro"),
    ]

    operations = [
        migrations.RunPython(create_owner_follows, remove_owner_follows),
    ]
