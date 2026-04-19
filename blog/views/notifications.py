from .common import (
    ChannelEditor,
    LoginRequiredMixin,
    ListView,
    Notification,
    PostCoAuthor,
    SearchContextMixin,
    View,
    get_object_or_404,
    redirect,
    url_has_allowed_host_and_scheme,
)


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
