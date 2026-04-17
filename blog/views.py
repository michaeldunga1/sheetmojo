from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.messages import success
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count, F, Max, Q, Sum
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView
from datetime import timedelta

from .forms import ChannelForm, CommentForm, ContactForm, NewsletterSubscribeForm, PostForm, ProfileEditForm, SignUpForm, UserEditForm, ReportForm

from .models import Channel, ChannelEditor, ChannelFollow, Comment, CommentReaction, Contact, NewsletterSubscription, Notification, Post, PostCoAuthor, PostReaction, Profile, SavedPost, Tag, UserFollow, Report, UserBlock
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
		visibility = Q(is_published=True) | Q(author=user) | Q(channel__owner=user)
		channel_ok = Q(channel__is_suspended=False) | Q(author=user) | Q(channel__owner=user)
		return visibility & channel_ok
	return Q(is_published=True, channel__is_suspended=False)


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

		return context


class ContactView(View):
	template_name = "blog/contact.html"
	form_class = ContactForm

	def _setting_int(self, name, default, minimum=1):
		try:
			value = int(getattr(settings, name, default))
		except (TypeError, ValueError):
			value = default
		return max(minimum, value)

	def _rate_limit_window_seconds(self):
		return self._setting_int("CONTACT_RATE_LIMIT_WINDOW_SECONDS", 10 * 60)

	def _rate_limit_max_submissions(self):
		return self._setting_int("CONTACT_RATE_LIMIT_MAX_SUBMISSIONS", 3)

	def _email_cooldown_seconds(self):
		return self._setting_int("CONTACT_EMAIL_COOLDOWN_SECONDS", 60)

	def _duplicate_window_hours(self):
		return self._setting_int("CONTACT_DUPLICATE_WINDOW_HOURS", 24)

	def _client_ip(self, request):
		forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
		if forwarded_for:
			return forwarded_for.split(",")[0].strip()
		return request.META.get("REMOTE_ADDR", "unknown")

	def _rate_limit_key(self, client_ip):
		return f"contact-rate:{client_ip}"

	def _email_cooldown_key(self, email):
		return f"contact-cooldown:{email}"

	def _is_rate_limited(self, client_ip):
		count = cache.get(self._rate_limit_key(client_ip), 0)
		return count >= self._rate_limit_max_submissions()

	def _record_submission(self, client_ip):
		key = self._rate_limit_key(client_ip)
		window = self._rate_limit_window_seconds()
		if not cache.add(key, 1, timeout=window):
			try:
				cache.incr(key)
			except ValueError:
				cache.set(key, 1, timeout=window)

	def _is_email_in_cooldown(self, email):
		if not email:
			return False
		return bool(cache.get(self._email_cooldown_key(email), False))

	def _record_email_submission(self, email):
		if email:
			cache.set(self._email_cooldown_key(email), True, timeout=self._email_cooldown_seconds())

	def get(self, request):
		form = self.form_class()
		return render(request, self.template_name, {"form": form})

	def post(self, request):
		form = self.form_class(request.POST)
		if form.is_valid():
			if form.cleaned_data.get("website"):
				messages.success(request, "Thank you for your message! We'll get back to you soon.")
				return redirect("blog:contact")

			email = (form.cleaned_data.get("email") or "").strip().lower()
			client_ip = self._client_ip(request)
			if self._is_rate_limited(client_ip):
				form.add_error(None, "Too many messages from this network. Please try again in a few minutes.")
				return render(request, self.template_name, {"form": form})

			message = (form.cleaned_data.get("message") or "").strip()
			duplicate_cutoff = timezone.now() - timedelta(hours=self._duplicate_window_hours())
			if Contact.objects.filter(email__iexact=email, message=message, received_at__gte=duplicate_cutoff).exists():
				form.add_error(None, "We already received this message recently. Please avoid sending duplicates.")
				return render(request, self.template_name, {"form": form})

			if self._is_email_in_cooldown(email):
				form.add_error(None, "Please wait a minute before sending another message from this email.")
				return render(request, self.template_name, {"form": form})

			form.save()
			self._record_submission(client_ip)
			self._record_email_submission(email)
			messages.success(request, "Thank you for your message! We'll get back to you soon.")
			return redirect("blog:contact")
		return render(request, self.template_name, {"form": form})


class NewsletterSubscribeView(View):
	template_name = "blog/newsletter_subscribe.html"
	form_class = NewsletterSubscribeForm

	def _setting_int(self, name, default, minimum=1):
		try:
			value = int(getattr(settings, name, default))
		except (TypeError, ValueError):
			value = default
		return max(minimum, value)

	def _rate_limit_window_seconds(self):
		return self._setting_int("NEWSLETTER_RATE_LIMIT_WINDOW_SECONDS", 10 * 60)

	def _rate_limit_max_submissions(self):
		return self._setting_int("NEWSLETTER_RATE_LIMIT_MAX_SUBMISSIONS", 5)

	def _client_ip(self, request):
		forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
		if forwarded_for:
			return forwarded_for.split(",")[0].strip()
		return request.META.get("REMOTE_ADDR", "unknown")

	def _rate_limit_key(self, client_ip):
		return f"newsletter-rate:{client_ip}"

	def _is_rate_limited(self, client_ip):
		count = cache.get(self._rate_limit_key(client_ip), 0)
		return count >= self._rate_limit_max_submissions()

	def _record_submission(self, client_ip):
		key = self._rate_limit_key(client_ip)
		window = self._rate_limit_window_seconds()
		if not cache.add(key, 1, timeout=window):
			try:
				cache.incr(key)
			except ValueError:
				cache.set(key, 1, timeout=window)

	def get(self, request):
		form = self.form_class()
		return render(request, self.template_name, {"form": form})

	def post(self, request):
		form = self.form_class(request.POST)
		if form.is_valid():
			if form.cleaned_data.get("website"):
				messages.success(request, "Thanks for subscribing to our newsletter.")
				return redirect("blog:newsletter-subscribe")

			client_ip = self._client_ip(request)
			if self._is_rate_limited(client_ip):
				form.add_error(None, "Too many subscription attempts from this network. Please try again later.")
				return render(request, self.template_name, {"form": form})

			email = (form.cleaned_data.get("email") or "").strip().lower()
			subscription, created = NewsletterSubscription.objects.get_or_create(
				email=email,
				defaults={"is_active": True},
			)
			if not created and not subscription.is_active:
				subscription.is_active = True
				subscription.save(update_fields=["is_active"])

			self._record_submission(client_ip)
			messages.success(request, "Thanks for subscribing to our newsletter.")
			return redirect("blog:newsletter-subscribe")

		return render(request, self.template_name, {"form": form})


class SupportUsView(View):
	template_name = "blog/support_us.html"

	def get(self, request):
		return render(request, self.template_name)

class PostReportView(LoginRequiredMixin, View):
	template_name = "blog/report_form.html"

	def get_post(self):
		return get_object_or_404(Post, channel__slug=self.kwargs["channel_slug"], slug=self.kwargs["post_slug"])

	def get(self, request, **kwargs):
		post = self.get_post()
		existing = Report.objects.filter(reporter=request.user, post=post).first()
		form = ReportForm(instance=existing)
		return render(request, self.template_name, {"form": form, "post": post, "content_type": "post", "existing_report": existing})

	def post(self, request, **kwargs):
		post = self.get_post()
		suspension_reason = get_user_suspension_reason(request.user)
		if suspension_reason:
			messages.error(request, suspension_reason)
			return redirect(post.get_absolute_url())
		if are_users_blocked(request.user, post.author) or are_users_blocked(request.user, post.channel.owner):
			messages.error(request, "Reporting is unavailable because one of the users has blocked the other.")
			return redirect(post.get_absolute_url())
		existing = Report.objects.filter(reporter=request.user, post=post).first()
		form = ReportForm(request.POST, instance=existing)
		if form.is_valid():
			report = form.save(commit=False)
			report.reporter = request.user
			report.content_type = Report.CONTENT_POST
			report.post = post
			report.save()
			success(request, "Your report has been saved. Our team will review it shortly.")
			return redirect(post.get_absolute_url())
		return render(request, self.template_name, {"form": form, "post": post, "content_type": "post", "existing_report": existing})


class CommentReportView(LoginRequiredMixin, View):
	template_name = "blog/report_form.html"

	def get_comment(self):
		return get_object_or_404(Comment, pk=self.kwargs["comment_id"])

	def get(self, request, **kwargs):
		comment = self.get_comment()
		existing = Report.objects.filter(reporter=request.user, comment=comment).first()
		form = ReportForm(instance=existing)
		return render(request, self.template_name, {"form": form, "comment": comment, "content_type": "comment", "existing_report": existing})

	def post(self, request, **kwargs):
		comment = self.get_comment()
		suspension_reason = get_user_suspension_reason(request.user)
		if suspension_reason:
			messages.error(request, suspension_reason)
			return redirect(comment.post.get_absolute_url())
		if are_users_blocked(request.user, comment.author):
			messages.error(request, "Reporting is unavailable because one of the users has blocked the other.")
			return redirect(comment.post.get_absolute_url())
		existing = Report.objects.filter(reporter=request.user, comment=comment).first()
		form = ReportForm(request.POST, instance=existing)
		if form.is_valid():
			report = form.save(commit=False)
			report.reporter = request.user
			report.content_type = Report.CONTENT_COMMENT
			report.comment = comment
			report.save()
			success(request, "Your report has been saved. Our team will review it shortly.")
			return redirect(comment.post.get_absolute_url())
		return render(request, self.template_name, {"form": form, "comment": comment, "content_type": "comment", "existing_report": existing})


class ChannelReportView(LoginRequiredMixin, View):
	template_name = "blog/report_form.html"

	def get_channel(self):
		return get_object_or_404(Channel, slug=self.kwargs["channel_slug"])

	def get(self, request, **kwargs):
		channel = self.get_channel()
		existing = Report.objects.filter(reporter=request.user, channel=channel).first()
		form = ReportForm(instance=existing)
		return render(request, self.template_name, {"form": form, "channel": channel, "content_type": "channel", "existing_report": existing})

	def post(self, request, **kwargs):
		channel = self.get_channel()
		suspension_reason = get_user_suspension_reason(request.user)
		if suspension_reason:
			messages.error(request, suspension_reason)
			return redirect(channel.get_absolute_url())
		if are_users_blocked(request.user, channel.owner):
			messages.error(request, "Reporting is unavailable because one of the users has blocked the other.")
			return redirect(channel.get_absolute_url())
		existing = Report.objects.filter(reporter=request.user, channel=channel).first()
		form = ReportForm(request.POST, instance=existing)
		if form.is_valid():
			report = form.save(commit=False)
			report.reporter = request.user
			report.content_type = Report.CONTENT_CHANNEL
			report.channel = channel
			report.save()
			success(request, "Your report has been saved. Our team will review it shortly.")
			return redirect(channel.get_absolute_url())
		return render(request, self.template_name, {"form": form, "channel": channel, "content_type": "channel", "existing_report": existing})


