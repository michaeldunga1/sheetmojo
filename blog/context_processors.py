from .models import ChannelFollow, Notification, SavedPost


def followed_channels(request):
	if not request.user.is_authenticated:
		return {"followed_channel_count": 0, "saved_post_count": 0, "unread_notification_count": 0}

	return {
		"followed_channel_count": ChannelFollow.objects.filter(follower=request.user).count(),
		"saved_post_count": SavedPost.objects.filter(user=request.user).count(),
		"unread_notification_count": Notification.objects.filter(recipient=request.user, is_read=False).count(),
	}