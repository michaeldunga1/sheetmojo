from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import ChannelForm, CommentForm, PostForm, ProfileEditForm, UserEditForm
from .models import Channel, ChannelFollow, Comment, Post, Profile

User = get_user_model()


def home_redirect(request):
	return redirect("blog:following-posts")


class SignUpView(CreateView):
	form_class = UserCreationForm
	template_name = "registration/register.html"
	success_url = reverse_lazy("login")


class OwnerRequiredMixin(UserPassesTestMixin):
	def test_func(self):
		return self.get_object().owner == self.request.user


class AuthorRequiredMixin(UserPassesTestMixin):
	def test_func(self):
		return self.get_object().author == self.request.user


class ChannelListView(LoginRequiredMixin, ListView):
	model = Channel
	template_name = "blog/channel_list.html"
	context_object_name = "channels"
	paginate_by = 10

	def get_queryset(self):
		return (
			Channel.objects.select_related("owner")
			.annotate(follower_count=Count("followers"))
			.order_by("-follower_count", "-created_at")
		)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		followed_channel_ids = set(
			ChannelFollow.objects.filter(follower=self.request.user).values_list("channel_id", flat=True)
		)
		context["followed_channel_ids"] = followed_channel_ids
		return context


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


class FollowingPostListView(ListView):
	model = Post
	template_name = "blog/following_posts.html"
	context_object_name = "posts"
	paginate_by = 10

	def get_queryset(self):
		base_queryset = Post.objects.select_related("channel", "author", "channel__owner")

		if not self.request.user.is_authenticated:
			return base_queryset.order_by("-created_at")

		followed_channel_ids = list(
			ChannelFollow.objects.filter(follower=self.request.user).values_list("channel_id", flat=True)
		)

		if not followed_channel_ids:
			return base_queryset.order_by("-created_at")

		return (
			base_queryset.filter(
				Q(channel_id__in=followed_channel_ids) | Q(author=self.request.user)
			)
			.distinct()
			.order_by("-created_at")
		)


class UserProfileView(LoginRequiredMixin, TemplateView):
	template_name = "blog/profile.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context.update(build_user_profile_context(self.request.user, self.request.user))
		return context


class PublicUserProfileView(LoginRequiredMixin, TemplateView):
	template_name = "blog/profile.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		profile_user = get_object_or_404(User, username=self.kwargs["username"])
		context.update(build_user_profile_context(profile_user, self.request.user))
		return context


def build_user_profile_context(profile_user, current_user):
	profile_obj = Profile.objects.filter(user=profile_user).first()
	user_posts = (
		Post.objects.filter(author=profile_user)
		.select_related("channel")
		.order_by("-created_at")
	)
	return {
		"profile_user": profile_user,
		"profile_obj": profile_obj,
		"user_posts": user_posts,
		"user_post_count": user_posts.count(),
		"user_channel_count": Channel.objects.filter(owner=profile_user).count(),
		"is_own_profile": profile_user == current_user,
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


class FollowChannelView(LoginRequiredMixin, View):
	def post(self, request, channel_slug):
		channel = get_object_or_404(Channel, slug=channel_slug)
		if channel.owner != request.user:
			ChannelFollow.objects.get_or_create(follower=request.user, channel=channel)
		return redirect("blog:channel-list")


class UnfollowChannelView(LoginRequiredMixin, View):
	def post(self, request, channel_slug):
		channel = get_object_or_404(Channel, slug=channel_slug)
		ChannelFollow.objects.filter(follower=request.user, channel=channel).delete()
		return redirect("blog:channel-list")


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


class PostListView(LoginRequiredMixin, ListView):
	model = Post
	template_name = "blog/post_list.html"
	context_object_name = "posts"
	paginate_by = 10

	def dispatch(self, request, *args, **kwargs):
		self.channel = get_object_or_404(Channel, slug=self.kwargs["channel_slug"])
		return super().dispatch(request, *args, **kwargs)

	def get_queryset(self):
		return Post.objects.filter(channel=self.channel).order_by("-created_at")

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["channel"] = self.channel
		return context


class PostDetailView(LoginRequiredMixin, DetailView):
	model = Post
	template_name = "blog/post_detail.html"
	context_object_name = "post"

	def get_queryset(self):
		return Post.objects.select_related("channel", "author").prefetch_related("comments__author")


class PostCreateView(LoginRequiredMixin, CreateView):
	model = Post
	form_class = PostForm
	template_name = "blog/post_form.html"

	def dispatch(self, request, *args, **kwargs):
		self.channel = get_object_or_404(Channel, slug=self.kwargs["channel_slug"])
		return super().dispatch(request, *args, **kwargs)

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs["instance"] = Post(channel=self.channel, author=self.request.user)
		return kwargs

	def get_success_url(self):
		return reverse_lazy("blog:post-list", kwargs={"channel_slug": self.channel.slug})


class PostUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
	model = Post
	form_class = PostForm
	template_name = "blog/post_form.html"

	def get_success_url(self):
		return reverse_lazy("blog:post-list", kwargs={"channel_slug": self.object.channel.slug})


class PostDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
	model = Post
	template_name = "blog/post_confirm_delete.html"

	def get_success_url(self):
		return reverse_lazy("blog:post-list", kwargs={"channel_slug": self.object.channel.slug})


class CommentCreateView(LoginRequiredMixin, CreateView):
	model = Comment
	form_class = CommentForm
	template_name = "blog/comment_form.html"

	def dispatch(self, request, *args, **kwargs):
		self.post_obj = get_object_or_404(Post, pk=self.kwargs["post_pk"])
		return super().dispatch(request, *args, **kwargs)

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs["instance"] = Comment(post=self.post_obj, author=self.request.user)
		return kwargs

	def form_valid(self, form):
		try:
			return super().form_valid(form)
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
		return reverse_lazy("blog:post-list", kwargs={"channel_slug": self.post_obj.channel.slug})


class CommentUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
	model = Comment
	form_class = CommentForm
	template_name = "blog/comment_form.html"

	def get_success_url(self):
		return reverse_lazy("blog:post-list", kwargs={"channel_slug": self.object.post.channel.slug})


class CommentDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
	model = Comment
	template_name = "blog/comment_confirm_delete.html"

	def get_success_url(self):
		return reverse_lazy("blog:post-list", kwargs={"channel_slug": self.object.post.channel.slug})
