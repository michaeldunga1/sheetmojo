from .common import (
    Channel,
    ChannelEditor,
    ChannelFollow,
    Contact,
    ContactForm,
    Count,
    ListView,
    LoginRequiredMixin,
    Max,
    NewsletterSubscribeForm,
    NewsletterSubscription,
    Paginator,
    Post,
    Q,
    Report,
    SavedPost,
    SearchContextMixin,
    Sum,
    Tag,
    TemplateView,
    User,
    UserFollow,
    ValidationError,
    View,
    build_query_with_params,
    build_saved_post_ids,
    cache,
    get_discovery_tags,
    get_search_query,
    get_visible_post_filter,
    get_visible_posts_queryset,
    messages,
    redirect,
    render,
    settings,
    success,
    timedelta,
    timezone,
)


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
        return render(request, self.template_name, {"form": self.form_class()})

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
        return render(request, self.template_name, {"form": self.form_class()})

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


class ChannelListView(SearchContextMixin, ListView):
    model = Channel
    template_name = "blog/channel_list.html"
    context_object_name = "channels"
    paginate_by = 10
    search_fields = ("name", "intro", "description", "owner__username")

    def get_queryset(self):
        queryset = Channel.objects.select_related("owner").order_by("-follower_count", "-created_at", "-id")
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(visibility="public")
        return self.apply_search(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["followed_channel_ids"] = set(
                ChannelFollow.objects.filter(follower=self.request.user).values_list("channel_id", flat=True)
            )
        else:
            context["followed_channel_ids"] = set()
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
        followed_channel_ids = ChannelFollow.objects.filter(follower=self.request.user).values_list("channel_id", flat=True)
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


class FollowingPostListView(SearchContextMixin, ListView):
    model = Post
    template_name = "blog/following_posts.html"
    context_object_name = "posts"
    paginate_by = 10
    search_fields = ("title", "body", "author__username", "channel__name")

    def get_queryset(self):
        base_queryset = get_visible_posts_queryset(self.request.user).select_related("channel", "author", "channel__owner")
        if not self.request.user.is_authenticated:
            return self.apply_search(base_queryset.order_by("-created_at"))

        followed_channel_ids = list(
            ChannelFollow.objects.filter(follower=self.request.user).values_list("channel_id", flat=True)
        )
        if not followed_channel_ids:
            return self.apply_search(base_queryset.order_by("-created_at"))

        queryset = (
            base_queryset.filter(Q(channel_id__in=followed_channel_ids) | Q(author=self.request.user))
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
        base_queryset = (
            Post.objects.filter(is_published=True)
            .select_related("channel", "author", "channel__owner")
            .order_by("-created_at")
        )
        if not followed_user_ids:
            return self.apply_search(base_queryset.none())
        return self.apply_search(base_queryset.filter(author_id__in=followed_user_ids).distinct())

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
        queryset = get_visible_posts_queryset(self.request.user).select_related("channel", "author", "channel__owner")

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


class TagPostListView(SearchContextMixin, ListView):
    model = Post
    template_name = "blog/tag_post_list.html"
    context_object_name = "posts"
    paginate_by = 10
    search_fields = ("title", "body", "author__username")

    def dispatch(self, request, *args, **kwargs):
        self.tag = self.get_tag()
        return super().dispatch(request, *args, **kwargs)

    def get_tag(self):
        return self._tag if hasattr(self, "_tag") else None

    def get_queryset(self):
        self._tag = self._tag if hasattr(self, "_tag") else None
        if self._tag is None:
            from .common import get_object_or_404

            self._tag = get_object_or_404(Tag, slug=self.kwargs["tag_slug"])
        queryset = (
            Post.objects.filter(tags=self._tag, is_published=True)
            .select_related("author", "channel", "channel__owner")
            .prefetch_related("tags")
            .order_by("-created_at")
        )
        return self.apply_search(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        related_tags = (
            Tag.objects.filter(posts__in=self.object_list)
            .exclude(pk=self._tag.pk)
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
        context["tag"] = self._tag
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


class GlobalSearchView(ListView):
    template_name = "blog/search_results.html"
    context_object_name = "results"
    paginate_by = 15
    chunk_size = 8

    def get_search_query(self):
        return get_search_query(self.request)

    def get_queryset(self):
        return []

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

        posts_queryset = (
            Post.objects.filter(
                Q(title__icontains=search_query)
                | Q(body__icontains=search_query)
                | Q(author__username__icontains=search_query)
                | Q(channel__name__icontains=search_query),
                is_published=True,
            )
            .select_related("author", "channel", "channel__owner")
            .distinct()
            .order_by("-created_at")
        )
        posts_page = Paginator(posts_queryset, self.chunk_size).get_page(post_page_number)

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
            context["posts_next_query"] = build_query_with_params(self.request, post_page=posts_page.next_page_number())
        if channels_page.has_next():
            context["channels_next_query"] = build_query_with_params(self.request, channel_page=channels_page.next_page_number())
        if users_page.has_next():
            context["users_next_query"] = build_query_with_params(self.request, user_page=users_page.next_page_number())

        context["saved_post_ids"] = build_saved_post_ids(self.request.user, posts)
        if self.request.user.is_authenticated:
            context["followed_channel_ids"] = set(
                ChannelFollow.objects.filter(follower=self.request.user).values_list("channel_id", flat=True)
            )

        return context
