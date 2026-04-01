import random
from django.db import models
from django.utils.text import slugify
from django_countries.fields import CountryField
from django.contrib.auth import get_user_model

class BusinessDetails(models.Model):
    business_name     = models.CharField(max_length=255)
    slug              = models.SlugField(max_length=255, unique=True, blank=True)
    category          = models.CharField(max_length=100, default='')
    country           = CountryField()
    city              = models.CharField(max_length=100)
    postal_code       = models.CharField(max_length=20, blank=True, default='')
    post_office_box   = models.PositiveIntegerField(blank=True, null=True)
    short_description = models.CharField(max_length=255, blank=True, default='')
    long_description  = models.TextField(blank=True, default='')
    created_on        = models.DateTimeField(auto_now_add=True)
    updated_on        = models.DateTimeField(auto_now=True)
    created_by        = models.ForeignKey(
                            get_user_model(),
                            on_delete=models.SET_NULL,
                            null=True,
                            blank=True,
                            related_name='businesses',
                        )

    def _generate_unique_slug(self):
        """Generate a slug, retrying on collision until one is unique."""
        base_slug = slugify(self.business_name)
        for _ in range(10):
            candidate = f"{base_slug}-{random.randint(1000, 9999)}"
            if not BusinessDetails.objects.filter(slug=candidate).exists():
                return candidate
        import uuid
        return f"{base_slug}-{uuid.uuid4().hex[:8]}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.business_name

    class Meta:
        verbose_name        = 'Business'
        verbose_name_plural = 'Businesses'
        ordering            = ['-created_on']
