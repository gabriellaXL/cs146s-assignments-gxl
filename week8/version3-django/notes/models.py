from django.db import models
from django.urls import reverse


class Note(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        BLOCKED = "blocked", "Blocked"
        ARCHIVED = "archived", "Archived"

    title = models.CharField(max_length=120)
    content = models.TextField()
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-created_at", "-id"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("notes:detail", kwargs={"pk": self.pk})
