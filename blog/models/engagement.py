from django.conf import settings
from django.db import models

from .channels import Channel
from .content import Comment, Post


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

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications_sent")
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

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="post_reactions")
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

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comment_reactions")
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

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="reports_submitted")
    content_type = models.CharField(max_length=20, choices=CONTENT_CHOICES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name="reports")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name="reports")
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, null=True, blank=True, related_name="reports")
    reported_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="reports_received")
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

