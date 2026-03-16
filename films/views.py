from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Count, OuterRef, Subquery
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.conf import settings
from .models import Film, Mood, ReviewEntry, WatchlistItem
from .forms import RegisterForm, ReviewForm



# ─────────────────────────────────────────
# Auth views
# ─────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to MoodFlix, {user.username}!")
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get("next", "home"))
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")


# ─────────────────────────────────────────
# Home
# ─────────────────────────────────────────

def home_view(request):
    films = Film.objects.all()[:8]
    moods = Mood.objects.all()

    recent_reviews = []
    if request.user.is_authenticated:
        recent_reviews = (
            ReviewEntry.objects.filter(user=request.user)
            .select_related("film", "mood")
            .order_by("-watched_at")[:5]
        )

    return render(request, "films/home.html", {
        "films": films,
        "moods": moods,
        "recent_reviews": recent_reviews,
        "query": "",
        "mood_id": "",
    })

def film_search(request):
    query = request.GET.get("q", "").lower()
    mood_id = request.GET.get("mood_id", "").strip()
    films = Film.objects.all()

    # search by title
    if query:
        films = films.filter(title__icontains=query)

    # search using mood button
    if mood_id:
        top_mood_subquery = (
            ReviewEntry.objects.filter(film=OuterRef('pk'))
            .values('film')
            .annotate(top_mood_count = Count('mood'))
            .order_by('-top_mood_count', 'mood')
            .values('mood')[:1]
        )
        films = films.annotate(top_mood=Subquery(top_mood_subquery)).filter(top_mood=mood_id) 

    film_list = [
        {
            "pk": film.pk,
            "fields": {
                "title": film.title,
                "release_year": film.release_year,
                "genre": film.genre
            }
        }
        for film in films
    ]

    return JsonResponse({"films": film_list})

# ─────────────────────────────────────────
# Film views
# ─────────────────────────────────────────

def film_detail_view(request, film_id):
    film = get_object_or_404(Film, pk=film_id)
    reviews = ReviewEntry.objects.filter(film=film).select_related("user", "mood").order_by("-watched_at")

    in_watchlist = False
    user_reviews = []
    if request.user.is_authenticated:
        in_watchlist = WatchlistItem.objects.filter(user=request.user, film=film).exists()
        user_reviews = reviews.filter(user=request.user)

    return render(request, "films/film_detail.html", {
        "film": film,
        "reviews": reviews,
        "user_reviews": user_reviews,
        "in_watchlist": in_watchlist,
    })


# ─────────────────────────────────────────
# Review views
# ─────────────────────────────────────────

@login_required
def add_review_view(request, film_id):
    film = get_object_or_404(Film, pk=film_id)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.film = film
            review.save()
            messages.success(request, "Review logged!")
            return redirect("film_detail", film_id=film.pk)
    else:
        form = ReviewForm()
    return render(request, "films/review_form.html", {
        "form": form,
        "film": film,
        "action": "Add",
    })


@login_required
def edit_review_view(request, review_id):
    review = get_object_or_404(ReviewEntry, pk=review_id, user=request.user)
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review updated!")
            return redirect("profile")
    else:
        # Pre-fill datetime-local field
        initial = {"watched_at": review.watched_at.strftime("%Y-%m-%dT%H:%M")}
        form = ReviewForm(instance=review, initial=initial)
    return render(request, "films/review_form.html", {
        "form": form,
        "film": review.film,
        "action": "Edit",
        "review": review,
    })


@login_required
def delete_review_view(request, review_id):
    review = get_object_or_404(ReviewEntry, pk=review_id, user=request.user)
    review.delete()
    messages.success(request, "Review deleted.")
    return redirect("profile")


# ─────────────────────────────────────────
# Watchlist views
# ─────────────────────────────────────────

@login_required
def watchlist_view(request):
    items = WatchlistItem.objects.filter(user=request.user).select_related("film").order_by("-added_at")
    return render(request, "films/watchlist.html", {"items": items})


@login_required
@require_POST
def watchlist_add_view(request, film_id):
    film = get_object_or_404(Film, pk=film_id)
    WatchlistItem.objects.get_or_create(user=request.user, film=film)
    messages.success(request, f'"{film.title}" added to your watchlist.')
    return redirect("film_detail", film_id=film.pk)


@login_required
@require_POST
def watchlist_remove_view(request, film_id):
    film = get_object_or_404(Film, pk=film_id)
    WatchlistItem.objects.filter(user=request.user, film=film).delete()
    messages.info(request, f'"{film.title}" removed from your watchlist.')
    next_url = request.POST.get("next", "")
    return redirect(next_url if next_url else "watchlist")


# ─────────────────────────────────────────
# Profile view
# ─────────────────────────────────────────

@login_required
def profile_view(request):
    mood_id = request.GET.get("mood_id", "").strip()
    reviews = ReviewEntry.objects.filter(user=request.user).select_related("film", "mood")
    if mood_id:
        reviews = reviews.filter(mood__id=mood_id)

    moods = Mood.objects.all()

    # Simple stats (C1 - Could Have)
    mood_stats = (
        ReviewEntry.objects.filter(user=request.user)
        .values("mood__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    top_mood = mood_stats.first() if mood_stats else None

    return render(request, "films/profile.html", {
        "reviews": reviews,
        "moods": moods,
        "mood_id": mood_id,
        "mood_stats": mood_stats,
        "top_mood": top_mood,
    })
