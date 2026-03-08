from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Film(models.Model):
    title = models.CharField(max_length=200)
    release_year = models.IntegerField()
    genre = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} ({self.release_year})"


class Mood(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class ReviewEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    mood = models.ForeignKey(Mood, on_delete=models.PROTECT)

    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review_text = models.TextField(blank=True)
    watched_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user} - {self.film}"


class WatchlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "film"], name="unique_watchlist")
        ]

    def __str__(self):
        return f"{self.user} - {self.film}"

