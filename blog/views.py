from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView
from datetime import timedelta

from .forms import ChannelForm, CommentForm, PostForm, ProfileEditForm, SignUpForm, UserEditForm
from .models import Channel, ChannelFollow, Comment, Notification, Post, PostReaction, Profile, SavedPost, Tag, UserFollow

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
		return self.get_object().channel.owner == self.request.user


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


class ChannelListView(SearchContextMixin, LoginRequiredMixin, ListView):
	model = Channel
	template_name = "blog/channel_list.html"
	context_object_name = "channels"
	paginate_by = 10
	search_fields = ("name", "intro", "description", "owner__username")

	def get_queryset(self):
		queryset = (
			Channel.objects.select_related("owner")
			.annotate(follower_count=Count("followers"))
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

	def get_queryset(self):
		return Channel.objects.select_related("owner").annotate(follower_count=Count("followers"))

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["recent_posts"] = self.object.posts.select_related("author").order_by("-created_at")[:5]
		context["is_following"] = ChannelFollow.objects.filter(
			follower=self.request.user,
			channel=self.object,
		).exists()
		return context


class FollowingPostListView(SearchContextMixin, ListView):
	model = Post
	template_name = "blog/following_posts.html"
	context_object_name = "posts"
	paginate_by = 10
	search_fields = ("title", "body", "author__username", "channel__name")

	def get_queryset(self):
		base_queryset = Post.objects.select_related("channel", "author", "channel__owner")

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
		base_queryset = Post.objects.select_related("channel", "author", "channel__owner").order_by("-created_at")
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
			Post.objects.select_related("channel", "author", "channel__owner")
			.annotate(
				love_count=Count(
					"reactions",
					filter=Q(reactions__reaction=PostReaction.LOVE),
					distinct=True,
				),
				comment_count=Count("comments", distinct=True),
			)
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
				search_query=get_search_query(self.request),
			)
		)
		return context



def build_user_profile_context(profile_user, current_user, search_query=""):
	profile_obj = Profile.objects.filter(user=profile_user).first()
	all_user_posts = (
		Post.objects.filter(author=profile_user)
		.select_related("channel")
		.order_by("-created_at")
	)
	user_posts = apply_search(all_user_posts, search_query, ("title", "body", "channel__name"))
	is_following = False
	if current_user.is_authenticated and profile_user != current_user:
		is_following = UserFollow.objects.filter(follower=current_user, following=profile_user).exists()
	return {
		"profile_user": profile_user,
		"profile_obj": profile_obj,
		"user_posts": user_posts,
		"user_post_count": all_user_posts.count(),
		"user_channel_count": Channel.objects.filter(owner=profile_user).count(),
		"user_follower_count": UserFollow.objects.filter(following=profile_user).count(),
		"user_following_count": UserFollow.objects.filter(follower=profile_user).count(),
		"is_own_profile": profile_user == current_user,
		"is_following_user": is_following,
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


class FollowUserView(LoginRequiredMixin, View):
	def post(self, request, username):
		target_user = get_object_or_404(User, username=username)
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
		post_obj = get_object_or_404(Post, channel__slug=channel_slug, slug=post_slug)
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
		post_obj = get_object_or_404(Post, channel__slug=channel_slug, slug=post_slug)
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
		post_obj = get_object_or_404(Post, channel__slug=channel_slug, slug=post_slug)
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
		post_obj = get_object_or_404(Post, channel__slug=channel_slug, slug=post_slug)
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
		from .models import CommentReaction
		comment_obj = get_object_or_404(Comment, pk=pk)
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
		from .models import CommentReaction
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


class ChannelUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
	model = Channel
	form_class = ChannelForm
	template_name = "blog/channel_form.html"
	slug_field = "slug"
	slug_url_kwarg = "slug"
	success_url = reverse_lazy("blog:channel-list")


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
			Post.objects.filter(channel=self.channel)
			.select_related("author", "channel", "channel__owner")
			.order_by("-created_at")
		)
		return self.apply_search(queryset)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["channel"] = self.channel
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
			Post.objects.filter(tags=self.tag)
			.select_related("author", "channel", "channel__owner")
			.order_by("-created_at")
		)
		return self.apply_search(queryset)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["tag"] = self.tag
		context["saved_post_ids"] = build_saved_post_ids(self.request.user, context.get("posts", []))
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
		)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		post = self.object
		user = self.request.user
		if user.is_authenticated:
			user_comment = post.comments.filter(author=user).first()
			other_comments = post.comments.exclude(author=user).order_by("-created_at")
		else:
			user_comment = None
			other_comments = post.comments.order_by("-created_at")
		context["user_comment"] = user_comment
		context["other_comments"] = other_comments
		context["is_post_saved"] = user.is_authenticated and SavedPost.objects.filter(user=user, post=post).exists()
		context["love_count"] = post.reactions.filter(reaction=PostReaction.LOVE).count()
		context["is_post_loved"] = user.is_authenticated and post.reactions.filter(user=user, reaction=PostReaction.LOVE).exists()
		
		# Build comment love counts and user loves for template
		all_comments = []
		if user_comment:
			all_comments.append(user_comment)
		all_comments.extend(list(other_comments))
		
		if all_comments:
			from .models import CommentReaction
			comment_ids = [c.id for c in all_comments]
			
			# Get love counts per comment
			love_counts = {}
			for result in CommentReaction.objects.filter(
				comment_id__in=comment_ids, reaction=CommentReaction.LOVE
			).values('comment_id').annotate(count=Count('id')):
				love_counts[result['comment_id']] = result['count']
			
			# Get user loved comments
			user_loved = set()
			if user.is_authenticated:
				user_loved = set(
					CommentReaction.objects.filter(
						user=user, comment_id__in=comment_ids, reaction=CommentReaction.LOVE
					).values_list('comment_id', flat=True)
				)
			
			# Attach to each comment for easy template access
			for comment in all_comments:
				comment.love_count = love_counts.get(comment.id, 0)
				comment.user_loved = comment.id in user_loved
		
		context["user_loved_comments"] = {c.id for c in all_comments if c.user_loved}
		return context


