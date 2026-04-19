from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        null=True,
        blank=True,
    )
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    post_office_box = models.CharField(max_length=50, blank=True)
    about_me = models.TextField(blank=True)
    profile_locked = models.BooleanField(default=False, help_text="If true, profile is hidden from public view.")
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

