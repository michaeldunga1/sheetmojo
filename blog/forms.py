from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Channel, Comment, Post, Profile, Tag

User = get_user_model()

WEEKDAY_CHOICES = (
    (0, "Monday"),
    (1, "Tuesday"),
    (2, "Wednesday"),
    (3, "Thursday"),
    (4, "Friday"),
    (5, "Saturday"),
    (6, "Sunday"),
)

DIGEST_HOUR_CHOICES = [(hour, f"{hour:02d}:00") for hour in range(24)]


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Email or username",
        help_text="Use the email you registered with or your username.",
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "autocomplete": "username",
                "placeholder": "name@example.com or username",
                "spellcheck": "false",
            }
        ),
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields["password"].widget.attrs.update(
            {
                "autocomplete": "current-password",
                "placeholder": "Password",
            }
        )


class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = ["name", "intro", "description"]


class PostForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        label="Tags",
        help_text="Comma-separated tags, e.g. python, django, webdev",
        widget=forms.TextInput(attrs={"placeholder": "python, django, webdev"}),
    )

    class Meta:
        model = Post
        fields = ["title", "body", "image", "tags_input"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            existing = ", ".join(self.instance.tags.values_list("name", flat=True))
            self.fields["tags_input"].initial = existing

    def get_tag_names(self):
        raw = self.cleaned_data.get("tags_input", "")
        names = [t.strip().lower() for t in raw.split(",") if t.strip()]
        return names[:10]  # cap at 10 tags per post


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if not email:
            return email
        qs = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


class ProfileEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["digest_weekday"].required = False
        self.fields["digest_hour"].required = False

    def clean_digest_weekday(self):
        value = self.cleaned_data.get("digest_weekday")
        if value in (None, ""):
            if self.instance and self.instance.pk:
                return self.instance.digest_weekday
            return Profile._meta.get_field("digest_weekday").default
        return value

    def clean_digest_hour(self):
        value = self.cleaned_data.get("digest_hour")
        if value in (None, ""):
            if self.instance and self.instance.pk:
                return self.instance.digest_hour
            return Profile._meta.get_field("digest_hour").default
        return value

    class Meta:
        model = Profile
        fields = [
            "country",
            "city",
            "postal_code",
            "post_office_box",
            "about_me",
            "email_digest_enabled",
            "digest_weekday",
            "digest_hour",
        ]
        widgets = {
            "digest_weekday": forms.Select(choices=WEEKDAY_CHOICES),
            "digest_hour": forms.Select(choices=DIGEST_HOUR_CHOICES),
        }
