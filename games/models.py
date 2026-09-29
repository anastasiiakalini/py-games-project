from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.template.defaultfilters import slugify
from django.urls import reverse


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Developer(AbstractUser):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="developers",
    )

    website = models.URLField()

    def __str__(self):
        return f"{self.username}"

    def get_absolute_url(self):
        return reverse("games:developer-detail", kwargs={"pk": self.pk})


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Game(models.Model):
    name = models.CharField(max_length=100, unique=True)

    description = models.TextField()

    price = models.DecimalField(
        decimal_places=2, max_digits=10, validators=[MinValueValidator(0)]
    )

    genre = models.ManyToManyField(
        Genre,
        related_name="games",
    )

    developer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="games",
    )

    def __str__(self):
        return f"{self.name} ({self.developer.name})"
