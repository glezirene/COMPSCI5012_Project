from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from .models import Film, Mood, ReviewEntry, WatchlistItem
from .forms import ReviewForm


# ─────────────────────────────────────────
# Helper
# ─────────────────────────────────────────

def make_user(username="testuser", password="testpass123"):
    return User.objects.create_user(username=username, password=password)


def make_film(title="Test Film", year=2020):
    return Film.objects.create(title=title, release_year=year, genre="Drama")


def make_mood(name="Happy"):
    return Mood.objects.get_or_create(name=name)[0]


# ─────────────────────────────────────────
# Model tests
# ─────────────────────────────────────────

class WatchlistUniquenessTest(TestCase):
    """A user cannot add the same film to their watchlist twice."""

    def test_duplicate_watchlist_raises(self):
        user = make_user()
        film = make_film()
        WatchlistItem.objects.create(user=user, film=film)
        with self.assertRaises(Exception):
            WatchlistItem.objects.create(user=user, film=film)

    def test_different_users_can_watchlist_same_film(self):
        film = make_film()
        user1 = make_user("alice")
        user2 = make_user("bob")
        WatchlistItem.objects.create(user=user1, film=film)
        WatchlistItem.objects.create(user=user2, film=film)
        self.assertEqual(WatchlistItem.objects.filter(film=film).count(), 2)


class ReviewRewatchTest(TestCase):
    """A user CAN log the same film more than once (diary / rewatch behaviour)."""

    def test_multiple_reviews_same_user_same_film(self):
        user = make_user()
        film = make_film()
        mood = make_mood()
        ReviewEntry.objects.create(
            user=user, film=film, mood=mood, rating=4,
            watched_at=timezone.now()
        )
        ReviewEntry.objects.create(
            user=user, film=film, mood=mood, rating=5,
            watched_at=timezone.now()
        )
        self.assertEqual(ReviewEntry.objects.filter(user=user, film=film).count(), 2)


# ─────────────────────────────────────────
# Form tests
# ─────────────────────────────────────────

class ReviewFormValidationTest(TestCase):

    def setUp(self):
        self.mood = make_mood()

    def _base_data(self, rating):
        return {
            "rating": rating,
            "mood": self.mood.pk,
            "watched_at": "2024-01-15T20:00",
            "review_text": "",
        }

    def test_valid_rating_accepted(self):
        for r in range(1, 6):
            form = ReviewForm(data=self._base_data(r))
            self.assertTrue(form.is_valid(), msg=f"Rating {r} should be valid")

    def test_rating_zero_invalid(self):
        form = ReviewForm(data=self._base_data(0))
        self.assertFalse(form.is_valid())

    def test_rating_six_invalid(self):
        form = ReviewForm(data=self._base_data(6))
        self.assertFalse(form.is_valid())

    def test_rating_coerced_to_int(self):
        form = ReviewForm(data=self._base_data(3))
        self.assertTrue(form.is_valid())
        self.assertIsInstance(form.cleaned_data["rating"], int)

    def test_missing_mood_invalid(self):
        data = self._base_data(3)
        data["mood"] = ""
        form = ReviewForm(data=data)
        self.assertFalse(form.is_valid())


# ─────────────────────────────────────────
# View tests
# ─────────────────────────────────────────

