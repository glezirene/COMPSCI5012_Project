from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Film(models.Model):
    title = models.CharField(max_length=200)
    release_year = models.IntegerField()
    genre = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.release_year})"


class Mood(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ReviewEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name="reviews")
    mood = models.ForeignKey(Mood, on_delete=models.PROTECT, related_name="reviews")

    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review_text = models.TextField(blank=True)
    watched_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-watched_at"]

    def __str__(self):
        return f"{self.user} - {self.film} ({self.rating}★)"


class WatchlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist_items")
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name="watchlist_items")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "film"], name="unique_watchlist")
        ]
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user} - {self.film}"
