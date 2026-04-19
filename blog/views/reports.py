from .common import (
    Channel,
    Comment,
    LoginRequiredMixin,
    Post,
    Report,
    ReportForm,
    User,
    View,
    are_users_blocked,
    get_object_or_404,
    get_user_suspension_reason,
    messages,
    redirect,
    render,
    reverse,
    success,
)


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
