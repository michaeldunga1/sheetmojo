from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from .channels import Channel


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
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    body = models.TextField()
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)
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
        word_count = len(self.body.split())
        return max(1, (word_count + 199) // 200)

    def get_absolute_url(self):
        return reverse("blog:post-detail", kwargs={"channel_slug": self.channel.slug, "post_slug": self.slug})

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
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_posts")
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


class PostCoAuthor(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="co_authors")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coauthored_posts")
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coauthor_invites_sent")
    accepted = models.BooleanField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["post", "user"], name="unique_post_coauthor"),
        ]
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user} co-authors {self.post}"

