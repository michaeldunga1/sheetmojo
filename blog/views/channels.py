from .common import (
    Channel,
    ChannelEditor,
    ChannelFollow,
    ChannelForm,
    ChannelMembership,
    ChannelMembershipInviteForm,
    Count,
    CreateView,
    DeleteView,
    DetailView,
    F,
    ListView,
    LoginRequiredMixin,
    Max,
    Notification,
    OwnerRequiredMixin,
    PermissionDenied,
    Post,
    PostCoAuthor,
    Q,
    Report,
    SavedPost,
    Sum,
    Tag,
    UpdateView,
    User,
    View,
    build_channel_membership_context,
    build_query_with_params,
    build_saved_post_ids,
    create_notification,
    get_channel_suspension_reason,
    get_discovery_tags,
    get_user_suspension_reason,
    get_visible_post_filter,
    get_visible_posts_queryset,
    get_object_or_404,
    messages,
    method_decorator,
    redirect,
    render,
    require_POST,
    reverse,
    reverse_lazy,
    success,
    timezone,
    timedelta,
    url_has_allowed_host_and_scheme,
)


def build_channel_editor_context(channel, user):
    if user.is_authenticated:
        return {
            "channel_editors": ChannelEditor.objects.filter(channel=channel, accepted=True).select_related("user"),
            "is_channel_editor": ChannelEditor.objects.filter(channel=channel, user=user, accepted=True).exists(),
            "my_editor_invite": ChannelEditor.objects.filter(channel=channel, user=user, accepted=None).select_related("invited_by").first(),
        }
    else:
        return {
            "channel_editors": ChannelEditor.objects.filter(channel=channel, accepted=True).select_related("user"),
            "is_channel_editor": False,
            "my_editor_invite": None,
        }


def build_channel_analytics_context(channel, request, analytics_window_choices):
    analytics_window = request.GET.get("window", "7d")
    valid = {choice[0] for choice in analytics_window_choices}
    analytics_window = analytics_window if analytics_window in valid else "7d"

    channel_posts = channel.posts.filter(is_published=True)
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
    top_post = channel_posts.order_by("-love_count", "-comment_count", "-saves_count", "-view_count", "-created_at").first()
    window_label = dict(analytics_window_choices).get(analytics_window, "7 days")

    return {
        "channel_analytics": {
            "total_posts": total_posts,
            "total_followers": channel.follower_count,
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
        },
        "analytics_window": analytics_window,
        "analytics_window_choices": analytics_window_choices,
        "analytics_window_links": [
            {
                "value": value,
                "label": label,
                "query_string": build_query_with_params(request, window=value),
            }
            for value, label in analytics_window_choices
        ],
    }


class ChannelMembershipChangeRoleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        membership = get_object_or_404(ChannelMembership, pk=pk)
        channel = membership.channel
        is_admin = (
            ChannelMembership.objects.filter(
                channel=channel,
                user=request.user,
                role__in=["admin", "creator"],
                accepted=True,
            ).exists()
            or channel.owner == request.user
        )
        if not is_admin or membership.user == channel.owner:
            raise PermissionDenied("You do not have permission to change this member's role.")
        new_role = request.POST.get("role")
        if new_role not in dict(ChannelMembership.ROLE_CHOICES):
            messages.error(request, "Invalid role.")
        else:
            membership.role = new_role
            membership.save(update_fields=["role"])
            messages.success(request, f"{membership.user.username}'s role updated to {membership.get_role_display()}.")
        return redirect(channel.get_absolute_url())


class ChannelMembershipRemoveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        membership = get_object_or_404(ChannelMembership, pk=pk)
        channel = membership.channel
        is_admin = (
            ChannelMembership.objects.filter(
                channel=channel,
                user=request.user,
                role__in=["admin", "creator"],
                accepted=True,
            ).exists()
            or channel.owner == request.user
        )
        if not is_admin or membership.user == channel.owner:
            raise PermissionDenied("You do not have permission to remove this member.")
        membership.delete()
        messages.success(request, f"{membership.user.username} removed from the channel.")
        return redirect(channel.get_absolute_url())


class ChannelMembershipRespondInviteView(LoginRequiredMixin, View):
    @method_decorator(require_POST)
    def post(self, request, pk):
        invite = get_object_or_404(ChannelMembership, pk=pk, user=request.user, accepted=False)
        action = request.POST.get("action")
        if action == "accept":
            invite.accepted = True
            invite.save(update_fields=["accepted"])
            messages.success(request, "You have joined the channel.")
        elif action == "decline":
            invite.delete()
            messages.info(request, "You declined the invitation.")
        else:
            messages.error(request, "Invalid action.")
        return redirect(invite.channel.get_absolute_url())


