from django.db import migrations, models
from django.utils.text import slugify


def populate_post_slugs(apps, schema_editor):
    Post = apps.get_model("blog", "Post")

    for post in Post.objects.all().order_by("id"):
        base_slug = slugify(post.title) or "post"
        slug = base_slug
        counter = 1

        while Post.objects.filter(channel_id=post.channel_id, slug=slug).exclude(pk=post.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        post.slug = slug
        post.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0009_profile_user_alter_profile_city_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="slug",
            field=models.SlugField(blank=True, default="", max_length=200),
        ),
        migrations.RunPython(populate_post_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="post",
            name="slug",
            field=models.SlugField(max_length=200),
        ),
        migrations.AddConstraint(
            model_name="post",
            constraint=models.UniqueConstraint(fields=("channel", "slug"), name="unique_post_slug_per_channel"),
        ),
    ]
