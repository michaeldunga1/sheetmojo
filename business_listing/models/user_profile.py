
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django_countries.fields import CountryField

class UserProfile(models.Model):
    """
    Extended profile information for users.
    One-to-one relationship with the default User model.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    about_me = models.TextField(
        blank=True,
        verbose_name="About Me",
        help_text="Tell others a little bit about yourself or your business experience."
    )
    country = CountryField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, default='')
    postal_code = models.CharField(max_length=20, blank=True, default='')
    post_office_box = models.PositiveIntegerField(blank=True, null=True)

    # You can add more fields later, for example:
    # phone = models.CharField(max_length=20, blank=True)
    # profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    # website = models.URLField(blank=True)
    # joined_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['user__username']

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def username(self):
        """Convenience property for templates"""
        return self.user.username