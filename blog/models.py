from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

User = get_user_model()


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", null=True, blank=True)
	country = models.CharField(max_length=100, blank=True)
	city = models.CharField(max_length=100, blank=True)
	postal_code = models.CharField(max_length=20, blank=True)
	post_office_box = models.CharField(max_length=50, blank=True)
	about_me = models.TextField(blank=True)
	is_suspended = models.BooleanField(default=False)
	suspended_until = models.DateTimeField(null=True, blank=True)
	suspension_reason = models.CharField(max_length=255, blank=True)
	commenting_restricted_until = models.DateTimeField(null=True, blank=True)
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

	@property
	def is_currently_suspended(self):
		if not self.is_suspended:
			return False
		if self.suspended_until and self.suspended_until <= timezone.now():
			return False
		return True

	@property
	def is_commenting_restricted(self):
		if not self.commenting_restricted_until:
			return False
		return self.commenting_restricted_until > timezone.now()


class Channel(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="channels")
	name = models.CharField(max_length=100)
	intro = models.CharField(max_length=255, blank=True)
	description = models.TextField(blank=True)
	is_suspended = models.BooleanField(default=False)
	suspended_until = models.DateTimeField(null=True, blank=True)
	suspension_reason = models.CharField(max_length=255, blank=True)
	comments_enabled = models.BooleanField(default=True)
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

	@property
	def is_currently_suspended(self):
		if not self.is_suspended:
			return False
		if self.suspended_until and self.suspended_until <= timezone.now():
			return False
		return True

	follower_count = models.PositiveIntegerField(default=0, db_index=True)
	posts_count = models.PositiveIntegerField(default=0)

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


class UserBlock(models.Model):
	blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocks_made")
	blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocks_received")
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["blocker", "blocked"], name="unique_user_block_pair"),
		]
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.blocker} blocked {self.blocked}"


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
	is_published = models.BooleanField(default=True, db_index=True)
	published_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	view_count = models.PositiveIntegerField(default=0, db_index=True)
	love_count = models.PositiveIntegerField(default=0, db_index=True)
	comment_count = models.PositiveIntegerField(default=0, db_index=True)
	saves_count = models.PositiveIntegerField(default=0)

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
		if self.is_published and not self.published_at:
			self.published_at = timezone.now()
		if not self.is_published:
			self.published_at = None
		self.full_clean()
		return super().save(*args, **kwargs)


class Comment(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
	body = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	love_count = models.PositiveIntegerField(default=0)

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
	TYPE_COAUTHOR_INVITE = "coauthor_invite"
	TYPE_COAUTHOR_ACCEPTED = "coauthor_accepted"
	TYPE_EDITOR_INVITE = "editor_invite"
	TYPE_EDITOR_ACCEPTED = "editor_accepted"
	TYPE_CHOICES = (
		(TYPE_FOLLOW, "New follower"),
		(TYPE_NEW_POST, "New post"),
		(TYPE_COMMENT, "New comment"),
		(TYPE_COAUTHOR_INVITE, "Co-author invite"),
		(TYPE_COAUTHOR_ACCEPTED, "Co-author accepted"),
		(TYPE_EDITOR_INVITE, "Editor invite"),
		(TYPE_EDITOR_ACCEPTED, "Editor accepted"),
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


class Report(models.Model):
	CONTENT_POST = "post"
	CONTENT_COMMENT = "comment"
	CONTENT_CHANNEL = "channel"
	CONTENT_USER = "user"
	CONTENT_CHOICES = (
		(CONTENT_POST, "Post"),
		(CONTENT_COMMENT, "Comment"),
		(CONTENT_CHANNEL, "Channel"),
		(CONTENT_USER, "User"),
	)

	REASON_SPAM = "spam"
	REASON_ABUSE = "abuse"
	REASON_HARASSMENT = "harassment"
	REASON_MISINFORMATION = "misinformation"
	REASON_ILLEGAL = "illegal"
	REASON_OTHER = "other"
	REASON_CHOICES = (
		(REASON_SPAM, "Spam"),
		(REASON_ABUSE, "Abusive content"),
		(REASON_HARASSMENT, "Harassment"),
		(REASON_MISINFORMATION, "Misinformation"),
		(REASON_ILLEGAL, "Illegal content"),
		(REASON_OTHER, "Other"),
	)

	STATUS_PENDING = "pending"
	STATUS_REVIEWED = "reviewed"
	STATUS_RESOLVED = "resolved"
	STATUS_CHOICES = (
		(STATUS_PENDING, "Pending"),
		(STATUS_REVIEWED, "Reviewed"),
		(STATUS_RESOLVED, "Resolved"),
	)

	reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="reports_submitted")
	content_type = models.CharField(max_length=20, choices=CONTENT_CHOICES)
	post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name="reports")
	comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name="reports")
	channel = models.ForeignKey(Channel, on_delete=models.CASCADE, null=True, blank=True, related_name="reports")
	reported_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="reports_received")
	reason = models.CharField(max_length=20, choices=REASON_CHOICES)
	description = models.TextField()
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
	admin_notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	reviewed_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ["-created_at"]
		constraints = [
			models.UniqueConstraint(fields=["reporter", "post"], condition=models.Q(post__isnull=False), name="unique_report_per_reporter_post"),
			models.UniqueConstraint(fields=["reporter", "comment"], condition=models.Q(comment__isnull=False), name="unique_report_per_reporter_comment"),
			models.UniqueConstraint(fields=["reporter", "channel"], condition=models.Q(channel__isnull=False), name="unique_report_per_reporter_channel"),
			models.UniqueConstraint(fields=["reporter", "reported_user"], condition=models.Q(reported_user__isnull=False), name="unique_report_per_reporter_user"),
		]

	def __str__(self):
		return f"Report on {self.content_type} by {self.reporter} ({self.reason})"


class PostCoAuthor(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="co_authors")
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coauthored_posts")
	invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coauthor_invites_sent")
	accepted = models.BooleanField(null=True, default=None)  # None=pending, True=accepted, False=declined
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["post", "user"], name="unique_post_coauthor"),
		]
		ordering = ["created_at"]

	def __str__(self):
		return f"{self.user} co-authors {self.post}"


class ChannelEditor(models.Model):
	channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="editors")
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="editor_channels")
	invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="editor_invites_sent")
	accepted = models.BooleanField(null=True, default=None)  # None=pending, True=accepted, False=declined
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["channel", "user"], name="unique_channel_editor"),
		]
		ordering = ["created_at"]

	def __str__(self):

		return f"{self.user} editor of {self.channel}"


class Contact(models.Model):
	name = models.CharField(max_length=255)
	email = models.EmailField()
	message = models.TextField()
	received_at = models.DateTimeField(auto_now_add=True)
	read = models.BooleanField(default=False)

	class Meta:
		ordering = ["-received_at"]

	def __str__(self):
		return f"Contact from {self.name} ({self.email})"


class NewsletterSubscription(models.Model):
	email = models.EmailField(unique=True)
	is_active = models.BooleanField(default=True)
	subscribed_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-subscribed_at"]

	def __str__(self):
		status = "active" if self.is_active else "inactive"
		return f"{self.email} ({status})"