class UserReportView(LoginRequiredMixin, View):
	template_name = "blog/report_form.html"

	def get_reported_user(self):
		return get_object_or_404(User, username=self.kwargs["username"])

	def get(self, request, **kwargs):
		reported_user = self.get_reported_user()
		existing = Report.objects.filter(reporter=request.user, reported_user=reported_user).first()
		form = ReportForm(instance=existing)
		return render(request, self.template_name, {"form": form, "reported_user": reported_user, "content_type": "user", "existing_report": existing})

	def post(self, request, **kwargs):
		reported_user = self.get_reported_user()
		suspension_reason = get_user_suspension_reason(request.user)
		if suspension_reason:
			messages.error(request, suspension_reason)
			return redirect(reverse("blog:user-profile", kwargs={"username": reported_user.username}))
		if are_users_blocked(request.user, reported_user):
			messages.error(request, "Reporting is unavailable because one of the users has blocked the other.")
			return redirect(reverse("blog:user-profile", kwargs={"username": reported_user.username}))
		existing = Report.objects.filter(reporter=request.user, reported_user=reported_user).first()
		form = ReportForm(request.POST, instance=existing)
		if form.is_valid():
			report = form.save(commit=False)
			report.reporter = request.user
			report.content_type = Report.CONTENT_USER
			report.reported_user = reported_user
			report.save()
			success(request, "Your report has been saved. Our team will review it shortly.")
			return redirect(reverse("blog:user-profile", kwargs={"username": reported_user.username}))
		return render(request, self.template_name, {"form": form, "reported_user": reported_user, "content_type": "user", "existing_report": existing})


class ReportDeleteView(LoginRequiredMixin, View):
	def post(self, request, pk):
		report = get_object_or_404(Report, pk=pk, reporter=request.user)
		redirect_url = self._get_redirect_url(report)
		report.delete()
		success(request, "Your report has been withdrawn.")
		return redirect(redirect_url)

	def _get_redirect_url(self, report):
		if report.post:
			return report.post.get_absolute_url()
		if report.comment:
			return report.comment.post.get_absolute_url()
		if report.channel:
			return report.channel.get_absolute_url()
		if report.reported_user:
			return reverse("blog:user-profile", kwargs={"username": report.reported_user.username})
		return reverse("blog:channel-list")


class ChannelListView(SearchContextMixin, LoginRequiredMixin, ListView):
	model = Channel
	template_name = "blog/channel_list.html"
	context_object_name = "channels"
	paginate_by = 10
	search_fields = ("name", "intro", "description", "owner__username")

	def get_queryset(self):
		queryset = (
			Channel.objects.select_related("owner")
			.order_by("-follower_count", "-created_at", "-id")
		)
		return self.apply_search(queryset)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		followed_channel_ids = set(
			ChannelFollow.objects.filter(follower=self.request.user).values_list("channel_id", flat=True)
		)
		context["followed_channel_ids"] = followed_channel_ids
		return context


class MyChannelListView(ChannelListView):
	template_name = "blog/channel_list.html"

	def get_queryset(self):
		return super().get_queryset().filter(owner=self.request.user)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["page_title"] = "My Channels"
		context["page_kicker"] = "Publications you own and manage."
		context["search_placeholder"] = "Search your channels by name, intro, or description"
		context["page_is_private"] = True
		context["empty_state_text"] = "You have not created any channels yet."
		return context


class FollowedChannelListView(ChannelListView):
	template_name = "blog/channel_list.html"

	def get_queryset(self):
		followed_channel_ids = ChannelFollow.objects.filter(
			follower=self.request.user
		).values_list("channel_id", flat=True)
		return super().get_queryset().filter(pk__in=followed_channel_ids)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["page_title"] = "Followed Channels"
		context["page_kicker"] = "Channels you follow, ready to revisit or search."
		context["search_placeholder"] = "Search the channels you follow by name, intro, description, or owner"
		context["page_is_private"] = True
		context["empty_state_text"] = "You are not following any channels yet."
		return context


class SavedPostListView(SearchContextMixin, LoginRequiredMixin, ListView):
	model = Post
	template_name = "blog/saved_posts.html"
	context_object_name = "posts"
	paginate_by = 10
	search_fields = ("title", "body", "author__username", "channel__name")

	def get_queryset(self):
		queryset = (
			Post.objects.filter(saved_by__user=self.request.user)
			.filter(get_visible_post_filter(self.request.user))
			.select_related("channel", "author", "channel__owner")
			.order_by("-saved_by__created_at", "-id")
		)
		return self.apply_search(queryset)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["saved_post_ids"] = build_saved_post_ids(self.request.user, context.get("posts", []))
		return context


class NotificationListView(SearchContextMixin, LoginRequiredMixin, ListView):
	model = Notification
	template_name = "blog/notifications.html"
	context_object_name = "notifications"
	paginate_by = 12
	search_fields = ("message", "actor__username")
	type_choices = (
		("all", "All types"),
		(Notification.TYPE_FOLLOW, "New follower"),
		(Notification.TYPE_NEW_POST, "New post"),
		(Notification.TYPE_COMMENT, "New comment"),
		(Notification.TYPE_COAUTHOR_INVITE, "Co-author invite"),
		(Notification.TYPE_COAUTHOR_ACCEPTED, "Co-author accepted"),
		(Notification.TYPE_EDITOR_INVITE, "Editor invite"),
		(Notification.TYPE_EDITOR_ACCEPTED, "Editor accepted"),
	)

	def get_status_filter(self):
		# Backward compatible with existing `unread=1` query parameter.
		if self.request.GET.get("unread") == "1":
			return "unread"
		status = self.request.GET.get("status", "all")
		return status if status in {"all", "unread", "read"} else "all"

	def get_type_filter(self):
		notification_type = self.request.GET.get("type", "all")
		valid_types = {choice[0] for choice in self.type_choices}
		return notification_type if notification_type in valid_types else "all"

	def get_queryset(self):
		queryset = Notification.objects.select_related("actor").filter(recipient=self.request.user)
		status_filter = self.get_status_filter()
		type_filter = self.get_type_filter()
		if status_filter == "unread":
			queryset = queryset.filter(is_read=False)
		elif status_filter == "read":
			queryset = queryset.filter(is_read=True)
		if type_filter != "all":
			queryset = queryset.filter(notification_type=type_filter)
		return self.apply_search(queryset)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		status_filter = self.get_status_filter()
		type_filter = self.get_type_filter()
		context["status_filter"] = status_filter
		context["type_filter"] = type_filter
		context["type_choices"] = self.type_choices
		context["unread_only"] = status_filter == "unread"
		# Pending invites so notifications template can show accept/decline forms
		context["pending_coauthor_invites"] = {
			invite.post_id: invite.pk
			for invite in PostCoAuthor.objects.filter(user=self.request.user, accepted=None)
		}
		context["pending_editor_invites"] = {
			invite.channel_id: invite.pk
			for invite in ChannelEditor.objects.filter(user=self.request.user, accepted=None)
		}
		return context


class NotificationBatchActionView(LoginRequiredMixin, View):
	def post(self, request):
		action = request.POST.get("action", "")
		notification_ids = request.POST.getlist("notification_ids")
		queryset = Notification.objects.filter(recipient=request.user, pk__in=notification_ids)

		if action == "mark_read":
			queryset.update(is_read=True)
		elif action == "mark_unread":
			queryset.update(is_read=False)
		elif action == "delete":
			queryset.delete()

		next_url = request.POST.get("next", "")
		if next_url and url_has_allowed_host_and_scheme(
			next_url,
			allowed_hosts={request.get_host()},
			require_https=request.is_secure(),
		):
			return redirect(next_url)
		return redirect("blog:notifications")


class ChannelDetailView(LoginRequiredMixin, DetailView):
	model = Channel
	template_name = "blog/channel_detail.html"
	context_object_name = "channel"
	slug_field = "slug"
	slug_url_kwarg = "channel_slug"
	analytics_window_choices = (
		("7d", "7 days"),
		("30d", "30 days"),
		("all", "All time"),
	)

	def get_analytics_window(self):
		window = self.request.GET.get("window", "7d")
		valid = {choice[0] for choice in self.analytics_window_choices}
		return window if window in valid else "7d"

	def get_queryset(self):
		return Channel.objects.select_related("owner")

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["recent_posts"] = self.object.posts.filter(is_published=True).select_related("author").order_by("-created_at")[:5]
		context["is_following"] = ChannelFollow.objects.filter(
			follower=self.request.user,
			channel=self.object,
		).exists()
		context["has_reported_channel"] = Report.objects.filter(
			reporter=self.request.user,
			channel=self.object,
		).exists()
		if self.object.owner_id == self.request.user.id:
			analytics_window = self.get_analytics_window()
			channel_posts = self.object.posts.filter(is_published=True)
			if analytics_window == "7d":
				channel_posts = channel_posts.filter(created_at__gte=timezone.now() - timedelta(days=7))
			elif analytics_window == "30d":
				channel_posts = channel_posts.filter(created_at__gte=timezone.now() - timedelta(days=30))

			totals = channel_posts.aggregate(
				total_views=Sum("view_count"),
				total_loves=Sum("love_count"),
				total_comments=Sum("comment_count"),
				total_saves=Sum("saves_count"),
			)
			total_posts = channel_posts.count()
			total_views = totals["total_views"] or 0
			total_loves = totals["total_loves"] or 0
			total_comments = totals["total_comments"] or 0
			total_saves = totals["total_saves"] or 0
			total_engagement = total_loves + total_comments + total_saves
			top_post = channel_posts.order_by(
				"-love_count", "-comment_count", "-saves_count", "-view_count", "-created_at"
			).first()
			window_label = dict(self.analytics_window_choices).get(analytics_window, "7 days")

			context["channel_analytics"] = {
				"total_posts": total_posts,
				"total_followers": self.object.follower_count,
				"total_views": total_views,
				"total_loves": total_loves,
				"total_comments": total_comments,
				"total_saves": total_saves,
				"total_engagement": total_engagement,
				"posts_in_window": total_posts,
				"window_label": window_label,
				"avg_engagement_per_post": round(total_engagement / total_posts, 1) if total_posts else 0,
				"engagement_rate": round((total_engagement / total_views) * 100, 1) if total_views else 0,
				"top_post": top_post,
			}
			context["analytics_window"] = analytics_window
			context["analytics_window_choices"] = self.analytics_window_choices
			context["analytics_window_links"] = [
				{
					"value": value,
					"label": label,
					"query_string": build_query_with_params(self.request, window=value),
				}
				for value, label in self.analytics_window_choices
			]
		else:
			context["channel_analytics"] = None
			context["analytics_window"] = None
			context["analytics_window_choices"] = self.analytics_window_choices
			context["analytics_window_links"] = []
		# Editors
		context["channel_editors"] = ChannelEditor.objects.filter(
			channel=self.object, accepted=True
		).select_related("user")
		if self.object.owner_id == self.request.user.id:
			context["channel_editor_invites"] = ChannelEditor.objects.filter(
				channel=self.object, accepted=None
			).select_related("user")
		else:
			context["channel_editor_invites"] = ChannelEditor.objects.none()
		context["is_channel_editor"] = ChannelEditor.objects.filter(
			channel=self.object, user=self.request.user, accepted=True
		).exists()
		context["my_editor_invite"] = ChannelEditor.objects.filter(
			channel=self.object, user=self.request.user, accepted=None
		).first()
		return context