class AuthViewTest(TestCase):

    def test_register_get(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_register_creates_user_and_redirects(self):
        response = self.client.post(reverse("register"), {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "Str0ngPass!",
            "password2": "Str0ngPass!",
        })
        self.assertRedirects(response, reverse("home"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_valid(self):
        make_user("alice", "pass1234!")
        response = self.client.post(reverse("login"), {
            "username": "alice",
            "password": "pass1234!",
        })
        self.assertRedirects(response, reverse("home"))

    def test_login_invalid(self):
        response = self.client.post(reverse("login"), {
            "username": "nobody",
            "password": "wrongpass",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid")

    def test_logout_requires_post(self):
        make_user()
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 405)


    def test_logout_post_redirects(self):
    	make_user()
    	self.client.login(username="testuser", password="testpass123")
    	response = self.client.post(reverse("logout"))
    	self.assertRedirects(response, reverse("login"))



class WatchlistViewTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.film = make_film()
        self.client.login(username="testuser", password="testpass123")

    def test_add_watchlist_via_post(self):
        response = self.client.post(reverse("watchlist_add", args=[self.film.pk]))
        self.assertRedirects(response, reverse("film_detail", args=[self.film.pk]))
        self.assertTrue(WatchlistItem.objects.filter(user=self.user, film=self.film).exists())

    def test_add_watchlist_get_rejected(self):
        response = self.client.get(reverse("watchlist_add", args=[self.film.pk]))
        self.assertEqual(response.status_code, 405)

    def test_remove_watchlist_via_post(self):
        WatchlistItem.objects.create(user=self.user, film=self.film)
        self.client.post(reverse("watchlist_remove", args=[self.film.pk]))
        self.assertFalse(WatchlistItem.objects.filter(user=self.user, film=self.film).exists())

    def test_add_duplicate_does_not_raise(self):
        self.client.post(reverse("watchlist_add", args=[self.film.pk]))
        self.client.post(reverse("watchlist_add", args=[self.film.pk]))
        self.assertEqual(WatchlistItem.objects.filter(user=self.user, film=self.film).count(), 1)

    def test_watchlist_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("watchlist"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('watchlist')}")


class ReviewOwnershipTest(TestCase):
    """A user cannot edit or delete another user's review."""

    def setUp(self):
        self.owner = make_user("owner")
        self.other = make_user("other", "otherpass")
        self.film = make_film()
        self.mood = make_mood()
        self.review = ReviewEntry.objects.create(
            user=self.owner, film=self.film, mood=self.mood,
            rating=4, watched_at=timezone.now()
        )

    def test_other_user_cannot_edit_review(self):
        self.client.login(username="other", password="otherpass")
        response = self.client.get(reverse("edit_review", args=[self.review.pk]))
        self.assertEqual(response.status_code, 404)

    def test_other_user_cannot_delete_review(self):
        self.client.login(username="other", password="otherpass")
        response = self.client.post(reverse("delete_review", args=[self.review.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(ReviewEntry.objects.filter(pk=self.review.pk).exists())


class SearchAndFilterTest(TestCase):

    def setUp(self):
        self.film1 = Film.objects.create(title="Inception", release_year=2010, genre="Sci-Fi")
        self.film2 = Film.objects.create(title="The Godfather", release_year=1972, genre="Drama")
        self.mood = make_mood("Nostalgic")
        self.user = make_user()
        ReviewEntry.objects.create(
            user=self.user, film=self.film2, mood=self.mood,
            rating=5, watched_at=timezone.now()
        )

    def test_search_by_title(self):
        response = self.client.get(reverse("film_list") + "?q=inception")
        self.assertContains(response, "Inception")
        self.assertNotContains(response, "The Godfather")

    def test_search_empty_returns_all(self):
        response = self.client.get(reverse("film_list"))
        self.assertContains(response, "Inception")
        self.assertContains(response, "The Godfather")

    def test_mood_filter_by_id(self):
        response = self.client.get(reverse("film_list") + f"?mood_id={self.mood.pk}")
        self.assertContains(response, "The Godfather")
        self.assertNotContains(response, "Inception")



class ProfileFilterTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.client.login(username="testuser", password="testpass123")

        self.film1 = Film.objects.create(title="Inception", release_year=2010, genre="Sci-Fi")
        self.film2 = Film.objects.create(title="The Godfather", release_year=1972, genre="Drama")

        self.mood1 = make_mood("Nostalgic")
        self.mood2 = make_mood("Happy")

        ReviewEntry.objects.create(
            user=self.user,
            film=self.film1,
            mood=self.mood1,
            rating=5,
            watched_at=timezone.now()
        )
        ReviewEntry.objects.create(
            user=self.user,
            film=self.film2,
            mood=self.mood2,
            rating=4,
            watched_at=timezone.now()
        )

    def test_profile_mood_filter_by_id(self):
        response = self.client.get(reverse("profile") + f"?mood_id={self.mood1.pk}")
        self.assertContains(response, "Inception")
        self.assertNotContains(response, "The Godfather")
