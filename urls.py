from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Home
    path("", views.home_view, name="home"),

    # Films
    path("films/", views.film_list_view, name="film_list"),
    path("films/<int:film_id>/", views.film_detail_view, name="film_detail"),

    # Reviews
    path("films/<int:film_id>/review/add/", views.add_review_view, name="add_review"),
    path("reviews/<int:review_id>/edit/", views.edit_review_view, name="edit_review"),
    path("reviews/<int:review_id>/delete/", views.delete_review_view, name="delete_review"),

    # Watchlist
    path("watchlist/", views.watchlist_view, name="watchlist"),
    path("watchlist/add/<int:film_id>/", views.watchlist_add_view, name="watchlist_add"),
    path("watchlist/remove/<int:film_id>/", views.watchlist_remove_view, name="watchlist_remove"),

    # Profile
    path("profile/", views.profile_view, name="profile"),
]