class FollowingPostListView(SearchContextMixin, ListView):
	model = Post
	template_name = "blog/following_posts.html"
	context_object_name = "posts"
	paginate_by = 10
	search_fields = ("title", "body", "author__username", "channel__name")

	def get_queryset(self):
		base_queryset = Post.objects.filter(is_published=True).select_related("channel", "author", "channel__owner")

		if not self.request.user.is_authenticated:
			return self.apply_search(base_queryset.order_by("-created_at"))

		followed_channel_ids = list(
			ChannelFollow.objects.filter(follower=self.request.user).values_list("channel_id", flat=True)
		)

		if not followed_channel_ids:
			return self.apply_search(base_queryset.order_by("-created_at"))

		queryset = (
			base_queryset.filter(
				Q(channel_id__in=followed_channel_ids) | Q(author=self.request.user)
			)
			.distinct()
			.order_by("-created_at")
		)
		return self.apply_search(queryset)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["saved_post_ids"] = build_saved_post_ids(self.request.user, context.get("posts", []))
		context["trending_tags"] = get_discovery_tags(limit=10)
		return context


class UserFollowingPostListView(SearchContextMixin, LoginRequiredMixin, ListView):
	model = Post
	template_name = "blog/user_following_posts.html"
	context_object_name = "posts"
	paginate_by = 10
	search_fields = ("title", "body", "author__username", "channel__name")

	def get_queryset(self):
		followed_user_ids = list(
			UserFollow.objects.filter(follower=self.request.user).values_list("following_id", flat=True)
		)
		base_queryset = Post.objects.filter(is_published=True).select_related("channel", "author", "channel__owner").order_by("-created_at")
		if not followed_user_ids:
			return self.apply_search(base_queryset.none())
		queryset = base_queryset.filter(author_id__in=followed_user_ids).distinct()
		return self.apply_search(queryset)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["saved_post_ids"] = build_saved_post_ids(self.request.user, context.get("posts", []))
		return context


class TrendingPostListView(SearchContextMixin, LoginRequiredMixin, ListView):
	model = Post
	template_name = "blog/trending_posts.html"
	context_object_name = "posts"
	paginate_by = 10
	search_fields = ("title", "body", "author__username", "channel__name")

	def get_sort_by(self):
		sort_by = self.request.GET.get("sort", "love")
		return sort_by if sort_by in {"love", "comments", "date"} else "love"

	def get_window(self):
		window = self.request.GET.get("window", "7d")
		return window if window in {"24h", "7d", "30d", "all"} else "7d"

	def get_queryset(self):
		sort_by = self.get_sort_by()
		window = self.get_window()

		queryset = (
			Post.objects.filter(is_published=True).select_related("channel", "author", "channel__owner")
		)

		if window != "all":
			delta_map = {
				"24h": timedelta(hours=24),
				"7d": timedelta(days=7),
				"30d": timedelta(days=30),
			}
			queryset = queryset.filter(created_at__gte=timezone.now() - delta_map[window])

		queryset = self.apply_search(queryset)

		if sort_by == "comments":
			return queryset.order_by("-comment_count", "-love_count", "-created_at")
		if sort_by == "date":
			return queryset.order_by("-created_at", "-love_count", "-comment_count")
		return queryset.order_by("-love_count", "-comment_count", "-created_at")

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["saved_post_ids"] = build_saved_post_ids(self.request.user, context.get("posts", []))
		context["sort_by"] = self.get_sort_by()
		context["window"] = self.get_window()
		context["show_popularity_metrics"] = True
		return context


class UserProfileView(LoginRequiredMixin, TemplateView):
	template_name = "blog/profile.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context.update(
			build_user_profile_context(
				self.request.user,
				self.request.user,
				request=self.request,
				search_query=get_search_query(self.request),
			)
		)
		return context


class PublicUserProfileView(LoginRequiredMixin, TemplateView):
	template_name = "blog/profile.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		profile_user = get_object_or_404(User, username=self.kwargs["username"])
		context.update(
			build_user_profile_context(
				profile_user,
				self.request.user,
				request=self.request,
				search_query=get_search_query(self.request),
			)
		)
		return context



def build_user_profile_context(profile_user, current_user, request=None, search_query=""):
	profile_obj = Profile.objects.filter(user=profile_user).first()
	visible_posts = (
		Post.objects.filter(author=profile_user)
		.select_related("channel")
		.order_by("-created_at")
	)
	if profile_user != current_user:
		visible_posts = visible_posts.filter(is_published=True)

	state_filter = "all"
	if request:
		requested_state = request.GET.get("state", "all")
		if profile_user == current_user:
			state_filter = requested_state if requested_state in {"all", "published", "drafts"} else "all"
		else:
			state_filter = "published"

	if state_filter == "published":
		visible_posts = visible_posts.filter(is_published=True)
	elif state_filter == "drafts":
		visible_posts = visible_posts.filter(is_published=False)

	filtered_user_posts = apply_search(visible_posts, search_query, ("title", "body", "channel__name"))
	post_page_number = request.GET.get("page", "1") if request else "1"
	user_posts_page = Paginator(filtered_user_posts, 10).get_page(post_page_number)
	user_posts = list(user_posts_page.object_list)
	page_query_string = ""
	if request:
		params = request.GET.copy()
		params.pop("page", None)
		page_query_string = params.urlencode()
	is_following = False
	is_user_blocked = False
	is_blocked_by_user = False
	if current_user.is_authenticated and profile_user != current_user:
		is_user_blocked = is_blocking_user(current_user, profile_user)
		is_blocked_by_user = is_blocking_user(profile_user, current_user)
		is_following = UserFollow.objects.filter(follower=current_user, following=profile_user).exists()
		if is_user_blocked or is_blocked_by_user:
			is_following = False
	has_reported_user = False
	if current_user.is_authenticated and profile_user != current_user:
		has_reported_user = Report.objects.filter(reporter=current_user, reported_user=profile_user).exists()
	published_post_count = Post.objects.filter(author=profile_user, is_published=True).count()
	draft_post_count = Post.objects.filter(author=profile_user, is_published=False).count() if profile_user == current_user else 0
	return {
		"profile_user": profile_user,
		"profile_obj": profile_obj,
		"user_posts": user_posts,
		"page_obj": user_posts_page,
		"paginator": user_posts_page.paginator,
		"is_paginated": user_posts_page.has_other_pages(),
		"page_query_string": page_query_string,
		"user_post_count": Post.objects.filter(author=profile_user).count() if profile_user == current_user else published_post_count,
		"published_post_count": published_post_count,
		"draft_post_count": draft_post_count,
		"state_filter": state_filter,
		"user_channel_count": Channel.objects.filter(owner=profile_user).count(),
		"user_follower_count": UserFollow.objects.filter(following=profile_user).count(),
		"user_following_count": UserFollow.objects.filter(follower=profile_user).count(),
		"is_own_profile": profile_user == current_user,
		"is_following_user": is_following,
		"is_user_blocked": is_user_blocked,
		"is_blocked_by_user": is_blocked_by_user,
		"has_reported_user": has_reported_user,
		"search_query": search_query,
		"saved_post_ids": build_saved_post_ids(current_user, user_posts),
	}


class UserProfileEditView(LoginRequiredMixin, View):
	template_name = "blog/profile_form.html"

	def get(self, request):
		profile_obj, _ = Profile.objects.get_or_create(user=request.user)
		user_form = UserEditForm(instance=request.user)
		profile_form = ProfileEditForm(instance=profile_obj)
		return render(
			request,
			self.template_name,
			{"user_form": user_form, "profile_form": profile_form},
		)

	def post(self, request):
		profile_obj, _ = Profile.objects.get_or_create(user=request.user)
		user_form = UserEditForm(request.POST, instance=request.user)
		profile_form = ProfileEditForm(request.POST, instance=profile_obj)
		if user_form.is_valid() and profile_form.is_valid():
			user_form.save()
			profile_form.save()
			return redirect("blog:profile")
		return render(
			request,
			self.template_name,
			{"user_form": user_form, "profile_form": profile_form},
		)


