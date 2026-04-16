from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
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
	email_digest_enabled = models.BooleanField(default=True)
	digest_weekday = models.PositiveSmallIntegerField(
		default=0,
		validators=[MinValueValidator(0), MaxValueValidator(6)],
	)
	digest_hour = models.PositiveSmallIntegerField(
		default=9,
		validators=[MinValueValidator(0), MaxValueValidator(23)],
	)
	last_digest_sent_at = models.DateTimeField(null=True, blank=True)

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


class UserFollow(models.Model):
	follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_following")
	following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_followers")
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["follower", "following"], name="unique_user_follow_pair"),
		]
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.follower} follows user {self.following}"


class Tag(models.Model):
	name = models.CharField(max_length=50, unique=True)
	slug = models.SlugField(max_length=50, unique=True)

	class Meta:
		ordering = ["name"]

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		return super().save(*args, **kwargs)


class Post(models.Model):
	channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="posts")
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
	title = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200)
	body = models.TextField()
	image = models.ImageField(upload_to="post_images/", blank=True, null=True)
	tags = models.ManyToManyField("Tag", related_name="posts", blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["channel", "slug"], name="unique_post_slug_per_channel"),
		]
		ordering = ["-created_at"]

	def __str__(self):
		return self.title

	@property
	def image_exists(self):
		if not self.image:
			return False
		try:
			return self.image.storage.exists(self.image.name)
		except Exception:
			return False

	@property
	def reading_time_minutes(self):
		# Estimate reading time at 200 words per minute, minimum 1 minute.
		word_count = len(self.body.split())
		return max(1, (word_count + 199) // 200)

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


class SavedPost(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_posts")
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="saved_by")
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["user", "post"], name="unique_saved_post_per_user"),
		]
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.user} saved {self.post}"

	def save(self, *args, **kwargs):
		self.full_clean()
		return super().save(*args, **kwargs)


class Notification(models.Model):
	TYPE_FOLLOW = "follow"
	TYPE_NEW_POST = "new_post"
	TYPE_COMMENT = "comment"
	TYPE_CHOICES = (
		(TYPE_FOLLOW, "New follower"),
		(TYPE_NEW_POST, "New post"),
		(TYPE_COMMENT, "New comment"),
	)

	recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
	actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications_sent")
	notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
	message = models.CharField(max_length=255)
	target_url = models.CharField(max_length=255, blank=True)
	is_read = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"Notification to {self.recipient} from {self.actor}: {self.message}"


class PostReaction(models.Model):
	LOVE = "love"
	REACTION_CHOICES = ((LOVE, "Love"),)

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_reactions")
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reactions")
	reaction = models.CharField(max_length=20, choices=REACTION_CHOICES, default=LOVE)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["user", "post", "reaction"], name="unique_reaction_per_user_per_post"),
		]
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.user} reacted {self.reaction} to {self.post}"

	def save(self, *args, **kwargs):
		self.full_clean()
		return super().save(*args, **kwargs)


class CommentReaction(models.Model):
	LOVE = "love"
	REACTION_CHOICES = ((LOVE, "Love"),)

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_reactions")
	comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="reactions")
	reaction = models.CharField(max_length=20, choices=REACTION_CHOICES, default=LOVE)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["user", "comment", "reaction"], name="unique_reaction_per_user_per_comment"),
		]
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.user} reacted {self.reaction} to {self.comment}"

	def save(self, *args, **kwargs):
		self.full_clean()
		return super().save(*args, **kwargs)
