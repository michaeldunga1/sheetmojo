from django.contrib import admin

from .models import Channel, ChannelFollow, Comment, Notification, Post, Profile, SavedPost


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ("id", "country", "city", "postal_code", "post_office_box")
	search_fields = ("country", "city", "postal_code")


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "owner", "created_at")
	search_fields = ("name", "owner__username")


@admin.register(ChannelFollow)
class ChannelFollowAdmin(admin.ModelAdmin):
	list_display = ("id", "follower", "channel", "created_at")
	search_fields = ("follower__username", "channel__name", "channel__owner__username")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
	list_display = ("id", "title", "channel", "author", "created_at")
	search_fields = ("title", "author__username", "channel__name")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ("id", "post", "author", "created_at")
	search_fields = ("post__title", "author__username")


@admin.register(SavedPost)
class SavedPostAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "post", "created_at")
	search_fields = ("user__username", "post__title", "post__channel__name")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ("id", "recipient", "actor", "notification_type", "is_read", "created_at")
	search_fields = ("recipient__username", "actor__username", "message")