class DashboardView(LoginRequiredMixin, View):
	template_name = "blog/dashboard.html"
	paginate_by = 20

	TABS = ("posts", "channels", "comments", "reactions", "reports")
	DATE_SCOPES = ("all", "day", "month", "year", "duration", "range")

	def _to_int(self, value, default=None):
		if value in (None, ""):
			return default
		try:
			return int(value)
		except (TypeError, ValueError):
			return default

	def _apply_date_filters(self, queryset, request, field_name="created_at"):
		scope = request.GET.get("date_scope", "all")
		if scope not in self.DATE_SCOPES:
			scope = "all"

		now = timezone.now()
		if scope == "day":
			day = request.GET.get("day", "")
			if day:
				queryset = queryset.filter(**{f"{field_name}__date": day})
		elif scope == "month":
			month = request.GET.get("month", "")
			if month:
				queryset = queryset.filter(**{f"{field_name}__startswith": month})
		elif scope == "year":
			year = self._to_int(request.GET.get("year"))
			if year:
				queryset = queryset.filter(**{f"{field_name}__year": year})
		elif scope == "duration":
			days = self._to_int(request.GET.get("duration_days"), default=0)
			if days and days > 0:
				queryset = queryset.filter(**{f"{field_name}__gte": now - timedelta(days=days)})
		elif scope == "range":
			start_date = request.GET.get("start_date", "")
			end_date = request.GET.get("end_date", "")
			if start_date:
				queryset = queryset.filter(**{f"{field_name}__date__gte": start_date})
			if end_date:
				queryset = queryset.filter(**{f"{field_name}__date__lte": end_date})

		return queryset

	def _apply_numeric_filters(self, queryset, request, min_param, max_param, field_name):
		min_value = self._to_int(request.GET.get(min_param))
		max_value = self._to_int(request.GET.get(max_param))
		if min_value is not None:
			queryset = queryset.filter(**{f"{field_name}__gte": min_value})
		if max_value is not None:
			queryset = queryset.filter(**{f"{field_name}__lte": max_value})
		return queryset

	def _get_tab_queryset(self, request, tab, search_q):
		user = request.user
		if tab == "posts":
			qs = (
				Post.objects.filter(author=user)
				.select_related("channel")
				.annotate(report_count=Count("reports", distinct=True))
				.order_by("-created_at")
			)
			state = request.GET.get("state", "all")
			if state not in ("all", "published", "drafts"):
				state = "all"
			if state == "published":
				qs = qs.filter(is_published=True)
			elif state == "drafts":
				qs = qs.filter(is_published=False)

			channel_id = request.GET.get("channel_id", "")
			if channel_id.isdigit():
				qs = qs.filter(channel_id=int(channel_id))

			if search_q:
				qs = qs.filter(Q(title__icontains=search_q) | Q(channel__name__icontains=search_q))
			qs = self._apply_date_filters(qs, request)
			qs = self._apply_numeric_filters(qs, request, "min_comment_count", "max_comment_count", "comment_count")
			qs = self._apply_numeric_filters(qs, request, "min_flag_count", "max_flag_count", "report_count")
			qs = self._apply_numeric_filters(qs, request, "min_like_count", "max_like_count", "love_count")
			return qs

		if tab == "channels":
			qs = (
				Channel.objects.filter(owner=user)
				.annotate(report_count=Count("reports", distinct=True))
				.order_by("-created_at")
			)
			if search_q:
				qs = qs.filter(Q(name__icontains=search_q) | Q(description__icontains=search_q))
			qs = self._apply_date_filters(qs, request)
			qs = self._apply_numeric_filters(qs, request, "min_follower_count", "max_follower_count", "follower_count")
			qs = self._apply_numeric_filters(qs, request, "min_posts_count", "max_posts_count", "posts_count")
			qs = self._apply_numeric_filters(qs, request, "min_flag_count", "max_flag_count", "report_count")
			return qs

		if tab == "comments":
			qs = (
				Comment.objects.filter(author=user)
				.select_related("post", "post__channel")
				.annotate(report_count=Count("reports", distinct=True))
				.order_by("-created_at")
			)
			if search_q:
				qs = qs.filter(Q(body__icontains=search_q) | Q(post__title__icontains=search_q))
			qs = self._apply_date_filters(qs, request)
			qs = self._apply_numeric_filters(qs, request, "min_like_count", "max_like_count", "love_count")
			qs = self._apply_numeric_filters(qs, request, "min_flag_count", "max_flag_count", "report_count")
			return qs

		if tab == "reactions":
			qs = (
				PostReaction.objects.filter(user=user, reaction=PostReaction.LOVE)
				.select_related("post", "post__channel", "post__author")
				.order_by("-created_at")
			)
			if search_q:
				qs = qs.filter(Q(post__title__icontains=search_q) | Q(post__author__username__icontains=search_q))
			qs = self._apply_date_filters(qs, request)
			return qs

		qs = (
			Report.objects.filter(reporter=user)
			.select_related("post", "comment", "channel", "reported_user")
			.order_by("-created_at")
		)
		if search_q:
			qs = qs.filter(Q(reason__icontains=search_q) | Q(description__icontains=search_q))
		status = request.GET.get("status", "")
		reason = request.GET.get("reason", "")
		content_type = request.GET.get("content_type", "")
		if status in {choice[0] for choice in Report.STATUS_CHOICES}:
			qs = qs.filter(status=status)
		if reason in {choice[0] for choice in Report.REASON_CHOICES}:
			qs = qs.filter(reason=reason)
		if content_type in {choice[0] for choice in Report.CONTENT_CHOICES}:
			qs = qs.filter(content_type=content_type)
		qs = self._apply_date_filters(qs, request)
		return qs

	def _build_counts(self, user):
		channels_qs = Channel.objects.filter(owner=user)
		return {
			"posts": Post.objects.filter(author=user).count(),
			"channels": channels_qs.count(),
			"comments": Comment.objects.filter(author=user).count(),
			"reactions": PostReaction.objects.filter(user=user, reaction=PostReaction.LOVE).count(),
			"reports": Report.objects.filter(reporter=user).count(),
			"posts_created": Post.objects.filter(author=user).count(),
			"channels_owned": channels_qs.count(),
			"subscriber_count": channels_qs.aggregate(total=Sum("follower_count")).get("total") or 0,
			"blocking_count": UserBlock.objects.filter(blocker=user).count(),
			"blocker_count": UserBlock.objects.filter(blocked=user).count(),
		}

	def _flag_posts(self, user, posts):
		created_count = 0
		for post in posts:
			_, created = Report.objects.update_or_create(
				reporter=user,
				post=post,
				defaults={
					"content_type": Report.CONTENT_POST,
					"reason": Report.REASON_OTHER,
					"description": "Flagged via dashboard batch action.",
				},
			)
			if created:
				created_count += 1
		return created_count

	def _flag_channels(self, user, channels):
		created_count = 0
		for channel in channels:
			_, created = Report.objects.update_or_create(
				reporter=user,
				channel=channel,
				defaults={
					"content_type": Report.CONTENT_CHANNEL,
					"reason": Report.REASON_OTHER,
					"description": "Flagged via dashboard batch action.",
				},
			)
			if created:
				created_count += 1
		return created_count

	def _flag_comments(self, user, comments):
		created_count = 0
		for comment in comments:
			_, created = Report.objects.update_or_create(
				reporter=user,
				comment=comment,
				defaults={
					"content_type": Report.CONTENT_COMMENT,
					"reason": Report.REASON_OTHER,
					"description": "Flagged via dashboard batch action.",
				},
			)
			if created:
				created_count += 1
		return created_count

	def _run_batch_action(self, request, tab, action, selected_ids):
		user = request.user
		if tab == "posts":
			qs = Post.objects.filter(author=user, id__in=selected_ids)
			if action == "delete":
				count = qs.count()
				qs.delete()
				return f"Deleted {count} post(s)."
			if action == "publish":
				count = qs.update(is_published=True, published_at=timezone.now())
				return f"Published {count} post(s)."
			if action == "unpublish":
				count = qs.update(is_published=False, published_at=None)
				return f"Unpublished {count} post(s)."
			if action == "like":
				created_count = 0
				for post in qs:
					_, created = PostReaction.objects.get_or_create(user=user, post=post, reaction=PostReaction.LOVE)
					if created:
						created_count += 1
				return f"Added {created_count} like reaction(s)."
			if action == "unlike":
				count, _ = PostReaction.objects.filter(user=user, post__in=qs, reaction=PostReaction.LOVE).delete()
				return f"Removed {count} like reaction(s)."
			if action == "flag":
				count = self._flag_posts(user, qs)
				return f"Flagged {count} post(s)."

		if tab == "channels":
			qs = Channel.objects.filter(owner=user, id__in=selected_ids)
			if action == "delete":
				count = qs.count()
				qs.delete()
				return f"Deleted {count} channel(s)."
			if action == "suspend":
				count = qs.update(is_suspended=True)
				return f"Suspended {count} channel(s)."
			if action == "unsuspend":
				count = qs.update(is_suspended=False, suspended_until=None, suspension_reason="")
				return f"Unsuspended {count} channel(s)."
			if action == "disable_comments":
				count = qs.update(comments_enabled=False)
				return f"Disabled comments for {count} channel(s)."
			if action == "enable_comments":
				count = qs.update(comments_enabled=True)
				return f"Enabled comments for {count} channel(s)."
			if action == "flag":
				count = self._flag_channels(user, qs)
				return f"Flagged {count} channel(s)."

		if tab == "comments":
			qs = Comment.objects.filter(author=user, id__in=selected_ids)
			if action == "delete":
				count = qs.count()
				qs.delete()
				return f"Deleted {count} comment(s)."
			if action == "like":
				created_count = 0
				for comment in qs:
					_, created = CommentReaction.objects.get_or_create(user=user, comment=comment, reaction=CommentReaction.LOVE)
					if created:
						created_count += 1
				return f"Added {created_count} like reaction(s) on comments."
			if action == "unlike":
				count, _ = CommentReaction.objects.filter(user=user, comment__in=qs, reaction=CommentReaction.LOVE).delete()
				return f"Removed {count} like reaction(s) from comments."
			if action == "flag":
				count = self._flag_comments(user, qs)
				return f"Flagged {count} comment(s)."

		if tab == "reactions":
			qs = PostReaction.objects.filter(user=user, reaction=PostReaction.LOVE, id__in=selected_ids)
			if action == "unlike":
				count = qs.count()
				qs.delete()
				return f"Removed {count} reaction(s)."
			if action == "flag":
				posts = Post.objects.filter(reactions__in=qs).distinct()
				count = self._flag_posts(user, posts)
				return f"Flagged {count} post(s) from selected reactions."

		if tab == "reports":
			qs = Report.objects.filter(reporter=user, id__in=selected_ids)
			if action == "delete":
				count = qs.count()
				qs.delete()
				return f"Deleted {count} report(s)."
			if action == "block_reported_users":
				blocked_count = 0
				for report in qs.select_related("reported_user"):
					if report.reported_user and report.reported_user != user:
						_, created = UserBlock.objects.get_or_create(blocker=user, blocked=report.reported_user)
						if created:
							blocked_count += 1
				return f"Blocked {blocked_count} user(s) from selected reports."

		return "No valid batch action was selected for this tab."

	def post(self, request):
		tab = request.POST.get("tab", "posts")
		if tab not in self.TABS:
			tab = "posts"
		action = request.POST.get("batch_action", "")
		selected_ids = [int(item) for item in request.POST.getlist("selected_ids") if item.isdigit()]

		if not selected_ids:
			messages.warning(request, "Select at least one row to run a batch action.")
		elif not action:
			messages.warning(request, "Choose a batch action first.")
		else:
			message = self._run_batch_action(request, tab, action, selected_ids)
			success(request, message)

		params = request.POST.copy()
		for key in ["csrfmiddlewaretoken", "selected_ids", "batch_action"]:
			params.pop(key, None)
		query = params.urlencode()
		base = reverse("blog:dashboard")
		return redirect(f"{base}?{query}" if query else base)

	def get(self, request):
		tab = request.GET.get("tab", "posts")
		if tab not in self.TABS:
			tab = "posts"
		search_q = get_search_query(request)
		page_num = request.GET.get("page", "1")

		counts = self._build_counts(request.user)
		qs = self._get_tab_queryset(request, tab, search_q)

		page_obj = Paginator(qs, self.paginate_by).get_page(page_num)
		params = request.GET.copy()
		params.pop("page", None)
		page_query_string = params.urlencode()
		persisted_query_items = [(key, value) for key, value in params.items()]

		available_actions = []
		if tab == "posts":
			available_actions = [
				("publish", "Publish"),
				("unpublish", "Unpublish"),
				("like", "Like"),
				("unlike", "Unlike"),
				("flag", "Flag"),
				("delete", "Delete"),
			]
		elif tab == "channels":
			available_actions = [
				("suspend", "Suspend"),
				("unsuspend", "Unsuspend"),
				("disable_comments", "Disable comments"),
				("enable_comments", "Enable comments"),
				("flag", "Flag"),
				("delete", "Delete"),
			]
		elif tab == "comments":
			available_actions = [
				("like", "Like"),
				("unlike", "Unlike"),
				("flag", "Flag"),
				("delete", "Delete"),
			]
		elif tab == "reactions":
			available_actions = [
				("unlike", "Unlike"),
				("flag", "Flag related posts"),
			]
		elif tab == "reports":
			available_actions = [
				("block_reported_users", "Block reported users"),
				("delete", "Delete"),
			]

		context = {
			"tab": tab,
			"tabs": self.TABS,
			"counts": counts,
			"page_obj": page_obj,
			"is_paginated": page_obj.has_other_pages(),
			"page_query_string": page_query_string,
			"persisted_query_items": persisted_query_items,
			"available_actions": available_actions,
			"owned_channels": Channel.objects.filter(owner=request.user).order_by("name"),
			"search_query": search_q,
			"state": request.GET.get("state", "all") if tab == "posts" else None,
			"date_scope": request.GET.get("date_scope", "all"),
			"day": request.GET.get("day", ""),
			"month": request.GET.get("month", ""),
			"year": request.GET.get("year", ""),
			"duration_days": request.GET.get("duration_days", ""),
			"start_date": request.GET.get("start_date", ""),
			"end_date": request.GET.get("end_date", ""),
			"channel_id": request.GET.get("channel_id", ""),
			"min_comment_count": request.GET.get("min_comment_count", ""),
			"max_comment_count": request.GET.get("max_comment_count", ""),
			"min_flag_count": request.GET.get("min_flag_count", ""),
			"max_flag_count": request.GET.get("max_flag_count", ""),
			"min_like_count": request.GET.get("min_like_count", ""),
			"max_like_count": request.GET.get("max_like_count", ""),
			"min_follower_count": request.GET.get("min_follower_count", ""),
			"max_follower_count": request.GET.get("max_follower_count", ""),
			"min_posts_count": request.GET.get("min_posts_count", ""),
			"max_posts_count": request.GET.get("max_posts_count", ""),
			"status": request.GET.get("status", ""),
			"reason": request.GET.get("reason", ""),
			"content_type": request.GET.get("content_type", ""),
			"report_status_choices": Report.STATUS_CHOICES,
			"report_reason_choices": Report.REASON_CHOICES,
			"report_content_choices": Report.CONTENT_CHOICES,
		}
		return render(request, self.template_name, context)