class PostCreateView(LoginRequiredMixin, CreateView):
	model = Post
	form_class = PostForm
	template_name = "blog/post_form.html"

	def dispatch(self, request, *args, **kwargs):
		self.channel = get_object_or_404(Channel, slug=self.kwargs["channel_slug"])
		if self.channel.owner_id != request.user.id:
			raise PermissionDenied("Only the channel creator can create posts in this channel.")
		return super().dispatch(request, *args, **kwargs)

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs["instance"] = Post(channel=self.channel, author=self.request.user)
		return kwargs

	def get_success_url(self):
		return reverse_lazy("blog:post-list", kwargs={"channel_slug": self.channel.slug})

	def form_valid(self, form):
		response = super().form_valid(form)
		save_post_tags(self.object, form)
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
		return reverse_lazy("blog:post-list", kwargs={"channel_slug": self.object.channel.slug})

	def form_valid(self, form):
		response = super().form_valid(form)
		save_post_tags(self.object, form)
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
			Post,
			channel__slug=self.kwargs["channel_slug"],
			slug=self.kwargs["post_slug"],
		)
		return super().dispatch(request, *args, **kwargs)

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs["instance"] = Comment(post=self.post_obj, author=self.request.user)
		return kwargs

	def form_valid(self, form):
		try:
			response = super().form_valid(form)
			if self.post_obj.author_id != self.request.user.id:
				create_notification(
					recipient=self.post_obj.author,
					actor=self.request.user,
					notification_type=Notification.TYPE_COMMENT,
					message=f"{self.request.user.username} commented on your post: {self.post_obj.title}.",
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
			return context

		# Search posts
		posts = (
			Post.objects.filter(
				Q(title__icontains=search_query)
				| Q(body__icontains=search_query)
				| Q(author__username__icontains=search_query)
				| Q(channel__name__icontains=search_query)
			)
			.select_related("author", "channel", "channel__owner")
			.distinct()
			.order_by("-created_at")[:10]
		)

		# Search channels
		channels = (
			Channel.objects.filter(
				Q(name__icontains=search_query)
				| Q(intro__icontains=search_query)
				| Q(description__icontains=search_query)
				| Q(owner__username__icontains=search_query)
			)
			.select_related("owner")
			.annotate(follower_count=Count("followers"))
			.distinct()
			.order_by("-follower_count", "-created_at")[:10]
		)

		# Search users
		users = (
			User.objects.filter(
				Q(username__icontains=search_query)
				| Q(first_name__icontains=search_query)
				| Q(last_name__icontains=search_query)
			)
			.distinct()
			.order_by("username")[:10]
		)

		context["posts"] = posts
		context["channels"] = channels
		context["users"] = users
		context["saved_post_ids"] = build_saved_post_ids(self.request.user, posts)

		# Track if user follows channels
		if self.request.user.is_authenticated:
			followed_channel_ids = set(
				ChannelFollow.objects.filter(follower=self.request.user).values_list("channel_id", flat=True)
			)
			context["followed_channel_ids"] = followed_channel_ids

		return context
