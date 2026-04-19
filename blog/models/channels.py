from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Channel(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="channels")
    name = models.CharField(max_length=100)
    intro = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    is_suspended = models.BooleanField(default=False)
    suspended_until = models.DateTimeField(null=True, blank=True)
    suspension_reason = models.CharField(max_length=255, blank=True)
    comments_enabled = models.BooleanField(default=True)
    slug = models.SlugField(max_length=100, default="")
    visibility = models.CharField(
        max_length=20,
        choices=[
            ("public", "Public"),
            ("private", "Private (only admins)"),
            ("restricted", "Restricted (selected users)"),
        ],
        default="public",
    )
    allowed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="allowed_channels",
        help_text="Users allowed to view this channel if restricted.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    follower_count = models.PositiveIntegerField(default=0, db_index=True)
    posts_count = models.PositiveIntegerField(default=0)

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


class ChannelMembership(models.Model):
    ROLE_CHOICES = [
        ("creator", "Creator"),
        ("admin", "Admin"),
        ("viewer", "Viewer"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="channel_memberships")
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="viewer")
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="channel_invitations_sent",
    )
    invited_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "channel")

    def __str__(self):
        return f"{self.user.username} in {self.channel.name} as {self.role}"


class ChannelFollow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="channel_follows")
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


class ChannelEditor(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="editors")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="editor_channels")
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="editor_invites_sent")
    accepted = models.BooleanField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["channel", "user"], name="unique_channel_editor"),
        ]
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user} editor of {self.channel}"