class AccountDeleteView(LoginRequiredMixin, View):
	template_name = "blog/account_confirm_delete.html"

	def get(self, request):
		return render(request, self.template_name)

	def post(self, request):
		user = request.user
		logout(request)
		user.delete()
		return redirect("home")


class FollowUserView(LoginRequiredMixin, View):
	def post(self, request, username):
		target_user = get_object_or_404(User, username=username)
		suspension_reason = get_user_suspension_reason(request.user)
		if suspension_reason:
			messages.error(request, suspension_reason)
			return redirect("blog:user-profile", username=username)
		if are_users_blocked(request.user, target_user):
			messages.error(request, "Follow is unavailable because one of the users has blocked the other.")
			return redirect("blog:user-profile", username=username)
		if target_user != request.user:
			_, created = UserFollow.objects.get_or_create(follower=request.user, following=target_user)
			if created:
				create_notification(
					recipient=target_user,
					actor=request.user,
					notification_type=Notification.TYPE_FOLLOW,
					message=f"{request.user.username} started following you.",
					target_url=f"/users/{request.user.username}/",
				)
		next_url = request.POST.get("next", "")
		if next_url and url_has_allowed_host_and_scheme(
			next_url,
			allowed_hosts={request.get_host()},
			require_https=request.is_secure(),
		):
			return redirect(next_url)
		return redirect("blog:user-profile", username=username)


class UnfollowUserView(LoginRequiredMixin, View):
	def post(self, request, username):
		target_user = get_object_or_404(User, username=username)
		UserFollow.objects.filter(follower=request.user, following=target_user).delete()
		next_url = request.POST.get("next", "")
		if next_url and url_has_allowed_host_and_scheme(
			next_url,
			allowed_hosts={request.get_host()},
			require_https=request.is_secure(),
		):
			return redirect(next_url)
		return redirect("blog:user-profile", username=username)


class BlockUserView(LoginRequiredMixin, View):
	def post(self, request, username):
		target_user = get_object_or_404(User, username=username)
		if target_user != request.user:
			UserBlock.objects.get_or_create(blocker=request.user, blocked=target_user)
			# A block implies no active follow relationship in either direction.
			UserFollow.objects.filter(follower=request.user, following=target_user).delete()
			UserFollow.objects.filter(follower=target_user, following=request.user).delete()
		next_url = request.POST.get("next", "")
		if next_url and url_has_allowed_host_and_scheme(
			next_url,
			allowed_hosts={request.get_host()},
			require_https=request.is_secure(),
		):
			return redirect(next_url)
		return redirect("blog:user-profile", username=username)


class UnblockUserView(LoginRequiredMixin, View):
	def post(self, request, username):
		target_user = get_object_or_404(User, username=username)
		UserBlock.objects.filter(blocker=request.user, blocked=target_user).delete()
		next_url = request.POST.get("next", "")
		if next_url and url_has_allowed_host_and_scheme(
			next_url,
			allowed_hosts={request.get_host()},
			require_https=request.is_secure(),
		):
			return redirect(next_url)
		return redirect("blog:user-profile", username=username)


class FollowUserView(LoginRequiredMixin, View):
	def post(self, request, username):
		target_user = get_object_or_404(User, username=username)
		suspension_reason = get_user_suspension_reason(request.user)
		if suspension_reason:
			messages.error(request, suspension_reason)
			return redirect("blog:user-profile", username=username)
		if are_users_blocked(request.user, target_user):
			messages.error(request, "Follow is unavailable because one of the users has blocked the other.")
			return redirect("blog:user-profile", username=username)
		if target_user != request.user:
			_, created = UserFollow.objects.get_or_create(follower=request.user, following=target_user)
			if created:
				create_notification(
					recipient=target_user,
					actor=request.user,
					notification_type=Notification.TYPE_FOLLOW,
					message=f"{request.user.username} started following you.",
					target_url=f"/users/{request.user.username}/",
				)
		next_url = request.POST.get("next", "")
		if next_url and url_has_allowed_host_and_scheme(
			next_url,
			allowed_hosts={request.get_host()},
			require_https=request.is_secure(),
		):
			return redirect(next_url)
		return redirect("blog:user-profile", username=username)


class UnfollowUserView(LoginRequiredMixin, View):
	def post(self, request, username):
		target_user = get_object_or_404(User, username=username)
		UserFollow.objects.filter(follower=request.user, following=target_user).delete()
		next_url = request.POST.get("next", "")
		if next_url and url_has_allowed_host_and_scheme(
			next_url,
			allowed_hosts={request.get_host()},
			require_https=request.is_secure(),
		):
			return redirect(next_url)
		return redirect("blog:user-profile", username=username)


class FollowChannelView(LoginRequiredMixin, View):
	def post(self, request, channel_slug):
		channel = get_object_or_404(Channel, slug=channel_slug)
		suspension_reason = get_user_suspension_reason(request.user)
		if suspension_reason:
			messages.error(request, suspension_reason)
			return redirect(channel.get_absolute_url())
		channel_suspension = get_channel_suspension_reason(channel)
		if channel_suspension:
			messages.error(request, channel_suspension)
			return redirect(channel.get_absolute_url())
		if are_users_blocked(request.user, channel.owner):
			messages.error(request, "Follow is unavailable because one of the users has blocked the other.")
			return redirect(channel.get_absolute_url())
		if channel.owner != request.user:
			_, created = ChannelFollow.objects.get_or_create(follower=request.user, channel=channel)
			if created:
				create_notification(
					recipient=channel.owner,
					actor=request.user,
					notification_type=Notification.TYPE_FOLLOW,
					message=f"{request.user.username} followed your channel {channel.name}.",
					target_url=channel.get_absolute_url(),
				)
		next_url = request.POST.get("next", "")
		if next_url and url_has_allowed_host_and_scheme(
			next_url,
			allowed_hosts={request.get_host()},
			require_https=request.is_secure(),
		):
			return redirect(next_url)
		return redirect("blog:channel-list")


class UnfollowChannelView(LoginRequiredMixin, View):
	def post(self, request, channel_slug):
		channel = get_object_or_404(Channel, slug=channel_slug)
		ChannelFollow.objects.filter(follower=request.user, channel=channel).delete()
		next_url = request.POST.get("next", "")
		if next_url and url_has_allowed_host_and_scheme(
			next_url,
			allowed_hosts={request.get_host()},
			require_https=request.is_secure(),
		):
			return redirect(next_url)
		return redirect("blog:channel-list")


class SavePostView(LoginRequiredMixin, View):
	def post(self, request, channel_slug, post_slug):
		post_obj = get_object_or_404(get_visible_posts_queryset(request.user), channel__slug=channel_slug, slug=post_slug)
		suspension_reason = get_user_suspension_reason(request.user)
		if suspension_reason:
			messages.error(request, suspension_reason)
			return redirect(post_obj.get_absolute_url())
		if are_users_blocked(request.user, post_obj.author) or are_users_blocked(request.user, post_obj.channel.owner):
			messages.error(request, "Save is unavailable because one of the users has blocked the other.")
			return redirect(post_obj.get_absolute_url())
		SavedPost.objects.get_or_create(user=request.user, post=post_obj)
		next_url = request.POST.get("next", "")
		if next_url and url_has_allowed_host_and_scheme(
			next_url,
			allowed_hosts={request.get_host()},
			require_https=request.is_secure(),
		):
			return redirect(next_url)
		return redirect("blog:saved-posts")


class UnsavePostView(LoginRequiredMixin, View):
	def post(self, request, channel_slug, post_slug):
		post_obj = get_object_or_404(get_visible_posts_queryset(request.user), channel__slug=channel_slug, slug=post_slug)
		SavedPost.objects.filter(user=request.user, post=post_obj).delete()
		next_url = request.POST.get("next", "")
		if next_url and url_has_allowed_host_and_scheme(
			next_url,
			allowed_hosts={request.get_host()},
			require_https=request.is_secure(),
		):
			return redirect(next_url)
		return redirect("blog:saved-posts")


