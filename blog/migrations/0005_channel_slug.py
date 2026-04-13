# Generated migration

from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
	"""Populate slug field for all existing channels."""
	Channel = apps.get_model('blog', 'Channel')
	for channel in Channel.objects.all():
		base_slug = slugify(channel.name)
		slug = base_slug
		counter = 1
		# Check for existing slugs for this owner
		while Channel.objects.filter(owner=channel.owner, slug=slug).exclude(pk=channel.pk).exists():
			slug = f"{base_slug}-{counter}"
			counter += 1
		# Update the slug directly without triggering save()
		Channel.objects.filter(pk=channel.pk).update(slug=slug)


def reverse_populate_slugs(apps, schema_editor):
	"""Reverse operation: clear slug field."""
	Channel = apps.get_model('blog', 'Channel')
	Channel.objects.all().update(slug='')


class Migration(migrations.Migration):

	dependencies = [
		('blog', '0004_channel_description'),
	]

	operations = [
		migrations.AddField(
			model_name='channel',
			name='slug',
			field=models.SlugField(default='', max_length=100),
		),
		migrations.RunPython(populate_slugs, reverse_populate_slugs),
		migrations.AddConstraint(
			model_name='channel',
			constraint=models.UniqueConstraint(fields=['owner', 'slug'], name='unique_channel_slug_per_owner'),
		),
	]
