from django import forms
from django.contrib.auth import get_user_model

from .models import Channel, Comment, Post, Profile

User = get_user_model()


class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = ["name", "intro", "description"]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "body", "image"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["country", "city", "postal_code", "post_office_box", "about_me"]
