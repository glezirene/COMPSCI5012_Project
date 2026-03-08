from django.contrib import admin
from .models import Film, Mood, ReviewEntry, WatchlistItem

admin.site.register(Film)
admin.site.register(Mood)
admin.site.register(ReviewEntry)
admin.site.register(WatchlistItem)


# Register your models here.
