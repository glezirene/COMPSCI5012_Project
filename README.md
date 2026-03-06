# MoodFlix – Backend Setup

## Quick start (new branch)

```bash
# 1. Clone and switch to your backend branch
git checkout -b backend-implementation

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install Django
pip install django

# 4. Run migrations
python manage.py makemigrations films
python manage.py migrate

# 5. Load seed data (moods + sample films)
python manage.py loaddata films/fixtures/moods.json
python manage.py loaddata films/fixtures/films.json

# 6. Create a superuser (for /admin)
python manage.py createsuperuser

# 7. Run the dev server
python manage.py runserver
```

Visit http://127.0.0.1:8000/

---

## File structure

```
moodflix/                  ← Django project root
├── manage.py
├── moodflix/
│   ├── settings.py
│   └── urls.py
├── films/
│   ├── models.py          ← Film, Mood, ReviewEntry, WatchlistItem
│   ├── views.py           ← All views
│   ├── forms.py           ← RegisterForm, ReviewForm
│   ├── urls.py            ← Named URL patterns
│   ├── admin.py           ← Admin registrations
│   └── fixtures/
│       ├── moods.json     ← Pre-loads Happy/Sad/Anxious/Nostalgic/Excited/Scared
│       └── films.json     ← 10 sample films
└── templates/
    ├── base.html          ← Shared layout (dark MoodFlix theme)
    ├── films/
    │   ├── home.html
    │   ├── film_list.html
    │   ├── film_detail.html
    │   ├── review_form.html        ← Used for add AND edit
    │   ├── review_confirm_delete.html
    │   ├── watchlist.html
    │   └── profile.html
    └── registration/
        ├── login.html
        └── register.html
```

---

## URL map

| Name               | URL                                     | Auth required |
|--------------------|-----------------------------------------|---------------|
| `home`             | `/`                                     | No            |
| `register`         | `/register/`                            | No            |
| `login`            | `/login/`                               | No            |
| `logout`           | `/logout/`                              | POST only     |
| `film_list`        | `/films/?q=...&mood_id=...`             | No            |
| `film_detail`      | `/films/<id>/`                          | No            |
| `add_review`       | `/films/<id>/review/add/`               | Yes           |
| `edit_review`      | `/reviews/<id>/edit/`                   | Yes           |
| `delete_review`    | `/reviews/<id>/delete/`                 | Yes           |
| `watchlist`        | `/watchlist/`                           | Yes           |
| `watchlist_add`    | `/watchlist/add/<film_id>/`             | Yes, POST     |
| `watchlist_remove` | `/watchlist/remove/<film_id>/`          | Yes, POST     |
| `profile`          | `/profile/?mood_id=...`                 | Yes           |


## Query parameters and state-changing actions

- Film search uses `?q=...`
- Mood filtering uses `?mood_id=...`
- Logout is handled via `POST`
- Watchlist add/remove are handled via `POST`

---

## MoSCoW coverage

- ✅ M1 Register / login (Django auth)
- ✅ M2 Browse film list + film detail
- ✅ M3 Log a review (rating 1-5, mood, review text, watched_at)
- ✅ M4 Profile page with review list
- ✅ M5 Watchlist add/remove
- ✅ S1 Filter reviews by mood (profile page + film list)
- ✅ S2 Search films by title (?q= param)
- ✅ S3 Edit / delete a review
- ✅ C1 Mood stats on profile page (most common mood + counts)
