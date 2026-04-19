
from django import forms
from .models import ChannelMembership

class ChannelMembershipInviteForm(forms.Form):
    username = forms.CharField(label="Username", max_length=150)
    role = forms.ChoiceField(label="Role", choices=ChannelMembership.ROLE_CHOICES)

    def __init__(self, *args, **kwargs):
        self.channel = kwargs.pop('channel', None)
        self.invited_by = kwargs.pop('invited_by', None)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            raise forms.ValidationError("No user with that username exists.")
        if self.channel and ChannelMembership.objects.filter(channel=self.channel, user=user).exists():
            raise forms.ValidationError("This user is already a member of the channel.")
        return username

    def save(self):
        username = self.cleaned_data['username']
        role = self.cleaned_data['role']
        user = User.objects.get(username__iexact=username)
        membership = ChannelMembership.objects.create(
            user=user,
            channel=self.channel,
            role=role,
            invited_by=self.invited_by,
            accepted=False
        )
        return membership
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Channel, Comment, Contact, NewsletterSubscription, Post, Profile, Tag, Report

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
        fields = ["name", "intro", "description", "comments_enabled", "visibility", "allowed_users"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["allowed_users"].queryset = User.objects.all().order_by("username")
        self.fields["allowed_users"].required = False
        self.fields["allowed_users"].help_text = "Select users who can view this channel if visibility is set to 'Restricted'."


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
            "profile_locked",
            "email_digest_enabled",
            "digest_weekday",
            "digest_hour",
        ]
        widgets = {
            "digest_weekday": forms.Select(choices=WEEKDAY_CHOICES),
            "digest_hour": forms.Select(choices=DIGEST_HOUR_CHOICES),
        }


class ContactForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Contact
        fields = ["name", "email", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"placeholder": "your@email.com"}),
            "message": forms.Textarea(attrs={"rows": 6, "placeholder": "Your message..."}),
        }


class NewsletterSubscribeForm(forms.Form):
    website = forms.CharField(required=False, widget=forms.HiddenInput())
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}),
    )

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if NewsletterSubscription.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("This email is already subscribed.")
        return email

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["reason", "description"]
        widgets = {
            "reason": forms.RadioSelect(choices=Report.REASON_CHOICES),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Please provide details about why you're reporting this content"}),
        }
