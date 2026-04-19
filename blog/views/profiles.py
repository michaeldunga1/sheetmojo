from .common import (
    Channel,
    Comment,
    CommentReaction,
    Count,
    IntegrityError,
    LoginRequiredMixin,
    Notification,
    Paginator,
    Post,
    PostReaction,
    Profile,
    ProfileEditForm,
    Q,
    Report,
    Sum,
    TemplateView,
    User,
    UserBlock,
    UserEditForm,
    UserFollow,
    ValidationError,
    View,
    build_saved_post_ids,
    create_notification,
    get_object_or_404,
    get_search_query,
    is_blocking_user,
    logout,
    messages,
    redirect,
    render,
    reverse,
    success,
    timedelta,
    timezone,
    url_has_allowed_host_and_scheme,
    get_user_suspension_reason,
    are_users_blocked,
)


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


class PublicUserProfileView(TemplateView):
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
    visible_posts = Post.objects.filter(author=profile_user).select_related("channel").order_by("-created_at")
    # If profile is locked and not the owner, treat as hidden
    profile_locked = getattr(profile_obj, "profile_locked", False)
    is_own_profile = profile_user == current_user
    if profile_locked and not is_own_profile:
        # Hide all posts and details
        return {
            "profile_user": profile_user,
            "profile_obj": profile_obj,
            "is_own_profile": is_own_profile,
            "profile_locked": True,
        }
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

    from .common import apply_search

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
        "profile_locked": False,
    }


class UserProfileEditView(LoginRequiredMixin, View):
    template_name = "blog/profile_form.html"

    def get(self, request):
        profile_obj, _ = Profile.objects.get_or_create(user=request.user)
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=profile_obj)
        return render(request, self.template_name, {"user_form": user_form, "profile_form": profile_form})

    def post(self, request):
        profile_obj, _ = Profile.objects.get_or_create(user=request.user)
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileEditForm(request.POST, instance=profile_obj)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("blog:profile")
        return render(request, self.template_name, {"user_form": user_form, "profile_form": profile_form})


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
            qs = Channel.objects.filter(owner=user).annotate(report_count=Count("reports", distinct=True)).order_by("-created_at")
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

        qs = Report.objects.filter(reporter=user).select_related("post", "comment", "channel", "reported_user").order_by("-created_at")
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

    def get(self, request, username):
        messages.info(request, "Follow/unfollow actions must be performed via the profile page.")
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

    def get(self, request, username):
        messages.info(request, "Follow/unfollow actions must be performed via the profile page.")
        return redirect("blog:user-profile", username=username)


class BlockUserView(LoginRequiredMixin, View):
    def get(self, request, username):
        messages.info(request, "Block/unblock actions must be performed via the profile page.")
        return redirect("blog:user-profile", username=username)

    def post(self, request, username):
        target_user = get_object_or_404(User, username=username)
        if target_user != request.user:
            UserBlock.objects.get_or_create(blocker=request.user, blocked=target_user)
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
    def get(self, request, username):
        messages.info(request, "Block/unblock actions must be performed via the profile page.")
        return redirect("blog:user-profile", username=username)

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
