from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ReviewEntry, Mood


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [(i, "★" * i) for i in range(1, 6)]

    rating = forms.TypedChoiceField(
        choices=RATING_CHOICES,
        coerce=int,
        widget=forms.RadioSelect(attrs={"class": "star-radio"}),
    )
    watched_at = forms.DateField(
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control"}
        ),
        input_formats=["%Y-%m-%d"],
    )

    class Meta:
        model = ReviewEntry
        fields = ["rating", "review_text", "mood", "watched_at"]
        widgets = {
            "review_text": forms.Textarea(
                attrs={"class": "form-control", "rows": 5, "placeholder": "Write your review..."}
            ),
            "mood": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["mood"].queryset = Mood.objects.all()
        self.fields["mood"].empty_label = "Select a mood..."
        self.fields["review_text"].required = False
