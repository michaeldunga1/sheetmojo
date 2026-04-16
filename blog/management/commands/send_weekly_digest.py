from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from blog.models import ChannelFollow, Notification, Post, Profile

User = get_user_model()


class Command(BaseCommand):
    help = "Send weekly digest emails based on each user's digest preferences"

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Send regardless of weekday/hour preferences")
        parser.add_argument("--user", type=str, help="Only send digest for a specific username")
        parser.add_argument(
            "--send-empty",
            action="store_true",
            help="Send digest even if there are no followed-channel posts or unread notifications",
        )

    def handle(self, *args, **options):
        force = options["force"]
        send_empty = options["send_empty"]
        target_username = options.get("user")

        now = timezone.now()
        digest_window_start = now.replace(minute=0, second=0, microsecond=0)
        since = now - timedelta(days=7)

        users = User.objects.filter(is_active=True).exclude(email="")
        if target_username:
            users = users.filter(username=target_username)

        sent_count = 0
        skipped_count = 0

        for user in users:
            profile, _ = Profile.objects.get_or_create(user=user)
            if not profile.email_digest_enabled:
                skipped_count += 1
                continue

            if not force:
                if profile.digest_weekday != now.weekday() or profile.digest_hour != now.hour:
                    skipped_count += 1
                    continue

                if profile.last_digest_sent_at and profile.last_digest_sent_at >= digest_window_start:
                    skipped_count += 1
                    continue

            followed_channel_ids = ChannelFollow.objects.filter(follower=user).values_list("channel_id", flat=True)
            recent_posts = list(
                Post.objects.filter(channel_id__in=followed_channel_ids, created_at__gte=since)
                .select_related("author", "channel")
                .order_by("-created_at")[:10]
            )
            unread_notifications = list(
                Notification.objects.filter(recipient=user, is_read=False)
                .select_related("actor")
                .order_by("-created_at")[:10]
            )

            if not send_empty and not recent_posts and not unread_notifications:
                skipped_count += 1
                continue

            context = {
                "user": user,
                "recent_posts": recent_posts,
                "unread_notifications": unread_notifications,
                "since": since,
                "now": now,
            }

            subject = f"SheetMojo Weekly Digest - {now.strftime('%b %d, %Y')}"
            text_body = render_to_string("blog/emails/weekly_digest.txt", context)
            html_body = render_to_string("blog/emails/weekly_digest.html", context)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                to=[user.email],
            )
            email.attach_alternative(html_body, "text/html")
            email.send()

            profile.last_digest_sent_at = now
            profile.save(update_fields=["last_digest_sent_at"])
            sent_count += 1

        self.stdout.write(self.style.SUCCESS(f"Weekly digest complete. Sent: {sent_count}, Skipped: {skipped_count}"))
