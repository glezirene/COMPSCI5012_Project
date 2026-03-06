from django.contrib import admin
from .models import Film, Mood, ReviewEntry, WatchlistItem


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ["title", "release_year", "genre"]
    search_fields = ["title"]
    list_filter = ["genre", "release_year"]


@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(ReviewEntry)
class ReviewEntryAdmin(admin.ModelAdmin):
    list_display = ["user", "film", "mood", "rating", "watched_at"]
    list_filter = ["mood", "rating"]
    search_fields = ["user__username", "film__title"]


@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = ["user", "film", "added_at"]
    search_fields = ["user__username", "film__title"]
