from django.conf import settings
from django.db import models


class Calculator(models.Model):
    calculator_name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    tags = models.CharField(max_length=255)
    description = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="calculators",
    )

    class Meta:
        db_table = "calculator"
        ordering = ["-created_on"]

    def __str__(self) -> str:
        return self.calculator_name

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]