class LovePostView(LoginRequiredMixin, View):
	def post(self, request, channel_slug, post_slug):
		post_obj = get_object_or_404(get_visible_posts_queryset(request.user), channel__slug=channel_slug, slug=post_slug)
		suspension_reason = get_user_suspension_reason(request.user)
		if suspension_reason:
			messages.error(request, suspension_reason)
			return redirect(post_obj.get_absolute_url())
		if are_users_blocked(request.user, post_obj.author) or are_users_blocked(request.user, post_obj.channel.owner):
			messages.error(request, "Reaction is unavailable because one of the users has blocked the other.")
			return redirect(post_obj.get_absolute_url())
		PostReaction.objects.get_or_create(user=request.user, post=post_obj, reaction=PostReaction.LOVE)
		next_url = request.POST.get("next", "")
		if next_url and url_has_allowed_host_and_scheme(
			next_url,
			allowed_hosts={request.get_host()},
			require_https=request.is_secure(),
		):
			return redirect(next_url)
		return redirect("blog:post-detail", channel_slug=channel_slug, post_slug=post_slug)


class UnlovePostView(LoginRequiredMixin, View):
	def post(self, request, channel_slug, post_slug):
		post_obj = get_object_or_404(get_visible_posts_queryset(request.user), channel__slug=channel_slug, slug=post_slug)
		PostReaction.objects.filter(user=request.user, post=post_obj, reaction=PostReaction.LOVE).delete()
		next_url = request.POST.get("next", "")
		if next_url and url_has_allowed_host_and_scheme(
			next_url,
			allowed_hosts={request.get_host()},
			require_https=request.is_secure(),
		):
			return redirect(next_url)
		return redirect("blog:post-detail", channel_slug=channel_slug, post_slug=post_slug)


class LoveCommentView(LoginRequiredMixin, View):
	def post(self, request, pk):
		comment_obj = get_object_or_404(Comment, pk=pk)
		suspension_reason = get_user_suspension_reason(request.user)
		if suspension_reason:
			messages.error(request, suspension_reason)
			return redirect(comment_obj.post.get_absolute_url())
		if are_users_blocked(request.user, comment_obj.author) or are_users_blocked(request.user, comment_obj.post.author):
			messages.error(request, "Reaction is unavailable because one of the users has blocked the other.")
			return redirect(comment_obj.post.get_absolute_url())
		CommentReaction.objects.get_or_create(user=request.user, comment=comment_obj, reaction=CommentReaction.LOVE)
		next_url = request.POST.get("next", "")
		if next_url and url_has_allowed_host_and_scheme(
			next_url,
			allowed_hosts={request.get_host()},
			require_https=request.is_secure(),
		):
			return redirect(next_url)
		return redirect("blog:post-detail", channel_slug=comment_obj.post.channel.slug, post_slug=comment_obj.post.slug)


class UnloveCommentView(LoginRequiredMixin, View):
	def post(self, request, pk):
		comment_obj = get_object_or_404(Comment, pk=pk)
		CommentReaction.objects.filter(user=request.user, comment=comment_obj, reaction=CommentReaction.LOVE).delete()
		next_url = request.POST.get("next", "")
		if next_url and url_has_allowed_host_and_scheme(
			next_url,
			allowed_hosts={request.get_host()},
			require_https=request.is_secure(),
		):
			return redirect(next_url)
		return redirect("blog:post-detail", channel_slug=comment_obj.post.channel.slug, post_slug=comment_obj.post.slug)


class NotificationMarkReadView(LoginRequiredMixin, View):
	def post(self, request, pk):
		notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
		notification.is_read = True
		notification.save(update_fields=["is_read"])
		next_url = request.POST.get("next", "")
		if next_url and url_has_allowed_host_and_scheme(
			next_url,
			allowed_hosts={request.get_host()},
			require_https=request.is_secure(),
		):
			return redirect(next_url)
		return redirect("blog:notifications")


class NotificationMarkAllReadView(LoginRequiredMixin, View):
	def post(self, request):
		Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
		next_url = request.POST.get("next", "")
		if next_url and url_has_allowed_host_and_scheme(
			next_url,
			allowed_hosts={request.get_host()},
			require_https=request.is_secure(),
		):
			return redirect(next_url)
		return redirect("blog:notifications")


class ChannelCreateView(LoginRequiredMixin, CreateView):
	model = Channel
	form_class = ChannelForm
	template_name = "blog/channel_form.html"
	success_url = reverse_lazy("blog:channel-list")

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs["instance"] = Channel(owner=self.request.user)
		return kwargs

	def dispatch(self, request, *args, **kwargs):
		suspension_reason = get_user_suspension_reason(request.user)
		if suspension_reason:
			messages.error(request, suspension_reason)
			return redirect("blog:channel-list")
		return super().dispatch(request, *args, **kwargs)


class ChannelUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
	model = Channel
	form_class = ChannelForm
	template_name = "blog/channel_form.html"
	slug_field = "slug"
	slug_url_kwarg = "slug"
	success_url = reverse_lazy("blog:channel-list")


class ChannelToggleCommentsView(LoginRequiredMixin, View):
	def post(self, request, channel_slug):
		channel = get_object_or_404(Channel, slug=channel_slug, owner=request.user)
		channel.comments_enabled = not channel.comments_enabled
		channel.save(update_fields=["comments_enabled"])
		status = "enabled" if channel.comments_enabled else "disabled"
		success(request, f"Comments {status} for this channel.")
		return redirect(channel.get_absolute_url())


# ── Co-authorship: Post ───────────────────────────────────────────────────────

class PostInviteCoAuthorView(LoginRequiredMixin, View):
	"""Channel owner invites another user to co-author a specific post."""

	def post(self, request, channel_slug, post_slug):
		post = get_object_or_404(Post, channel__slug=channel_slug, slug=post_slug)
		if post.channel.owner != request.user:
			raise PermissionDenied
		username = request.POST.get("username", "").strip()
		invitee = get_object_or_404(User, username=username)
		if invitee == request.user:
			messages.error(request, "You cannot invite yourself as a co-author.")
			return redirect(post.get_absolute_url())
		if invitee == post.author:
			messages.error(request, "This user is already the post author.")
			return redirect(post.get_absolute_url())
		obj, created = PostCoAuthor.objects.get_or_create(
			post=post, user=invitee,
			defaults={"invited_by": request.user, "accepted": None},
		)
		if not created:
			messages.warning(request, f"{invitee.username} has already been invited or is already a co-author.")
		else:
			create_notification(
				recipient=invitee,
				actor=request.user,
				notification_type=Notification.TYPE_COAUTHOR_INVITE,
				message=f"{request.user.username} invited you to co-author: {post.title}.",
				target_url=post.get_absolute_url(),
			)
			success(request, f"Invitation sent to {invitee.username}.")
		return redirect(post.get_absolute_url())


class PostRespondCoAuthorView(LoginRequiredMixin, View):
	"""Invitee accepts or declines a co-author invitation for a post."""

	def post(self, request, pk):
		invite = get_object_or_404(PostCoAuthor, pk=pk, user=request.user, accepted=None)
		action = request.POST.get("action")
		if action == "accept":
			invite.accepted = True
			invite.save(update_fields=["accepted"])
			create_notification(
				recipient=invite.invited_by,
				actor=request.user,
				notification_type=Notification.TYPE_COAUTHOR_ACCEPTED,
				message=f"{request.user.username} accepted your co-author invitation for: {invite.post.title}.",
				target_url=invite.post.get_absolute_url(),
			)
			success(request, f"You are now a co-author of \"{invite.post.title}\".")
			return redirect(invite.post.get_absolute_url())
		elif action == "decline":
			invite.accepted = False
			invite.save(update_fields=["accepted"])
			success(request, "Invitation declined.")
		return redirect(reverse("blog:notifications"))


class PostRemoveCoAuthorView(LoginRequiredMixin, View):
	"""Channel owner removes a co-author from a post."""

	def post(self, request, pk):
		invite = get_object_or_404(PostCoAuthor, pk=pk)
		post = invite.post
		if post.channel.owner != request.user:
			raise PermissionDenied
		username = invite.user.username
		invite.delete()
		success(request, f"{username} removed from co-authors.")
		return redirect(post.get_absolute_url())


# ── Co-authorship: Channel editors ───────────────────────────────────────────

class ChannelInviteEditorView(LoginRequiredMixin, View):
	"""Channel owner invites another user as a channel editor."""

	def post(self, request, channel_slug):
		channel = get_object_or_404(Channel, slug=channel_slug, owner=request.user)
		username = request.POST.get("username", "").strip()
		invitee = get_object_or_404(User, username=username)
		if invitee == request.user:
			messages.error(request, "You cannot invite yourself as an editor.")
			return redirect(channel.get_absolute_url())
		obj, created = ChannelEditor.objects.get_or_create(
			channel=channel, user=invitee,
			defaults={"invited_by": request.user, "accepted": None},
		)
		if not created:
			messages.warning(request, f"{invitee.username} has already been invited or is already an editor.")
		else:
			create_notification(
				recipient=invitee,
				actor=request.user,
				notification_type=Notification.TYPE_EDITOR_INVITE,
				message=f"{request.user.username} invited you to be an editor of channel: {channel.name}.",
				target_url=channel.get_absolute_url(),
			)
			success(request, f"Invitation sent to {invitee.username}.")
		return redirect(channel.get_absolute_url())


class ChannelRespondEditorView(LoginRequiredMixin, View):
	"""Invitee accepts or declines a channel editor invitation."""

	def post(self, request, pk):
		invite = get_object_or_404(ChannelEditor, pk=pk, user=request.user, accepted=None)
		action = request.POST.get("action")
		if action == "accept":
			invite.accepted = True
			invite.save(update_fields=["accepted"])
			create_notification(
				recipient=invite.invited_by,
				actor=request.user,
				notification_type=Notification.TYPE_EDITOR_ACCEPTED,
				message=f"{request.user.username} accepted your editor invitation for channel: {invite.channel.name}.",
				target_url=invite.channel.get_absolute_url(),
			)
			success(request, f"You are now an editor of \"{invite.channel.name}\".")
			return redirect(invite.channel.get_absolute_url())
		elif action == "decline":
			invite.accepted = False
			invite.save(update_fields=["accepted"])
			success(request, "Invitation declined.")
		return redirect(reverse("blog:notifications"))


class ChannelRemoveEditorView(LoginRequiredMixin, View):
	"""Channel owner removes an editor from a channel."""

	def post(self, request, pk):
		invite = get_object_or_404(ChannelEditor, pk=pk)
		channel = invite.channel
		if channel.owner != request.user:
			raise PermissionDenied
		username = invite.user.username
		invite.delete()
		success(request, f"{username} removed from editors.")
		return redirect(channel.get_absolute_url())


class ChannelDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
	model = Channel
	template_name = "blog/channel_confirm_delete.html"
	slug_field = "slug"
	slug_url_kwarg = "slug"
	success_url = reverse_lazy("blog:channel-list")


class PostListView(SearchContextMixin, LoginRequiredMixin, ListView):
	model = Post
	template_name = "blog/post_list.html"
	context_object_name = "posts"
	paginate_by = 10
	search_fields = ("title", "body", "author__username")

	def dispatch(self, request, *args, **kwargs):
		self.channel = get_object_or_404(Channel, slug=self.kwargs["channel_slug"])
		return super().dispatch(request, *args, **kwargs)

	def get_queryset(self):
		queryset = (
			Post.objects.filter(channel=self.channel, is_published=True)
			.select_related("author", "channel", "channel__owner")
			.order_by("-created_at")
		)
		return self.apply_search(queryset)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["channel"] = self.channel
		context["saved_post_ids"] = build_saved_post_ids(self.request.user, context.get("posts", []))
		return context


class DraftPostListView(SearchContextMixin, LoginRequiredMixin, ListView):
	model = Post
	template_name = "blog/draft_post_list.html"
	context_object_name = "posts"
	paginate_by = 10
	search_fields = ("title", "body", "channel__name")

	def get_queryset(self):
		queryset = (
			Post.objects.filter(author=self.request.user, is_published=False)
			.select_related("author", "channel", "channel__owner")
			.order_by("-created_at")
		)
		return self.apply_search(queryset)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["saved_post_ids"] = build_saved_post_ids(self.request.user, context.get("posts", []))
		return context


class TagPostListView(SearchContextMixin, ListView):
	model = Post
	template_name = "blog/tag_post_list.html"
	context_object_name = "posts"
	paginate_by = 10
	search_fields = ("title", "body", "author__username")

	def dispatch(self, request, *args, **kwargs):
		self.tag = get_object_or_404(Tag, slug=self.kwargs["tag_slug"])
		return super().dispatch(request, *args, **kwargs)

	def get_queryset(self):
		queryset = (
			Post.objects.filter(tags=self.tag, is_published=True)
			.select_related("author", "channel", "channel__owner")
			.prefetch_related("tags")
			.order_by("-created_at")
		)
		return self.apply_search(queryset)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		related_tags = (
			Tag.objects.filter(posts__in=self.object_list)
			.exclude(pk=self.tag.pk)
			.annotate(
				post_count=Count("posts", filter=Q(posts__is_published=True), distinct=True),
				latest_post_at=Max("posts__created_at", filter=Q(posts__is_published=True)),
			)
			.order_by("-post_count", "-latest_post_at", "name")
			.distinct()[:10]
		)
		popular_tags = (
			Tag.objects.filter(posts__is_published=True)
			.annotate(
				post_count=Count("posts", filter=Q(posts__is_published=True), distinct=True),
				latest_post_at=Max("posts__created_at", filter=Q(posts__is_published=True)),
			)
			.order_by("-post_count", "-latest_post_at", "name")
			.distinct()[:12]
		)
		context["tag"] = self.tag
		context["tag_post_count"] = self.object_list.paginator.count if hasattr(self.object_list, "paginator") else len(self.object_list)
		context["related_tags"] = related_tags
		context["popular_tags"] = popular_tags
		context["saved_post_ids"] = build_saved_post_ids(self.request.user, context.get("posts", []))
		return context


class TagListView(SearchContextMixin, ListView):
	model = Tag
	template_name = "blog/tag_list.html"
	context_object_name = "tags"
	paginate_by = 24
	search_fields = ("name",)

	def get_queryset(self):
		queryset = (
			Tag.objects.filter(posts__is_published=True)
			.annotate(
				post_count=Count("posts", filter=Q(posts__is_published=True), distinct=True),
				latest_post_at=Max("posts__created_at", filter=Q(posts__is_published=True)),
			)
			.order_by("-post_count", "-latest_post_at", "name")
			.distinct()
		)
		return self.apply_search(queryset)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		base_queryset = self.get_queryset()
		context["featured_tags"] = list(base_queryset[:8])
		context["tag_count"] = base_queryset.count()
		return context


class PostDetailView(DetailView):
	model = Post
	template_name = "blog/post_detail.html"
	context_object_name = "post"
	slug_field = "slug"
	slug_url_kwarg = "post_slug"

	def get_queryset(self):
		return (
			Post.objects.select_related("channel", "channel__owner", "author")
			.prefetch_related("comments__author")
			.filter(channel__slug=self.kwargs["channel_slug"])
			.filter(get_visible_post_filter(self.request.user))
		)

	def get_object(self, queryset=None):
		obj = super().get_object(queryset)
		Post.objects.filter(pk=obj.pk).update(view_count=F("view_count") + 1)
		obj.view_count += 1
		return obj

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		post = self.object
		user = self.request.user
		comment_page_number = self.request.GET.get("comment_page", "1")
		if user.is_authenticated:
			user_comment = post.comments.filter(author=user).first()
			other_comments_queryset = post.comments.exclude(author=user).order_by("-created_at")
		else:
			user_comment = None
			other_comments_queryset = post.comments.order_by("-created_at")

		other_comments_page = Paginator(other_comments_queryset, 10).get_page(comment_page_number)
		other_comments = list(other_comments_page.object_list)
		context["user_comment"] = user_comment
		context["other_comments"] = other_comments
		context["comment_page_obj"] = other_comments_page
		context["comments_is_paginated"] = other_comments_page.has_other_pages()
		context["comments_page_query_string"] = build_query_with_params(self.request, comment_page=None)
		context["is_post_saved"] = user.is_authenticated and SavedPost.objects.filter(user=user, post=post).exists()
		context["love_count"] = post.love_count
		context["is_post_loved"] = user.is_authenticated and post.reactions.filter(user=user, reaction=PostReaction.LOVE).exists()
		context["has_reported_post"] = user.is_authenticated and Report.objects.filter(reporter=user, post=post).exists()
		context["commenting_disabled_reason"] = get_post_commenting_disabled_reason(user, post)
		context["can_comment"] = not bool(context["commenting_disabled_reason"])
		
		# Build comment user loves for template
		all_comments = []
		if user_comment:
			all_comments.append(user_comment)
		all_comments.extend(list(other_comments))
		
		if all_comments and user.is_authenticated:
			comment_ids = [c.id for c in all_comments]
			reported_comment_ids = set(
				Report.objects.filter(
					reporter=user,
					comment_id__in=comment_ids,
				).values_list("comment_id", flat=True)
			)
			user_loved = set(
				CommentReaction.objects.filter(
					user=user, comment_id__in=comment_ids, reaction=CommentReaction.LOVE
				).values_list('comment_id', flat=True)
			)
			for comment in all_comments:
				comment.user_loved = comment.id in user_loved
				comment.user_reported = comment.id in reported_comment_ids
		else:
			reported_comment_ids = set()
		
		context["user_loved_comments"] = {c.id for c in all_comments if getattr(c, 'user_loved', False)}
		context["reported_comment_ids"] = reported_comment_ids
		# Co-authors
		context["post_coauthors"] = PostCoAuthor.objects.filter(
			post=post, accepted=True
		).select_related("user")
		if post.channel.owner == user:
			context["post_coauthor_invites"] = PostCoAuthor.objects.filter(
				post=post, accepted=None
			).select_related("user")
		else:
			context["post_coauthor_invites"] = PostCoAuthor.objects.none()
		context["is_post_coauthor"] = user.is_authenticated and PostCoAuthor.objects.filter(
			post=post, user=user, accepted=True
		).exists()
		if user.is_authenticated:
			context["my_coauthor_invite"] = PostCoAuthor.objects.filter(
				post=post, user=user, accepted=None
			).first()
		else:
			context["my_coauthor_invite"] = None
		return context


class PostFocusView(DetailView):
	model = Post
	template_name = "blog/post_focus_view.html"
	context_object_name = "post"
	slug_field = "slug"
	slug_url_kwarg = "post_slug"

	def get_queryset(self):
		return (
			Post.objects.select_related("channel", "author")
			.filter(channel__slug=self.kwargs["channel_slug"])
			.filter(get_visible_post_filter(self.request.user))
		)

	def get_object(self, queryset=None):
		obj = super().get_object(queryset)
		Post.objects.filter(pk=obj.pk).update(view_count=F("view_count") + 1)
		obj.view_count += 1
		return obj


class PostCreateView(LoginRequiredMixin, CreateView):
	model = Post
	form_class = PostForm
	template_name = "blog/post_form.html"

	def dispatch(self, request, *args, **kwargs):
		self.channel = get_object_or_404(Channel, slug=self.kwargs["channel_slug"])
		suspension_reason = get_user_suspension_reason(request.user)
		if suspension_reason:
			messages.error(request, suspension_reason)
			return redirect(self.channel.get_absolute_url())
		channel_suspension = get_channel_suspension_reason(self.channel)
		if channel_suspension:
			messages.error(request, channel_suspension)
			return redirect(self.channel.get_absolute_url())
		if self.channel.owner_id != request.user.id:
			is_editor = ChannelEditor.objects.filter(channel=self.channel, user=request.user, accepted=True).exists()
			if not is_editor:
				raise PermissionDenied("Only the channel owner or an accepted editor can create posts in this channel.")
		return super().dispatch(request, *args, **kwargs)

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs["instance"] = Post(channel=self.channel, author=self.request.user)
		return kwargs

	def get_success_url(self):
		if self.object.is_published:
			return reverse_lazy("blog:post-detail", kwargs={"channel_slug": self.channel.slug, "post_slug": self.object.slug})
		return reverse_lazy("blog:draft-posts")

	def form_valid(self, form):
		action = self.request.POST.get("action", "publish")
		form.instance.is_published = action == "publish"
		response = super().form_valid(form)
		save_post_tags(self.object, form)
		if not self.object.is_published:
			return response
		notified_ids = set()
		channel_followers = User.objects.filter(channel_follows__channel=self.channel).exclude(pk=self.request.user.pk).distinct()
		for follower in channel_followers:
			create_notification(
				recipient=follower,
				actor=self.request.user,
				notification_type=Notification.TYPE_NEW_POST,
				message=f"{self.request.user.username} published a new post: {self.object.title}.",
				target_url=self.object.get_absolute_url(),
			)
			notified_ids.add(follower.pk)
		# Also notify users who follow the author directly (dedup)
		user_followers = (
			User.objects.filter(user_following__following=self.request.user)
			.exclude(pk=self.request.user.pk)
			.exclude(pk__in=notified_ids)
			.distinct()
		)
		for follower in user_followers:
			create_notification(
				recipient=follower,
				actor=self.request.user,
				notification_type=Notification.TYPE_NEW_POST,
				message=f"{self.request.user.username} published a new post: {self.object.title}.",
				target_url=self.object.get_absolute_url(),
			)
		return response


