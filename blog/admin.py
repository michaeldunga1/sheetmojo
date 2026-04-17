from django.contrib import admin

from .models import Channel, ChannelEditor, ChannelFollow, Comment, Contact, NewsletterSubscription, Notification, Post, PostCoAuthor, Profile, SavedPost, Report, UserBlock


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "is_suspended", "suspended_until", "commenting_restricted_until", "country", "city")
	search_fields = ("user__username", "country", "city", "postal_code")
	list_filter = ("is_suspended",)


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "owner", "is_suspended", "comments_enabled", "created_at")
	search_fields = ("name", "owner__username")
	list_filter = ("is_suspended", "comments_enabled")


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


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
	list_display = ("id", "reporter", "content_type", "reason", "status", "created_at")
	search_fields = ("reporter__username", "reason", "status")
	list_filter = ("content_type", "status", "reason", "created_at")
	readonly_fields = ("created_at", "reviewed_at")
	fieldsets = (
		("Report Information", {
			"fields": ("reporter", "content_type", "reason", "description")
		}),
		("Content", {
			"fields": ("post", "comment", "channel", "reported_user")
		}),
		("Status", {
			"fields": ("status", "admin_notes", "created_at", "reviewed_at")
		}),
	)


@admin.register(UserBlock)
class UserBlockAdmin(admin.ModelAdmin):
	list_display = ("id", "blocker", "blocked", "created_at")
	search_fields = ("blocker__username", "blocked__username")


@admin.register(PostCoAuthor)
class PostCoAuthorAdmin(admin.ModelAdmin):
	list_display = ("id", "post", "user", "invited_by", "accepted", "created_at")
	list_filter = ("accepted",)
	search_fields = ("user__username", "invited_by__username", "post__title")


@admin.register(ChannelEditor)
class ChannelEditorAdmin(admin.ModelAdmin):
	list_display = ("id", "channel", "user", "invited_by", "accepted", "created_at")
	list_filter = ("accepted",)
	search_fields = ("user__username", "invited_by__username", "channel__name")

	search_fields = ("user__username", "invited_by__username", "channel__name")


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "email", "received_at", "read")
	search_fields = ("name", "email", "message")
	list_filter = ("read", "received_at")
	readonly_fields = ("received_at",)


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
	list_display = ("id", "email", "is_active", "subscribed_at")
	search_fields = ("email",)
	list_filter = ("is_active", "subscribed_at")
	readonly_fields = ("subscribed_at",)
