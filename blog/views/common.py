from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages import success
from django.core.cache import cache
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Count, F, Max, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView
from django.utils.decorators import method_decorator

from ..forms import (
    ChannelForm,
    ChannelMembershipInviteForm,
    CommentForm,
    ContactForm,
    NewsletterSubscribeForm,
    PostForm,
    ProfileEditForm,
    ReportForm,
    SignUpForm,
    UserEditForm,
)
from ..models import (
    Channel,
    ChannelEditor,
    ChannelFollow,
    ChannelMembership,
    Comment,
    CommentReaction,
    Contact,
    NewsletterSubscription,
    Notification,
    Post,
    PostCoAuthor,
    PostReaction,
    Profile,
    Report,
    SavedPost,
    Tag,
    UserBlock,
    UserFollow,
)

User = get_user_model()


def get_search_query(request):
    return request.GET.get("q", "").strip()


def apply_search(queryset, search_query, search_fields):
    if not search_query or not search_fields:
        return queryset

    filters = Q()
    for field_name in search_fields:
        filters |= Q(**{f"{field_name}__icontains": search_query})
    return queryset.filter(filters)


def build_page_query_string(request):
    params = request.GET.copy()
    params.pop("page", None)
    return params.urlencode()


def build_query_with_params(request, **updates):
    params = request.GET.copy()
    for key, value in updates.items():
        if value is None:
            params.pop(key, None)
        else:
            params[key] = str(value)
    return params.urlencode()


def build_saved_post_ids(user, posts):
    if not user.is_authenticated:
        return set()

    post_ids = [post.id for post in posts]
    if not post_ids:
        return set()

    return set(
        SavedPost.objects.filter(user=user, post_id__in=post_ids).values_list("post_id", flat=True)
    )


def create_notification(recipient, actor, notification_type, message, target_url=""):
    if recipient == actor:
        return

    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        notification_type=notification_type,
        message=message,
        target_url=target_url,
    )


def get_or_create_profile(user):
    if not user.is_authenticated:
        return None
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


def build_channel_membership_context(channel, user):
    is_admin = False
    if user.is_authenticated:
        is_admin = (
            ChannelMembership.objects.filter(
                channel=channel,
                user=user,
                role__in=["admin", "creator"],
                accepted=True,
            ).exists()
            or channel.owner_id == user.id
        )
    return {
        "channel_members": ChannelMembership.objects.filter(channel=channel, accepted=True).select_related("user"),
        "channel_pending_invites": ChannelMembership.objects.filter(channel=channel, accepted=False).select_related("user"),
        "is_channel_admin": is_admin,
    }


def get_user_suspension_reason(user):
    if not user.is_authenticated:
        return ""
    profile = get_or_create_profile(user)
    if not profile or not profile.is_currently_suspended:
        return ""
    if profile.suspension_reason:
        return profile.suspension_reason
    if profile.suspended_until:
        return f"Account suspended until {profile.suspended_until:%b %d, %Y %H:%M}."
    return "Your account is suspended."


def get_comment_restriction_reason(user):
    if not user.is_authenticated:
        return ""
    profile = get_or_create_profile(user)
    if not profile or not profile.is_commenting_restricted:
        return ""
    return f"Commenting is restricted until {profile.commenting_restricted_until:%b %d, %Y %H:%M}."


def get_channel_suspension_reason(channel):
    if not channel.is_currently_suspended:
        return ""
    if channel.suspension_reason:
        return channel.suspension_reason
    if channel.suspended_until:
        return f"This channel is suspended until {channel.suspended_until:%b %d, %Y %H:%M}."
    return "This channel is suspended."


def are_users_blocked(user_a, user_b):
    if not user_a.is_authenticated or not user_b:
        return False
    if user_a.id == user_b.id:
        return False
    return UserBlock.objects.filter(
        Q(blocker=user_a, blocked=user_b) | Q(blocker=user_b, blocked=user_a)
    ).exists()


def is_blocking_user(blocker, blocked):
    if not blocker.is_authenticated or not blocked:
        return False
    if blocker.id == blocked.id:
        return False
    return UserBlock.objects.filter(blocker=blocker, blocked=blocked).exists()


def get_post_commenting_disabled_reason(user, post):
    if not user.is_authenticated:
        return ""
    suspension_reason = get_user_suspension_reason(user)
    if suspension_reason:
        return suspension_reason
    comment_restriction_reason = get_comment_restriction_reason(user)
    if comment_restriction_reason:
        return comment_restriction_reason
    if not post.channel.comments_enabled:
        return "Comments are disabled for this channel."
    if are_users_blocked(user, post.author) or are_users_blocked(user, post.channel.owner):
        return "Commenting is unavailable because one of the users has blocked the other."
    return ""


def get_discovery_tags(limit=12, search_query=""):
    queryset = Tag.objects.filter(posts__is_published=True)
    if search_query:
        queryset = queryset.filter(name__icontains=search_query)
    return (
        queryset.annotate(
            post_count=Count("posts", filter=Q(posts__is_published=True), distinct=True),
            latest_post_at=Max("posts__created_at", filter=Q(posts__is_published=True)),
        )
        .order_by("-post_count", "-latest_post_at", "name")
        .distinct()[:limit]
    )


def get_visible_post_filter(user):
    if user.is_authenticated:
        # Always show user's own posts
        own_posts = Q(author=user)
        # For private channels, only show if user is owner or accepted member
        private_channel_ids = ChannelMembership.objects.filter(user=user, accepted=True).values_list("channel_id", flat=True)
        visibility = Q(is_published=True) | Q(channel__owner=user)
        channel_ok = Q(channel__is_suspended=False) | Q(channel__owner=user)
        channel_visibility = (
            Q(channel__visibility="public")
            | (Q(channel__visibility="private") & (Q(channel__owner=user) | Q(channel_id__in=private_channel_ids)))
            | Q(channel__visibility="restricted", channel__allowed_users=user)
        )
        return own_posts | (visibility & channel_ok & channel_visibility)
    # Anonymous users: only public, non-restricted posts
    return Q(is_published=True, channel__is_suspended=False, channel__visibility="public")


def get_visible_posts_queryset(user):
    return Post.objects.filter(get_visible_post_filter(user))


def save_post_tags(post, form):
    names = form.get_tag_names()
    tags = []
    for name in names:
        from django.utils.text import slugify as _slugify

        tag, _ = Tag.objects.get_or_create(slug=_slugify(name), defaults={"name": name})
        tags.append(tag)
    post.tags.set(tags)


def home_redirect(request):
    return redirect("blog:following-posts")


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")


class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().owner == self.request.user


class AuthorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author == self.request.user


class ChannelPostOwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        post = self.get_object()
        user = self.request.user
        if post.channel.owner == user:
            return True
        return PostCoAuthor.objects.filter(post=post, user=user, accepted=True).exists()


class SearchContextMixin:
    search_fields = ()

    def get_search_query(self):
        return get_search_query(self.request)

    def apply_search(self, queryset):
        return apply_search(queryset, self.get_search_query(), self.search_fields)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.get_search_query()
        context["page_query_string"] = build_page_query_string(self.request)
        return context
