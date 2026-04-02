from io import BytesIO
import random

from django.db import models
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.urls import reverse
from PIL import Image
from PIL import UnidentifiedImageError

from .business_details import BusinessDetails
from ..currency_data import CURRENCY_CHOICES, CURRENCY_CODES


class Product(models.Model):
    MAX_PRODUCTS_PER_BUSINESS = 10

    @staticmethod
    def normalize_category(category):
        return " ".join((category or "").split()).title()

    class Currency:
        USD = "USD"
        EUR = "EUR"
        GBP = "GBP"
        KES = "KES"
        UGX = "UGX"
        TZS = "TZS"
        NGN = "NGN"
        ZAR = "ZAR"

        choices = CURRENCY_CHOICES
        values = CURRENCY_CODES

    class TermsOfSale(models.TextChoices):
        CASH_ONLY = "cash_only", "Cash Only"
        CASH_OR_CARD = "cash_or_card", "Cash or Card"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        PAY_ON_DELIVERY = "pay_on_delivery", "Pay on Delivery"
        ADVANCE_PAYMENT = "advance_payment", "Advance Payment Required"
        NEGOTIABLE = "negotiable", "Negotiable"

    business = models.ForeignKey(
        BusinessDetails,
        on_delete=models.CASCADE,
        related_name="products",
    )
    product_name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    product_image = models.ImageField(upload_to="products/", blank=True, null=True)
    product_thumbnail = models.ImageField(upload_to="products/thumbnails/", blank=True, null=True)
    product_category = models.CharField(max_length=100)
    tags = models.CharField(max_length=255, default="general")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.USD)
    product_description = models.TextField(default="N/A")
    terms_of_sale = models.CharField(
        max_length=30,
        choices=TermsOfSale.choices,
        default=TermsOfSale.NEGOTIABLE,
    )
    posted_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.product_category = self.normalize_category(self.product_category)
        self.tags = " ".join((self.tags or "").split())
        if self._state.adding and self.business_id:
            existing_count = Product.objects.filter(business_id=self.business_id).count()
            if existing_count >= self.MAX_PRODUCTS_PER_BUSINESS:
                raise ValidationError(
                    f"A business can list up to {self.MAX_PRODUCTS_PER_BUSINESS} products."
                )
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

        if self.product_image:
            thumbnail_name = self._build_thumbnail_name()
            if self.product_thumbnail.name != thumbnail_name:
                self._generate_thumbnail(thumbnail_name)
                Product.objects.filter(pk=self.pk).update(product_thumbnail=self.product_thumbnail.name)

    def _build_thumbnail_name(self):
        return f"products/thumbnails/product_{self.pk}.webp"

    def _generate_thumbnail(self, thumbnail_name):
        self.product_image.open("rb")
        try:
            image = Image.open(self.product_image)
        except (UnidentifiedImageError, OSError):
            self.product_image.close()
            return
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        elif image.mode == "L":
            image = image.convert("RGB")

        image.thumbnail((420, 420))

        thumb_io = BytesIO()
        image.save(thumb_io, format="WEBP", quality=82, method=6)
        self.product_thumbnail.save(
            thumbnail_name,
            ContentFile(thumb_io.getvalue()),
            save=False,
        )

        self.product_image.close()

    def _generate_unique_slug(self):
        base_slug = slugify(self.product_name) or "product"
        for _ in range(10):
            candidate = f"{base_slug}-{random.randint(1000, 9999)}"
            if not Product.objects.filter(slug=candidate).exists():
                return candidate
        import uuid
        return f"{base_slug}-{uuid.uuid4().hex[:8]}"

    def __str__(self):
        return self.product_name

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"slug": self.slug})

    class Meta:
        ordering = ["-posted_on"]
        verbose_name = "Product"
        verbose_name_plural = "Products"