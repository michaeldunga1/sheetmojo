"""
Signals that maintain denormalized counter fields so that no COUNT()
aggregation is needed on every page load.

Counters kept in sync:
  Channel.follower_count  ← ChannelFollow create/delete
  Channel.posts_count     ← Post create/delete
  Post.love_count         ← PostReaction create/delete
  Post.comment_count      ← Comment create/delete
  Post.saves_count        ← SavedPost create/delete
  Comment.love_count      ← CommentReaction create/delete
"""

from django.db.models import F
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Channel, ChannelFollow, Comment, CommentReaction, Post, PostReaction, SavedPost


# ---------------------------------------------------------------------------
# Channel.follower_count
# ---------------------------------------------------------------------------

@receiver(post_save, sender=ChannelFollow)
def on_channel_follow_save(sender, instance, created, **kwargs):
    if created:
        Channel.objects.filter(pk=instance.channel_id).update(follower_count=F("follower_count") + 1)


@receiver(post_delete, sender=ChannelFollow)
def on_channel_follow_delete(sender, instance, **kwargs):
    from django.db.models import F
    instance.channel.__class__.objects.filter(pk=instance.channel_id).update(
        follower_count=F("follower_count") - 1
    )


# ---------------------------------------------------------------------------
# Channel.posts_count
# ---------------------------------------------------------------------------

@receiver(post_save, sender=Post)
def on_post_save(sender, instance, created, **kwargs):
    if created:
        Channel.objects.filter(pk=instance.channel_id).update(posts_count=F("posts_count") + 1)


@receiver(post_delete, sender=Post)
def on_post_delete(sender, instance, **kwargs):
    Channel.objects.filter(pk=instance.channel_id).update(posts_count=F("posts_count") - 1)


# ---------------------------------------------------------------------------
# Post.love_count
# ---------------------------------------------------------------------------

@receiver(post_save, sender=PostReaction)
def on_post_reaction_save(sender, instance, created, **kwargs):
    if created:
        Post.objects.filter(pk=instance.post_id).update(love_count=F("love_count") + 1)


@receiver(post_delete, sender=PostReaction)
def on_post_reaction_delete(sender, instance, **kwargs):
    Post.objects.filter(pk=instance.post_id).update(love_count=F("love_count") - 1)


# ---------------------------------------------------------------------------
# Post.comment_count
# ---------------------------------------------------------------------------

@receiver(post_save, sender=Comment)
def on_comment_save(sender, instance, created, **kwargs):
    if created:
        Post.objects.filter(pk=instance.post_id).update(comment_count=F("comment_count") + 1)


@receiver(post_delete, sender=Comment)
def on_comment_delete(sender, instance, **kwargs):
    Post.objects.filter(pk=instance.post_id).update(comment_count=F("comment_count") - 1)


# ---------------------------------------------------------------------------
# Post.saves_count
# ---------------------------------------------------------------------------

@receiver(post_save, sender=SavedPost)
def on_saved_post_save(sender, instance, created, **kwargs):
    if created:
        Post.objects.filter(pk=instance.post_id).update(saves_count=F("saves_count") + 1)


@receiver(post_delete, sender=SavedPost)
def on_saved_post_delete(sender, instance, **kwargs):
    Post.objects.filter(pk=instance.post_id).update(saves_count=F("saves_count") - 1)


# ---------------------------------------------------------------------------
# Comment.love_count
# ---------------------------------------------------------------------------

@receiver(post_save, sender=CommentReaction)
def on_comment_reaction_save(sender, instance, created, **kwargs):
    if created:
        Comment.objects.filter(pk=instance.comment_id).update(love_count=F("love_count") + 1)


@receiver(post_delete, sender=CommentReaction)
def on_comment_reaction_delete(sender, instance, **kwargs):
    Comment.objects.filter(pk=instance.comment_id).update(love_count=F("love_count") - 1)

