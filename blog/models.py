from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", null=True, blank=True)
	country = models.CharField(max_length=100, blank=True)
	city = models.CharField(max_length=100, blank=True)
	postal_code = models.CharField(max_length=20, blank=True)
	post_office_box = models.CharField(max_length=50, blank=True)
	about_me = models.TextField(blank=True)

	def __str__(self):
		if self.user_id:
			return f"Profile of {self.user.username}"
		return f"{self.city}, {self.country}"


class Channel(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="channels")
	name = models.CharField(max_length=100)
	intro = models.CharField(max_length=255, blank=True)
	description = models.TextField(blank=True)
	slug = models.SlugField(max_length=100, default='')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["owner", "name"], name="unique_channel_name_per_owner"),
			models.UniqueConstraint(fields=["owner", "slug"], name="unique_channel_slug_per_owner"),
		]
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.name} ({self.owner})"

	def get_absolute_url(self):
		return reverse("blog:channel-detail", kwargs={"channel_slug": self.slug})

	def clean(self):
		super().clean()
		if self.pk is None and self.owner_id:
			channels_count = Channel.objects.filter(owner_id=self.owner_id).count()
			if channels_count >= 10:
				raise ValidationError({"name": "A user can have a maximum of 10 channels."})

	def save(self, *args, **kwargs):
		is_new = self.pk is None
		if not self.slug:
			base_slug = slugify(self.name)
			slug = base_slug
			counter = 1
			while Channel.objects.filter(owner=self.owner, slug=slug).exclude(pk=self.pk).exists():
				slug = f"{base_slug}-{counter}"
				counter += 1
			self.slug = slug
		self.full_clean()
		result = super().save(*args, **kwargs)
		if is_new and self.owner_id:
			ChannelFollow.objects.get_or_create(follower=self.owner, channel=self)
		return result


class ChannelFollow(models.Model):
	follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="channel_follows")
	channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="followers")
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["follower", "channel"], name="unique_follower_channel_pair"),
		]
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.follower} follows {self.channel}"

	def clean(self):
		super().clean()

	def save(self, *args, **kwargs):
		self.full_clean()
		return super().save(*args, **kwargs)


class Post(models.Model):
	channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="posts")
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
	title = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200)
	body = models.TextField()
	image = models.ImageField(upload_to="post_images/", blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["channel", "slug"], name="unique_post_slug_per_channel"),
		]
		ordering = ["-created_at"]

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse(
			"blog:post-detail",
			kwargs={"channel_slug": self.channel.slug, "post_slug": self.slug},
		)

	def clean(self):
		super().clean()
		if self.pk is None and self.channel_id:
			post_count = Post.objects.filter(channel_id=self.channel_id).count()
			if post_count >= 100:
				raise ValidationError({"channel": "A channel can have a maximum of 100 posts."})

	def save(self, *args, **kwargs):
		if not self.slug:
			base_slug = slugify(self.title) or "post"
			slug = base_slug
			counter = 1
			while Post.objects.filter(channel=self.channel, slug=slug).exclude(pk=self.pk).exists():
				slug = f"{base_slug}-{counter}"
				counter += 1
			self.slug = slug
		self.full_clean()
		return super().save(*args, **kwargs)


class Comment(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
	body = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["post", "author"], name="unique_comment_per_user_per_post"),
		]
		ordering = ["-created_at"]

	def __str__(self):
		return f"Comment by {self.author} on {self.post}"

	def save(self, *args, **kwargs):
		self.full_clean()
		return super().save(*args, **kwargs)
