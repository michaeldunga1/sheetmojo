from .common import (
    AuthorRequiredMixin,
    Channel,
    ChannelEditor,
    ChannelPostOwnerRequiredMixin,
    Comment,
    CommentForm,
    CommentReaction,
    CreateView,
    DeleteView,
    DetailView,
    F,
    IntegrityError,
    ListView,
    LoginRequiredMixin,
    Notification,
    Paginator,
    PermissionDenied,
    Post,
    PostCoAuthor,
    PostForm,
    PostReaction,
    Report,
    SavedPost,
    SearchContextMixin,
    Tag,
    UpdateView,
    User,
    ValidationError,
    View,
    are_users_blocked,
    build_query_with_params,
    build_saved_post_ids,
    create_notification,
    get_channel_suspension_reason,
    get_comment_restriction_reason,
    get_object_or_404,
    get_post_commenting_disabled_reason,
    get_user_suspension_reason,
    get_visible_post_filter,
    get_visible_posts_queryset,
    messages,
    redirect,
    reverse,
    reverse_lazy,
    save_post_tags,
    success,
    url_has_allowed_host_and_scheme,
)


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


class PostInviteCoAuthorView(LoginRequiredMixin, View):
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
        _, created = PostCoAuthor.objects.get_or_create(
            post=post,
            user=invitee,
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
        if action == "decline":
            invite.accepted = False
            invite.save(update_fields=["accepted"])
            success(request, "Invitation declined.")
        return redirect(reverse("blog:notifications"))


class PostRemoveCoAuthorView(LoginRequiredMixin, View):
    def post(self, request, pk):
        invite = get_object_or_404(PostCoAuthor, pk=pk)
        post = invite.post
        if post.channel.owner != request.user:
            raise PermissionDenied
        username = invite.user.username
        invite.delete()
        success(request, f"{username} removed from co-authors.")
        return redirect(post.get_absolute_url())


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


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"
    slug_field = "slug"
    slug_url_kwarg = "post_slug"

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        channel = post.channel
        user = request.user
        # Public channels: always allow
        if channel.visibility == "public":
            return super().dispatch(request, *args, **kwargs)
        # Private: only owner
        if channel.visibility == "private" and channel.owner != user:
            raise PermissionDenied("You do not have permission to view posts in this channel.")
        # Restricted: only allowed users or owner
        if channel.visibility == "restricted" and user not in channel.allowed_users.all() and channel.owner != user:
            raise PermissionDenied("You do not have permission to view posts in this channel.")
        return super().dispatch(request, *args, **kwargs)

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

        all_comments = []
        if user_comment:
            all_comments.append(user_comment)
        all_comments.extend(list(other_comments))

        if all_comments and user.is_authenticated:
            comment_ids = [comment.id for comment in all_comments]
            reported_comment_ids = set(
                Report.objects.filter(reporter=user, comment_id__in=comment_ids).values_list("comment_id", flat=True)
            )
            user_loved = set(
                CommentReaction.objects.filter(
                    user=user,
                    comment_id__in=comment_ids,
                    reaction=CommentReaction.LOVE,
                ).values_list("comment_id", flat=True)
            )
            for comment in all_comments:
                comment.user_loved = comment.id in user_loved
                comment.user_reported = comment.id in reported_comment_ids
        else:
            reported_comment_ids = set()

        context["user_loved_comments"] = {comment.id for comment in all_comments if getattr(comment, "user_loved", False)}
        context["reported_comment_ids"] = reported_comment_ids
        context["post_coauthors"] = PostCoAuthor.objects.filter(post=post, accepted=True).select_related("user")
        if post.channel.owner == user:
            context["post_coauthor_invites"] = PostCoAuthor.objects.filter(post=post, accepted=None).select_related("user")
        else:
            context["post_coauthor_invites"] = PostCoAuthor.objects.none()
        context["is_post_coauthor"] = user.is_authenticated and PostCoAuthor.objects.filter(
            post=post,
            user=user,
            accepted=True,
        ).exists()
        if user.is_authenticated:
            context["my_coauthor_invite"] = PostCoAuthor.objects.filter(post=post, user=user, accepted=None).first()
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
            if channel_owner.id != self.request.user.id and channel_owner.id != self.post_obj.author_id:
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
        return reverse_lazy("blog:post-detail", kwargs={"channel_slug": self.post_obj.channel.slug, "post_slug": self.post_obj.slug})


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
        return reverse_lazy("blog:post-detail", kwargs={"channel_slug": self.object.post.channel.slug, "post_slug": self.object.post.slug})


class CommentDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Comment
    template_name = "blog/comment_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("blog:post-detail", kwargs={"channel_slug": self.object.post.channel.slug, "post_slug": self.object.post.slug})
