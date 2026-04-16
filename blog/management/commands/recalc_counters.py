"""
Management command to backfill all denormalized counter fields.

Usage:
    python manage.py recalc_counters
"""

from django.core.management.base import BaseCommand
from django.db.models import Count, Q


class Command(BaseCommand):
    help = "Recalculate and store all denormalized counter fields on Post, Channel, and Comment."

    def handle(self, *args, **options):
        from blog.models import Channel, Comment, Post, PostReaction

        self.stdout.write("Recalculating Post.love_count …")
        for post in Post.objects.iterator():
            Post.objects.filter(pk=post.pk).update(
                love_count=post.reactions.filter(reaction=PostReaction.LOVE).count(),
                comment_count=post.comments.count(),
                saves_count=post.saved_by.count(),
            )

        self.stdout.write("Recalculating Channel.follower_count and Channel.posts_count …")
        for channel in Channel.objects.iterator():
            Channel.objects.filter(pk=channel.pk).update(
                follower_count=channel.followers.count(),
                posts_count=channel.posts.count(),
            )

        self.stdout.write("Recalculating Comment.love_count …")
        for comment in Comment.objects.iterator():
            Comment.objects.filter(pk=comment.pk).update(
                love_count=comment.reactions.count(),
            )

        self.stdout.write(self.style.SUCCESS("Done — all counters recalculated."))