class ChannelMembershipInviteView(LoginRequiredMixin, View):
    def post(self, request, channel_slug):
        channel = get_object_or_404(Channel, slug=channel_slug)
        if (
            not ChannelMembership.objects.filter(
                channel=channel, user=request.user, role__in=["admin", "creator"]
            ).exists()
            and channel.owner != request.user
        ):
            raise PermissionDenied("You do not have permission to invite users to this channel.")
        form = ChannelMembershipInviteForm(request.POST, channel=channel, invited_by=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Invitation sent.")
            response_form = ChannelMembershipInviteForm(channel=channel, invited_by=request.user)
        else:
            messages.error(request, ", ".join([str(e) for e in form.errors.values()]))
            response_form = form
        if request.headers.get("HX-Request") == "true":
            context = {
                "channel": channel,
                "channel_invite_form": response_form,
                **build_channel_membership_context(channel, request.user),
            }
            return render(request, "blog/partials/channel_members_panel.html", context)
        return redirect(channel.get_absolute_url())


class FollowChannelView(LoginRequiredMixin, View):
    def get(self, request, channel_slug):
        messages.info(request, "Follow/unfollow actions must be performed via the channel page.")
        channel = get_object_or_404(Channel, slug=channel_slug)
        return redirect(channel.get_absolute_url())

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
        from .common import are_users_blocked

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
    def get(self, request, channel_slug):
        messages.info(request, "Follow/unfollow actions must be performed via the channel page.")
        channel = get_object_or_404(Channel, slug=channel_slug)
        return redirect(channel.get_absolute_url())

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


class ChannelDetailView(DetailView):
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

    def dispatch(self, request, *args, **kwargs):
        channel = self.get_object()
        user = request.user
        if channel.visibility == "private" and channel.owner != user:
            raise PermissionDenied("You do not have permission to view this channel.")
        if channel.visibility == "restricted" and user not in channel.allowed_users.all() and channel.owner != user:
            raise PermissionDenied("You do not have permission to view this channel.")
        return super().dispatch(request, *args, **kwargs)

    def get_analytics_window(self):
        window = self.request.GET.get("window", "7d")
        valid = {choice[0] for choice in self.analytics_window_choices}
        return window if window in valid else "7d"

    def get_queryset(self):
        return Channel.objects.select_related("owner")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent_posts"] = self.object.posts.filter(is_published=True).select_related("author").order_by("-created_at")[:5]
        user = self.request.user
        if user.is_authenticated:
            context["is_following"] = ChannelFollow.objects.filter(
                follower=user,
                channel=self.object,
            ).exists()
            context["has_reported_channel"] = Report.objects.filter(
                reporter=user,
                channel=self.object,
            ).exists()
        else:
            context["is_following"] = False
            context["has_reported_channel"] = False
        context.update(build_channel_membership_context(self.object, user))
        context.update(build_channel_editor_context(self.object, user))
        return context


class ChannelMembersView(LoginRequiredMixin, DetailView):
    model = Channel
    template_name = "blog/channel_members.html"
    context_object_name = "channel"
    slug_field = "slug"
    slug_url_kwarg = "channel_slug"

    def get_queryset(self):
        return Channel.objects.select_related("owner")

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        membership_context = build_channel_membership_context(self.object, request.user)
        if not membership_context["is_channel_admin"]:
            raise PermissionDenied("You do not have permission to manage members for this channel.")
        self.membership_context = membership_context
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.membership_context)
        context.update(build_channel_editor_context(self.object, self.request.user))
        context["channel_invite_form"] = ChannelMembershipInviteForm(channel=self.object, invited_by=self.request.user)
        return context


class ChannelAnalyticsView(LoginRequiredMixin, DetailView):
    model = Channel
    template_name = "blog/channel_analytics.html"
    context_object_name = "channel"
    slug_field = "slug"
    slug_url_kwarg = "channel_slug"
    analytics_window_choices = (
        ("7d", "7 days"),
        ("30d", "30 days"),
        ("all", "All time"),
    )

    def get_queryset(self):
        return Channel.objects.select_related("owner")

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.owner_id != request.user.id:
            raise PermissionDenied("Only the channel owner can view analytics for this channel.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_channel_editor_context(self.object, self.request.user))
        context.update(build_channel_analytics_context(self.object, self.request, self.analytics_window_choices))
        return context


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


class ChannelInviteEditorView(LoginRequiredMixin, View):
    def post(self, request, channel_slug):
        channel = get_object_or_404(Channel, slug=channel_slug, owner=request.user)
        username = request.POST.get("username", "").strip()
        invitee = get_object_or_404(User, username=username)
        if invitee == request.user:
            messages.error(request, "You cannot invite yourself as an editor.")
            return redirect(channel.get_absolute_url())
        _, created = ChannelEditor.objects.get_or_create(
            channel=channel,
            user=invitee,
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
        if action == "decline":
            invite.accepted = False
            invite.save(update_fields=["accepted"])
            success(request, "Invitation declined.")
        return redirect(reverse("blog:notifications"))


class ChannelRemoveEditorView(LoginRequiredMixin, View):
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