class PostUpdateView(LoginRequiredMixin, ChannelPostOwnerRequiredMixin, UpdateView):
	model = Post
	form_class = PostForm
	template_name = "blog/post_form.html"
	slug_field = "slug"
	slug_url_kwarg = "post_slug"

	def get_queryset(self):
		return Post.objects.select_related("channel", "channel__owner").filter(channel__slug=self.kwargs["channel_slug"])

	def get_success_url(self):
		if self.object.is_published:
			return reverse_lazy("blog:post-detail", kwargs={"channel_slug": self.object.channel.slug, "post_slug": self.object.slug})
		return reverse_lazy("blog:draft-posts")

	def form_valid(self, form):
		post_obj = self.get_object()
		suspension_reason = get_user_suspension_reason(self.request.user)
		if suspension_reason:
			messages.error(self.request, suspension_reason)
			return redirect(post_obj.get_absolute_url())
		channel_suspension = get_channel_suspension_reason(post_obj.channel)
		if channel_suspension:
			messages.error(self.request, channel_suspension)
			return redirect(post_obj.get_absolute_url())
		was_published = post_obj.is_published
		action = self.request.POST.get("action", "publish")
		form.instance.is_published = action == "publish"
		response = super().form_valid(form)
		save_post_tags(self.object, form)
		if self.object.is_published and not was_published:
			notified_ids = set()
			channel_followers = User.objects.filter(channel_follows__channel=self.object.channel).exclude(pk=self.request.user.pk).distinct()
			for follower in channel_followers:
				create_notification(
					recipient=follower,
					actor=self.request.user,
					notification_type=Notification.TYPE_NEW_POST,
					message=f"{self.request.user.username} published a new post: {self.object.title}.",
					target_url=self.object.get_absolute_url(),
				)
				notified_ids.add(follower.pk)
			user_followers = (
				User.objects.filter(user_following__following=self.request.user)
				.exclude(pk=self.request.user.pk)
				.exclude(pk__in=notified_ids)
				.distinct()
			)
			for follower in user_followers:
				create_notification(
					recipient=follower,
					actor=self.request.user,
					notification_type=Notification.TYPE_NEW_POST,
					message=f"{self.request.user.username} published a new post: {self.object.title}.",
					target_url=self.object.get_absolute_url(),
				)
		return response


class PostDeleteView(LoginRequiredMixin, ChannelPostOwnerRequiredMixin, DeleteView):
	model = Post
	template_name = "blog/post_confirm_delete.html"
	slug_field = "slug"
	slug_url_kwarg = "post_slug"

	def get_queryset(self):
		return Post.objects.select_related("channel", "channel__owner").filter(channel__slug=self.kwargs["channel_slug"])

	def get_success_url(self):
		return reverse_lazy("blog:post-list", kwargs={"channel_slug": self.object.channel.slug})


class CommentCreateView(LoginRequiredMixin, CreateView):
	model = Comment
	form_class = CommentForm
	template_name = "blog/comment_form.html"

	def dispatch(self, request, *args, **kwargs):
		self.post_obj = get_object_or_404(
			get_visible_posts_queryset(request.user),
			channel__slug=self.kwargs["channel_slug"],
			slug=self.kwargs["post_slug"],
		)
		suspension_reason = get_user_suspension_reason(request.user)
		if suspension_reason:
			messages.error(request, suspension_reason)
			return redirect(self.post_obj.get_absolute_url())
		comment_restriction_reason = get_comment_restriction_reason(request.user)
		if comment_restriction_reason:
			messages.error(request, comment_restriction_reason)
			return redirect(self.post_obj.get_absolute_url())
		if not self.post_obj.channel.comments_enabled:
			messages.error(request, "Comments are disabled for this channel.")
			return redirect(self.post_obj.get_absolute_url())
		if are_users_blocked(request.user, self.post_obj.author) or are_users_blocked(request.user, self.post_obj.channel.owner):
			messages.error(request, "Commenting is unavailable because one of the users has blocked the other.")
			return redirect(self.post_obj.get_absolute_url())
		return super().dispatch(request, *args, **kwargs)

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs["instance"] = Comment(post=self.post_obj, author=self.request.user)
		return kwargs

	def form_valid(self, form):
		try:
			response = super().form_valid(form)
			recipients = []
			if self.post_obj.author_id != self.request.user.id:
				recipients.append(
					(
						self.post_obj.author,
						f"{self.request.user.username} commented on your post: {self.post_obj.title}.",
					)
				)

			channel_owner = self.post_obj.channel.owner
			if (
				channel_owner.id != self.request.user.id
				and channel_owner.id != self.post_obj.author_id
			):
				recipients.append(
					(
						channel_owner,
						f"{self.request.user.username} commented on a post in your channel: {self.post_obj.title}.",
					)
				)

			for recipient, message in recipients:
				create_notification(
					recipient=recipient,
					actor=self.request.user,
					notification_type=Notification.TYPE_COMMENT,
					message=message,
					target_url=self.post_obj.get_absolute_url(),
				)
			return response
		except ValidationError as exc:
			if hasattr(exc, "message_dict"):
				for field, errors in exc.message_dict.items():
					target_field = None if field == "__all__" else field
					for error in errors:
						form.add_error(target_field, error)
			else:
				for error in exc.messages:
					form.add_error(None, error)
			return self.form_invalid(form)
		except IntegrityError:
			form.add_error(None, "You have already commented on this post.")
			return self.form_invalid(form)

	def get_success_url(self):
		return reverse_lazy(
			"blog:post-detail",
			kwargs={"channel_slug": self.post_obj.channel.slug, "post_slug": self.post_obj.slug},
		)


class CommentUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
	model = Comment
	form_class = CommentForm
	template_name = "blog/comment_form.html"

	def dispatch(self, request, *args, **kwargs):
		comment = self.get_object()
		suspension_reason = get_user_suspension_reason(request.user)
		if suspension_reason:
			messages.error(request, suspension_reason)
			return redirect(comment.post.get_absolute_url())
		comment_restriction_reason = get_comment_restriction_reason(request.user)
		if comment_restriction_reason:
			messages.error(request, comment_restriction_reason)
			return redirect(comment.post.get_absolute_url())
		if not comment.post.channel.comments_enabled:
			messages.error(request, "Comments are disabled for this channel.")
			return redirect(comment.post.get_absolute_url())
		if are_users_blocked(request.user, comment.post.author) or are_users_blocked(request.user, comment.post.channel.owner):
			messages.error(request, "Commenting is unavailable because one of the users has blocked the other.")
			return redirect(comment.post.get_absolute_url())
		return super().dispatch(request, *args, **kwargs)

	def get_success_url(self):
		return reverse_lazy(
			"blog:post-detail",
			kwargs={"channel_slug": self.object.post.channel.slug, "post_slug": self.object.post.slug},
		)


class CommentDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
	model = Comment
	template_name = "blog/comment_confirm_delete.html"

	def get_success_url(self):
		return reverse_lazy(
			"blog:post-detail",
			kwargs={"channel_slug": self.object.post.channel.slug, "post_slug": self.object.post.slug},
		)


class GlobalSearchView(ListView):
	template_name = "blog/search_results.html"
	context_object_name = "results"
	paginate_by = 15
	chunk_size = 8

	def get_search_query(self):
		return get_search_query(self.request)

	def get_queryset(self):
		return []  # We'll override get_context_data instead

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		search_query = self.get_search_query()
		context["search_query"] = search_query

		if not search_query:
			context["posts"] = []
			context["channels"] = []
			context["users"] = []
			context["matching_tags"] = []
			context["trending_tags"] = get_discovery_tags(limit=12)
			return context

		post_page_number = self.request.GET.get("post_page", "1")
		channel_page_number = self.request.GET.get("channel_page", "1")
		user_page_number = self.request.GET.get("user_page", "1")

		# Search posts
		posts_queryset = (
			Post.objects.filter(
				Q(title__icontains=search_query)
				| Q(body__icontains=search_query)
				| Q(author__username__icontains=search_query)
				| Q(channel__name__icontains=search_query)
				,
				is_published=True,
			)
			.select_related("author", "channel", "channel__owner")
			.distinct()
			.order_by("-created_at")
		)
		posts_page = Paginator(posts_queryset, self.chunk_size).get_page(post_page_number)

		# Search channels
		channels_queryset = (
			Channel.objects.filter(
				Q(name__icontains=search_query)
				| Q(intro__icontains=search_query)
				| Q(description__icontains=search_query)
				| Q(owner__username__icontains=search_query)
			)
			.select_related("owner")
			.distinct()
			.order_by("-follower_count", "-created_at")
		)
		channels_page = Paginator(channels_queryset, self.chunk_size).get_page(channel_page_number)

		# Search users
		users_queryset = (
			User.objects.filter(
				Q(username__icontains=search_query)
				| Q(first_name__icontains=search_query)
				| Q(last_name__icontains=search_query)
			)
			.distinct()
			.order_by("username")
		)
		users_page = Paginator(users_queryset, self.chunk_size).get_page(user_page_number)

		posts = list(posts_page.object_list)
		channels = list(channels_page.object_list)
		users = list(users_page.object_list)
		matching_tags = list(get_discovery_tags(limit=8, search_query=search_query))

		context["posts"] = posts
		context["channels"] = channels
		context["users"] = users
		context["matching_tags"] = matching_tags
		context["trending_tags"] = get_discovery_tags(limit=8)
		context["posts_total"] = posts_page.paginator.count
		context["channels_total"] = channels_page.paginator.count
		context["users_total"] = users_page.paginator.count
		context["posts_has_next"] = posts_page.has_next()
		context["channels_has_next"] = channels_page.has_next()
		context["users_has_next"] = users_page.has_next()
		context["posts_next_query"] = ""
		context["channels_next_query"] = ""
		context["users_next_query"] = ""
		if posts_page.has_next():
			context["posts_next_query"] = build_query_with_params(
				self.request,
				post_page=posts_page.next_page_number(),
			)
		if channels_page.has_next():
			context["channels_next_query"] = build_query_with_params(
				self.request,
				channel_page=channels_page.next_page_number(),
			)
		if users_page.has_next():
			context["users_next_query"] = build_query_with_params(
				self.request,
				user_page=users_page.next_page_number(),
			)

		context["saved_post_ids"] = build_saved_post_ids(self.request.user, posts)

		# Track if user follows channels
		if self.request.user.is_authenticated:
			followed_channel_ids = set(
				ChannelFollow.objects.filter(follower=self.request.user).values_list("channel_id", flat=True)
			)
			context["followed_channel_ids"] = followed_channel_ids

		return context
