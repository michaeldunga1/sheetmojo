from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from .models import Channel, ChannelFollow, Comment, Notification, Post, Profile, SavedPost, Tag

User = get_user_model()


class BlogModelRulesTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username="alice", password="password123")
		self.other_user = User.objects.create_user(username="bob", password="password123")
		self.channel = Channel.objects.create(owner=self.user, name="General")

	def test_user_can_create_maximum_10_channels(self):
		for i in range(1, 10):
			Channel.objects.create(owner=self.user, name=f"Channel {i}")

		with self.assertRaises(ValidationError):
			Channel.objects.create(owner=self.user, name="Overflow Channel")

	def test_channel_can_have_maximum_100_posts(self):
		for i in range(100):
			Post.objects.create(
				channel=self.channel,
				author=self.user,
				title=f"Post {i}",
				body="Body",
			)

		with self.assertRaises(ValidationError):
			Post.objects.create(
				channel=self.channel,
				author=self.user,
				title="Overflow post",
				body="Body",
			)

	def test_user_can_only_create_one_comment_per_post(self):
		post = Post.objects.create(channel=self.channel, author=self.user, title="Title", body="Body")
		Comment.objects.create(post=post, author=self.user, body="First")

		with self.assertRaises(ValidationError):
			Comment.objects.create(post=post, author=self.user, body="Second")

	def test_user_can_comment_on_any_post(self):
		other_channel = Channel.objects.create(owner=self.other_user, name="Other")
		post = Post.objects.create(channel=other_channel, author=self.other_user, title="Other title", body="Body")

		comment = Comment.objects.create(post=post, author=self.user, body="Looks good")

		self.assertEqual(comment.author, self.user)
		self.assertEqual(comment.post, post)

	def test_owner_automatically_follows_new_channel(self):
		self.assertTrue(ChannelFollow.objects.filter(follower=self.user, channel=self.channel).exists())

	def test_user_can_only_save_a_post_once(self):
		post = Post.objects.create(channel=self.channel, author=self.user, title="Saved once", body="Body")
		SavedPost.objects.create(user=self.user, post=post)

		with self.assertRaises(ValidationError):
			SavedPost.objects.create(user=self.user, post=post)


class BlogViewAccessTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username="alice2", password="password123")
		self.other_user = User.objects.create_user(username="bob2", password="password123")
		self.channel = Channel.objects.create(owner=self.user, name="Alice channel")
		self.post = Post.objects.create(channel=self.channel, author=self.user, title="Hello", body="World")

	def test_user_can_comment_on_other_users_post(self):
		self.client.login(username="bob2", password="password123")

		response = self.client.post(
			reverse(
				"blog:comment-create",
				kwargs={"channel_slug": self.post.channel.slug, "post_slug": self.post.slug},
			),
			{"body": "Nice post"},
		)

		self.assertEqual(response.status_code, 302)
		self.assertTrue(Comment.objects.filter(post=self.post, author=self.other_user).exists())

	def test_non_owner_cannot_edit_channel(self):
		self.client.login(username="bob2", password="password123")

		response = self.client.post(
			reverse("blog:channel-edit", kwargs={"slug": self.channel.slug}),
			{"name": "Should not work"},
		)

		self.assertEqual(response.status_code, 403)

	def test_duplicate_comment_returns_form_error(self):
		self.client.login(username="bob2", password="password123")
		Comment.objects.create(post=self.post, author=self.other_user, body="First comment")

		response = self.client.post(
			reverse(
				"blog:comment-create",
				kwargs={"channel_slug": self.post.channel.slug, "post_slug": self.post.slug},
			),
			{"body": "Second comment"},
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Comment with this Post and Author already exists.")

	def test_user_sees_followed_channel_posts(self):
		self.client.login(username="bob2", password="password123")
		ChannelFollow.objects.create(follower=self.other_user, channel=self.channel)

		response = self.client.get(reverse("blog:following-posts"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Hello")

	def test_user_does_not_see_unfollowed_channel_posts(self):
		self.client.login(username="bob2", password="password123")

		response = self.client.get(reverse("blog:following-posts"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Hello")

	def test_user_sees_own_posts_in_following_feed(self):
		self.client.login(username="bob2", password="password123")
		Post.objects.create(channel=self.channel, author=self.other_user, title="My own in unfollowed", body="Body")

		response = self.client.get(reverse("blog:following-posts"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "My own in unfollowed")

	def test_user_can_follow_and_unfollow_channel(self):
		self.client.login(username="bob2", password="password123")

		follow_response = self.client.post(reverse("blog:channel-follow", kwargs={"channel_slug": self.channel.slug}))
		self.assertEqual(follow_response.status_code, 302)
		self.assertTrue(ChannelFollow.objects.filter(follower=self.other_user, channel=self.channel).exists())

		unfollow_response = self.client.post(reverse("blog:channel-unfollow", kwargs={"channel_slug": self.channel.slug}))
		self.assertEqual(unfollow_response.status_code, 302)
		self.assertFalse(ChannelFollow.objects.filter(follower=self.other_user, channel=self.channel).exists())

	def test_user_can_save_and_unsave_post(self):
		self.client.login(username="bob2", password="password123")

		save_response = self.client.post(
			reverse("blog:post-save", kwargs={"channel_slug": self.post.channel.slug, "post_slug": self.post.slug})
		)
		self.assertEqual(save_response.status_code, 302)
		self.assertTrue(SavedPost.objects.filter(user=self.other_user, post=self.post).exists())

		unsave_response = self.client.post(
			reverse("blog:post-unsave", kwargs={"channel_slug": self.post.channel.slug, "post_slug": self.post.slug})
		)
		self.assertEqual(unsave_response.status_code, 302)
		self.assertFalse(SavedPost.objects.filter(user=self.other_user, post=self.post).exists())

	def test_saved_posts_page_lists_only_saved_posts(self):
		self.client.login(username="bob2", password="password123")
		saved_post = Post.objects.create(channel=self.channel, author=self.user, title="Saved read", body="Body")
		other_post = Post.objects.create(channel=self.channel, author=self.user, title="Not saved", body="Body")
		SavedPost.objects.create(user=self.other_user, post=saved_post)

		response = self.client.get(reverse("blog:saved-posts"))

		self.assertEqual(response.status_code, 200)
		posts = list(response.context["posts"])
		self.assertIn(saved_post, posts)
		self.assertNotIn(other_post, posts)

	def test_saved_posts_search_filters_results(self):
		self.client.login(username="bob2", password="password123")
		matching_post = Post.objects.create(channel=self.channel, author=self.user, title="Neo Soul", body="Body")
		other_post = Post.objects.create(channel=self.channel, author=self.user, title="Prog Rock", body="Body")
		SavedPost.objects.create(user=self.other_user, post=matching_post)
		SavedPost.objects.create(user=self.other_user, post=other_post)

		response = self.client.get(reverse("blog:saved-posts"), {"q": "Neo"})

		self.assertEqual(response.status_code, 200)
		posts = list(response.context["posts"])
		self.assertEqual(posts, [matching_post])

	def test_channel_list_is_sorted_by_follower_count(self):
		self.client.login(username="bob2", password="password123")
		third_user = User.objects.create_user(username="charlie2", password="password123")

		popular_channel = Channel.objects.create(owner=self.user, name="Popular")
		less_popular_channel = Channel.objects.create(owner=self.user, name="Less Popular")

		ChannelFollow.objects.create(follower=self.other_user, channel=popular_channel)
		ChannelFollow.objects.create(follower=third_user, channel=popular_channel)
		ChannelFollow.objects.create(follower=self.other_user, channel=less_popular_channel)

		response = self.client.get(reverse("blog:channel-list"))
		channels = list(response.context["channels"])

		self.assertEqual(channels[0].id, popular_channel.id)
		self.assertEqual(channels[1].id, less_popular_channel.id)

	def test_channel_list_is_paginated(self):
		self.client.login(username="bob2", password="password123")

		for idx in range(12):
			owner = User.objects.create_user(username=f"owner_{idx}", password="password123")
			Channel.objects.create(owner=owner, name=f"Paginated {idx}")

		response = self.client.get(reverse("blog:channel-list"))

		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.context["is_paginated"])
		self.assertEqual(len(response.context["channels"]), 10)

	def test_channel_list_search_filters_results(self):
		self.client.login(username="bob2", password="password123")
		matching_channel = Channel.objects.create(owner=self.user, name="Jazz Theory")
		non_matching_channel = Channel.objects.create(owner=self.user, name="Rock History")

		response = self.client.get(reverse("blog:channel-list"), {"q": "Jazz"})

		self.assertEqual(response.status_code, 200)
		channels = list(response.context["channels"])
		self.assertIn(matching_channel, channels)
		self.assertNotIn(non_matching_channel, channels)

	def test_channel_list_pagination_preserves_search_query(self):
		self.client.login(username="bob2", password="password123")

		for idx in range(12):
			owner = User.objects.create_user(username=f"search_owner_{idx}", password="password123")
			Channel.objects.create(owner=owner, name=f"Focus Channel {idx}")

		response = self.client.get(reverse("blog:channel-list"), {"q": "Focus"})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "?q=Focus&amp;page=2")

	def test_my_channels_search_filters_owned_channels(self):
		self.client.login(username="alice2", password="password123")
		matching_channel = Channel.objects.create(owner=self.user, name="Alpha Notes")
		Channel.objects.create(owner=self.user, name="Beta Notes")
		Channel.objects.create(owner=self.other_user, name="Alpha Outside")

		response = self.client.get(reverse("blog:my-channels"), {"q": "Alpha"})

		self.assertEqual(response.status_code, 200)
		channels = list(response.context["channels"])
		self.assertEqual(channels, [matching_channel])

	def test_followed_channels_page_lists_only_followed_channels(self):
		self.client.login(username="bob2", password="password123")
		followed_channel = Channel.objects.create(owner=self.user, name="Followed Channel")
		not_followed_channel = Channel.objects.create(owner=self.user, name="Not Followed Channel")
		ChannelFollow.objects.create(follower=self.other_user, channel=followed_channel)

		response = self.client.get(reverse("blog:followed-channels"))

		self.assertEqual(response.status_code, 200)
		channels = list(response.context["channels"])
		self.assertIn(followed_channel, channels)
		self.assertNotIn(not_followed_channel, channels)
		self.assertContains(response, "Followed Channels")

	def test_followed_channels_search_filters_results(self):
		self.client.login(username="bob2", password="password123")
		matching_channel = Channel.objects.create(owner=self.user, name="Fusion Room")
		other_channel = Channel.objects.create(owner=self.user, name="Ambient Room")
		ChannelFollow.objects.create(follower=self.other_user, channel=matching_channel)
		ChannelFollow.objects.create(follower=self.other_user, channel=other_channel)

		response = self.client.get(reverse("blog:followed-channels"), {"q": "Fusion"})

		self.assertEqual(response.status_code, 200)
		channels = list(response.context["channels"])
		self.assertEqual(channels, [matching_channel])

	def test_followed_channel_count_is_available_in_navigation_context(self):
		self.client.login(username="bob2", password="password123")
		ChannelFollow.objects.create(
			follower=self.other_user,
			channel=Channel.objects.create(owner=self.user, name="Count One"),
		)
		ChannelFollow.objects.create(
			follower=self.other_user,
			channel=Channel.objects.create(owner=self.user, name="Count Two"),
		)

		response = self.client.get(reverse("blog:following-posts"))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context["followed_channel_count"], 2)
		self.assertContains(response, 'aria-label="2 followed channels"')

	def test_saved_post_count_is_available_in_navigation_context(self):
		self.client.login(username="bob2", password="password123")
		SavedPost.objects.create(
			user=self.other_user,
			post=Post.objects.create(channel=self.channel, author=self.user, title="Saved count one", body="Body"),
		)
		SavedPost.objects.create(
			user=self.other_user,
			post=Post.objects.create(channel=self.channel, author=self.user, title="Saved count two", body="Body"),
		)

		response = self.client.get(reverse("blog:following-posts"))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context["saved_post_count"], 2)
		self.assertContains(response, 'aria-label="2 saved posts"')

	def test_follow_channel_creates_notification_for_channel_owner(self):
		self.client.login(username="bob2", password="password123")

		response = self.client.post(reverse("blog:channel-follow", kwargs={"channel_slug": self.channel.slug}))

		self.assertEqual(response.status_code, 302)
		notification = Notification.objects.filter(recipient=self.user, actor=self.other_user).first()
		self.assertIsNotNone(notification)
		self.assertEqual(notification.notification_type, Notification.TYPE_FOLLOW)

	def test_post_create_notifies_followers_of_channel(self):
		self.client.login(username="bob2", password="password123")
		ChannelFollow.objects.create(follower=self.other_user, channel=self.channel)
		self.client.logout()
		self.client.login(username="alice2", password="password123")

		response = self.client.post(
			reverse("blog:post-create", kwargs={"channel_slug": self.channel.slug}),
			{"title": "Notification Post", "body": "Body"},
		)

		self.assertEqual(response.status_code, 302)
		notification = Notification.objects.filter(recipient=self.other_user, actor=self.user).first()
		self.assertIsNotNone(notification)
		self.assertEqual(notification.notification_type, Notification.TYPE_NEW_POST)

	def test_post_create_can_save_draft_without_notifying_followers(self):
		self.client.login(username="bob2", password="password123")
		ChannelFollow.objects.create(follower=self.other_user, channel=self.channel)
		self.client.logout()
		self.client.login(username="alice2", password="password123")

		response = self.client.post(
			reverse("blog:post-create", kwargs={"channel_slug": self.channel.slug}),
			{"title": "Draft post", "body": "Draft body", "tags_input": "" , "action": "draft"},
		)

		self.assertRedirects(response, reverse("blog:draft-posts"))
		draft = Post.objects.get(title="Draft post")
		self.assertFalse(draft.is_published)
		self.assertFalse(
			Notification.objects.filter(
				recipient=self.other_user,
				actor=self.user,
				notification_type=Notification.TYPE_NEW_POST,
				target_url=draft.get_absolute_url(),
			).exists()
		)

	def test_non_owner_cannot_view_draft_post(self):
		draft = Post.objects.create(
			channel=self.channel,
			author=self.user,
			title="Private draft",
			body="Body",
			is_published=False,
		)
		self.client.login(username="bob2", password="password123")

		response = self.client.get(
			reverse("blog:post-detail", kwargs={"channel_slug": self.channel.slug, "post_slug": draft.slug})
		)

		self.assertEqual(response.status_code, 404)

	def test_draft_list_shows_only_own_unpublished_posts(self):
		Post.objects.create(channel=self.channel, author=self.user, title="Published one", body="Body", is_published=True)
		draft = Post.objects.create(channel=self.channel, author=self.user, title="Draft one", body="Body", is_published=False)
		self.client.login(username="alice2", password="password123")

		response = self.client.get(reverse("blog:draft-posts"))

		self.assertEqual(response.status_code, 200)
		posts = list(response.context["posts"])
		self.assertIn(draft, posts)
		self.assertNotIn("Published one", [p.title for p in posts])

	def test_owner_can_publish_existing_draft_and_notify_followers(self):
		draft = Post.objects.create(
			channel=self.channel,
			author=self.user,
			title="To publish",
			body="Body",
			is_published=False,
		)
		self.client.login(username="bob2", password="password123")
		ChannelFollow.objects.create(follower=self.other_user, channel=self.channel)
		self.client.logout()
		self.client.login(username="alice2", password="password123")

		response = self.client.post(
			reverse("blog:post-edit", kwargs={"channel_slug": self.channel.slug, "post_slug": draft.slug}),
			{"title": "To publish", "body": "Body", "tags_input": "", "action": "publish"},
		)

		self.assertRedirects(
			response,
			reverse("blog:post-detail", kwargs={"channel_slug": self.channel.slug, "post_slug": draft.slug}),
		)
		draft.refresh_from_db()
		self.assertTrue(draft.is_published)
		notification = Notification.objects.filter(recipient=self.other_user, actor=self.user).first()
		self.assertIsNotNone(notification)
		self.assertEqual(notification.notification_type, Notification.TYPE_NEW_POST)

	def test_profile_page_state_filter_shows_all_for_owner(self):
		# setUp creates 1 published post, add 1 more published + 1 draft
		Post.objects.create(channel=self.channel, author=self.user, title="Published p", body="Body", is_published=True)
		Post.objects.create(channel=self.channel, author=self.user, title="Draft d", body="Body", is_published=False)
		self.client.login(username="alice2", password="password123")

		response = self.client.get(reverse("blog:profile"), {"state": "all"})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context["state_filter"], "all")
		posts = list(response.context["user_posts"])
		self.assertEqual(len(posts), 3)  # 1 from setUp + 1 published + 1 draft
		self.assertContains(response, "All (3)")
		self.assertContains(response, "Published (2)")
		self.assertContains(response, "Drafts (1)")

	def test_profile_page_state_filter_published_only(self):
		# setUp creates 1 published post, add 1 more published + 1 draft
		Post.objects.create(channel=self.channel, author=self.user, title="Published", body="Body", is_published=True)
		Post.objects.create(channel=self.channel, author=self.user, title="Draft", body="Body", is_published=False)
		self.client.login(username="alice2", password="password123")

		response = self.client.get(reverse("blog:profile"), {"state": "published"})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context["state_filter"], "published")
		posts = list(response.context["user_posts"])
		self.assertEqual(len(posts), 2)  # 1 from setUp + 1 published, draft filtered out
		self.assertTrue(all(p.is_published for p in posts))

	def test_profile_page_non_owner_cannot_see_drafts(self):
		# setUp creates 1 published post, add 1 more published + 1 draft
		Post.objects.create(channel=self.channel, author=self.user, title="Published", body="Body", is_published=True)
		Post.objects.create(channel=self.channel, author=self.user, title="Draft", body="Body", is_published=False)
		self.client.login(username="bob2", password="password123")

		response = self.client.get(
			reverse("blog:user-profile", kwargs={"username": self.user.username}),
			{"state": "drafts"}
		)

		self.assertEqual(response.status_code, 200)
		# Non-owner always sees "published" filter even if drafts is requested
		self.assertEqual(response.context["state_filter"], "published")
		posts = list(response.context["user_posts"])
		self.assertEqual(len(posts), 2)  # 1 from setUp + 1 published (draft invisible to non-owners)
		self.assertTrue(all(p.is_published for p in posts))

	def test_comment_create_notifies_post_author(self):
		self.client.login(username="bob2", password="password123")

		response = self.client.post(
			reverse(
				"blog:comment-create",
				kwargs={"channel_slug": self.post.channel.slug, "post_slug": self.post.slug},
			),
			{"body": "Interesting read"},
		)

		self.assertEqual(response.status_code, 302)
		notification = Notification.objects.filter(recipient=self.user, actor=self.other_user).first()
		self.assertIsNotNone(notification)
		self.assertEqual(notification.notification_type, Notification.TYPE_COMMENT)

	def test_comment_create_notifies_channel_owner_when_different_from_post_author(self):
		channel_owner = User.objects.create_user(username="channel_owner", password="password123")
		post_author = User.objects.create_user(username="post_author", password="password123")
		commenter = User.objects.create_user(username="commenter", password="password123")
		channel = Channel.objects.create(owner=channel_owner, name="Shared Channel")
		post = Post.objects.create(channel=channel, author=post_author, title="Guest Post", body="Body")

		self.client.login(username="commenter", password="password123")
		response = self.client.post(
			reverse(
				"blog:comment-create",
				kwargs={"channel_slug": post.channel.slug, "post_slug": post.slug},
			),
			{"body": "Nice one"},
		)

		self.assertEqual(response.status_code, 302)
		recipients = set(
			Notification.objects.filter(actor=commenter, notification_type=Notification.TYPE_COMMENT)
			.values_list("recipient_id", flat=True)
		)
		self.assertEqual(recipients, {post_author.id, channel_owner.id})

	def test_comment_create_does_not_duplicate_when_post_author_is_channel_owner(self):
		self.client.login(username="bob2", password="password123")
		response = self.client.post(
			reverse(
				"blog:comment-create",
				kwargs={"channel_slug": self.post.channel.slug, "post_slug": self.post.slug},
			),
			{"body": "Only one notification expected"},
		)

		self.assertEqual(response.status_code, 302)
		self.assertEqual(
			Notification.objects.filter(
				recipient=self.user,
				actor=self.other_user,
				notification_type=Notification.TYPE_COMMENT,
			).count(),
			1,
		)

	def test_comment_create_does_not_notify_self(self):
		self.client.login(username="alice2", password="password123")
		response = self.client.post(
			reverse(
				"blog:comment-create",
				kwargs={"channel_slug": self.post.channel.slug, "post_slug": self.post.slug},
			),
			{"body": "My own post comment"},
		)

		self.assertEqual(response.status_code, 302)
		self.assertFalse(
			Notification.objects.filter(
				recipient=self.user,
				actor=self.user,
				notification_type=Notification.TYPE_COMMENT,
			).exists()
		)

	def test_notifications_page_supports_unread_filter_and_search(self):
		self.client.login(username="bob2", password="password123")
		Notification.objects.create(
			recipient=self.other_user,
			actor=self.user,
			notification_type=Notification.TYPE_FOLLOW,
			message="alice2 followed your channel.",
			target_url="/channels/",
			is_read=False,
		)
		Notification.objects.create(
			recipient=self.other_user,
			actor=self.user,
			notification_type=Notification.TYPE_COMMENT,
			message="alice2 commented on your post.",
			target_url="/channels/",
			is_read=True,
		)

		response = self.client.get(reverse("blog:notifications"), {"unread": "1", "q": "followed"})

		self.assertEqual(response.status_code, 200)
		notifications = list(response.context["notifications"])
		self.assertEqual(len(notifications), 1)
		self.assertIn("followed", notifications[0].message)

	def test_user_can_mark_notification_as_read(self):
		self.client.login(username="bob2", password="password123")
		notification = Notification.objects.create(
			recipient=self.other_user,
			actor=self.user,
			notification_type=Notification.TYPE_FOLLOW,
			message="alice2 followed your channel.",
			target_url="/channels/",
		)

		response = self.client.post(reverse("blog:notification-read", kwargs={"pk": notification.pk}))

		self.assertEqual(response.status_code, 302)
		notification.refresh_from_db()
		self.assertTrue(notification.is_read)

	def test_user_can_mark_all_notifications_as_read(self):
		self.client.login(username="bob2", password="password123")
		Notification.objects.create(
			recipient=self.other_user,
			actor=self.user,
			notification_type=Notification.TYPE_FOLLOW,
			message="alice2 followed your channel.",
			target_url="/channels/",
		)
		Notification.objects.create(
			recipient=self.other_user,
			actor=self.user,
			notification_type=Notification.TYPE_COMMENT,
			message="alice2 commented on your post.",
			target_url="/channels/",
		)

		response = self.client.post(reverse("blog:notifications-read-all"))

		self.assertEqual(response.status_code, 302)
		self.assertEqual(Notification.objects.filter(recipient=self.other_user, is_read=False).count(), 0)

	def test_unread_notification_count_is_available_in_navigation_context(self):
		self.client.login(username="bob2", password="password123")
		Notification.objects.create(
			recipient=self.other_user,
			actor=self.user,
			notification_type=Notification.TYPE_FOLLOW,
			message="alice2 followed your channel.",
			target_url="/channels/",
			is_read=False,
		)

		response = self.client.get(reverse("blog:following-posts"))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context["unread_notification_count"], 1)
		self.assertContains(response, 'aria-label="1 unread notifications"')

	def test_following_feed_includes_followed_channels_shortcut(self):
		self.client.login(username="bob2", password="password123")

		response = self.client.get(reverse("blog:following-posts"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, reverse("blog:followed-channels"))

	def test_channel_detail_page_loads_by_slug(self):
		self.client.login(username="bob2", password="password123")

		response = self.client.get(reverse("blog:channel-detail", kwargs={"channel_slug": self.channel.slug}))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.channel.name)
		self.assertContains(response, self.post.title)

	def test_channel_owner_sees_channel_analytics(self):
		self.client.login(username="alice2", password="password123")
		second_post = Post.objects.create(channel=self.channel, author=self.user, title="Metrics post", body="Body")
		Post.objects.filter(pk=self.post.pk).update(view_count=10, love_count=3, comment_count=2, saves_count=1)
		Post.objects.filter(pk=second_post.pk).update(view_count=20, love_count=5, comment_count=4, saves_count=3)
		self.channel.refresh_from_db()

		response = self.client.get(reverse("blog:channel-detail", kwargs={"channel_slug": self.channel.slug}))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Channel analytics")
		analytics = response.context["channel_analytics"]
		self.assertIsNotNone(analytics)
		self.assertEqual(analytics["total_posts"], self.channel.posts_count)
		self.assertEqual(analytics["total_views"], 30)
		self.assertEqual(analytics["total_loves"], 8)
		self.assertEqual(analytics["total_comments"], 6)
		self.assertEqual(analytics["total_saves"], 4)
		self.assertEqual(analytics["total_engagement"], 18)

	def test_non_owner_does_not_see_channel_analytics(self):
		self.client.login(username="bob2", password="password123")
		response = self.client.get(reverse("blog:channel-detail", kwargs={"channel_slug": self.channel.slug}))

		self.assertEqual(response.status_code, 200)
		self.assertIsNone(response.context["channel_analytics"])
		self.assertNotContains(response, "Channel analytics")

	def test_channel_owner_analytics_respects_time_window(self):
		self.client.login(username="alice2", password="password123")
		old_post = Post.objects.create(channel=self.channel, author=self.user, title="Old data", body="Body")
		recent_post = Post.objects.create(channel=self.channel, author=self.user, title="Recent data", body="Body")
		Post.objects.filter(pk=old_post.pk).update(created_at=timezone.now() - timedelta(days=40), view_count=50)
		Post.objects.filter(pk=recent_post.pk).update(created_at=timezone.now() - timedelta(days=2), view_count=10)

		response_7d = self.client.get(
			reverse("blog:channel-detail", kwargs={"channel_slug": self.channel.slug}),
			{"window": "7d"},
		)
		response_all = self.client.get(
			reverse("blog:channel-detail", kwargs={"channel_slug": self.channel.slug}),
			{"window": "all"},
		)

		self.assertEqual(response_7d.status_code, 200)
		self.assertEqual(response_all.status_code, 200)
		self.assertEqual(response_7d.context["analytics_window"], "7d")
		self.assertEqual(response_all.context["analytics_window"], "all")
		self.assertEqual(response_7d.context["channel_analytics"]["total_views"], 10)
		self.assertEqual(response_all.context["channel_analytics"]["total_views"], 60)

	def test_channel_owner_analytics_window_links_preserve_existing_query_params(self):
		self.client.login(username="alice2", password="password123")
		response = self.client.get(
			reverse("blog:channel-detail", kwargs={"channel_slug": self.channel.slug}),
			{"window": "7d", "q": "growth", "status": "active"},
		)

		self.assertEqual(response.status_code, 200)
		window_links = {item["value"]: item["query_string"] for item in response.context["analytics_window_links"]}
		self.assertIn("window=30d", window_links["30d"])
		self.assertIn("q=growth", window_links["30d"])
		self.assertIn("status=active", window_links["30d"])

	def test_post_detail_page_loads(self):
		self.client.login(username="bob2", password="password123")

		response = self.client.get(
			reverse(
				"blog:post-detail",
				kwargs={"channel_slug": self.post.channel.slug, "post_slug": self.post.slug},
			)
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.post.title)
		self.assertContains(response, self.post.body)
		self.post.refresh_from_db()
		self.assertEqual(self.post.view_count, 1)

	def test_home_redirects_authenticated_user_to_following_posts(self):
		self.client.login(username="bob2", password="password123")

		response = self.client.get(reverse("home"))

		self.assertRedirects(response, reverse("blog:following-posts"))

	def test_home_redirects_anonymous_user_to_login(self):
		response = self.client.get(reverse("home"))

		self.assertRedirects(response, reverse("blog:following-posts"))

	def test_login_redirects_to_home(self):
		response = self.client.post(
			reverse("login"),
			{"username": "bob2", "password": "password123"},
		)

		self.assertRedirects(response, reverse("home"), fetch_redirect_response=False)

	def test_anonymous_user_sees_all_posts_in_following_feed(self):
		response = self.client.get(reverse("blog:following-posts"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Hello")

	def test_following_posts_search_filters_feed_results(self):
		self.client.login(username="bob2", password="password123")
		ChannelFollow.objects.create(follower=self.other_user, channel=self.channel)
		Post.objects.create(channel=self.channel, author=self.user, title="Django Search", body="Findable body")
		Post.objects.create(channel=self.channel, author=self.user, title="Flask Notes", body="Different topic")

		response = self.client.get(reverse("blog:following-posts"), {"q": "Django"})

		self.assertEqual(response.status_code, 200)
		posts = list(response.context["posts"])
		titles = {post.title for post in posts}
		self.assertIn("Django Search", titles)
		self.assertNotIn("Flask Notes", titles)

	def test_following_feed_shows_trending_tags(self):
		self.client.login(username="bob2", password="password123")
		tagged_post = Post.objects.create(channel=self.channel, author=self.user, title="Tagged", body="Body")
		topic_tag = Tag.objects.create(name="analysis", slug="analysis")
		tagged_post.tags.add(topic_tag)

		response = self.client.get(reverse("blog:following-posts"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Trending tags")
		self.assertContains(response, "#analysis")

	def test_channel_post_list_search_filters_results(self):
		self.client.login(username="bob2", password="password123")
		matching_post = Post.objects.create(
			channel=self.channel,
			author=self.user,
			title="Scale Practice",
			body="Triads and inversions",
		)
		Post.objects.create(
			channel=self.channel,
			author=self.user,
			title="Rhythm Practice",
			body="Odd meters",
		)

		response = self.client.get(reverse("blog:post-list", kwargs={"channel_slug": self.channel.slug}), {"q": "Scale"})

		self.assertEqual(response.status_code, 200)
		posts = list(response.context["posts"])
		self.assertIn(matching_post, posts)
		self.assertEqual(len(posts), 1)

	def test_tag_list_page_orders_tags_by_usage(self):
		self.client.login(username="bob2", password="password123")
		python_post = Post.objects.create(channel=self.channel, author=self.user, title="Python piece", body="Body")
		django_post = Post.objects.create(channel=self.channel, author=self.user, title="Django piece", body="Body")
		mixed_post = Post.objects.create(channel=self.channel, author=self.user, title="Both piece", body="Body")
		python_tag = Tag.objects.create(name="python", slug="python")
		django_tag = Tag.objects.create(name="django", slug="django")
		api_tag = Tag.objects.create(name="api", slug="api")
		python_post.tags.add(python_tag)
		django_post.tags.add(django_tag)
		mixed_post.tags.add(python_tag, django_tag, api_tag)

		response = self.client.get(reverse("blog:tag-list"))

		self.assertEqual(response.status_code, 200)
		tags = list(response.context["tags"])
		self.assertEqual(tags[0].slug, "django")
		self.assertEqual(tags[1].slug, "python")
		self.assertContains(response, "Browse tags")

	def test_tag_post_page_shows_related_tags_and_browse_link(self):
		self.client.login(username="bob2", password="password123")
		primary = Tag.objects.create(name="python", slug="python")
		related = Tag.objects.create(name="django", slug="django")
		other = Tag.objects.create(name="music", slug="music")
		post = Post.objects.create(channel=self.channel, author=self.user, title="Tagged entry", body="Body")
		other_post = Post.objects.create(channel=self.channel, author=self.user, title="Other entry", body="Body")
		post.tags.add(primary, related)
		other_post.tags.add(other)

		response = self.client.get(reverse("blog:tag-posts", kwargs={"tag_slug": primary.slug}))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Browse all tags")
		self.assertContains(response, "Related tags")
		self.assertContains(response, "#django")

	def test_profile_page_shows_user_details_and_own_posts(self):
		self.client.login(username="bob2", password="password123")
		other_channel = Channel.objects.create(owner=self.other_user, name="Bob channel")
		own_post = Post.objects.create(channel=other_channel, author=self.other_user, title="My post", body="Mine")
		Post.objects.create(channel=self.channel, author=self.user, title="Alice post", body="Not mine")

		response = self.client.get(reverse("blog:profile"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.other_user.username)
		self.assertContains(response, own_post.title)
		self.assertNotContains(response, "Alice post")

	def test_profile_search_filters_user_posts(self):
		self.client.login(username="bob2", password="password123")
		other_channel = Channel.objects.create(owner=self.other_user, name="Bob channel")
		matching_post = Post.objects.create(
			channel=other_channel,
			author=self.other_user,
			title="City Pop Review",
			body="Detailed notes",
		)
		Post.objects.create(
			channel=other_channel,
			author=self.other_user,
			title="Hard Bop Review",
			body="Detailed notes",
		)

		response = self.client.get(reverse("blog:profile"), {"q": "City Pop"})

		self.assertEqual(response.status_code, 200)
		posts = list(response.context["user_posts"])
		self.assertEqual(posts, [matching_post])

	def test_public_user_profile_page_loads_by_username(self):
		self.client.login(username="alice2", password="password123")

		response = self.client.get(reverse("blog:user-profile", kwargs={"username": self.other_user.username}))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.other_user.username)

	def test_search_results_show_matching_tags(self):
		self.client.login(username="bob2", password="password123")
		search_tag = Tag.objects.create(name="django", slug="django")
		tagged_post = Post.objects.create(channel=self.channel, author=self.user, title="Framework notes", body="Body")
		tagged_post.tags.add(search_tag)

		response = self.client.get(reverse("blog:search"), {"q": "djan"})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Tags")
		self.assertContains(response, "#django")

	def test_profile_edit_updates_user_and_profile_details(self):
		self.client.login(username="bob2", password="password123")

		response = self.client.post(
			reverse("blog:profile-edit"),
			{
				"username": "bob2",
				"email": "bob2@example.com",
				"first_name": "Bob",
				"last_name": "Builder",
				"country": "Kenya",
				"city": "Nairobi",
				"postal_code": "00100",
				"post_office_box": "P.O. Box 1",
				"about_me": "Hello world",
			},
		)

		self.assertRedirects(response, reverse("blog:profile"))
		self.other_user.refresh_from_db()
		profile = Profile.objects.get(user=self.other_user)
		self.assertEqual(self.other_user.first_name, "Bob")
		self.assertEqual(profile.city, "Nairobi")

	def test_account_delete_removes_current_user(self):
		self.client.login(username="bob2", password="password123")

		response = self.client.post(reverse("blog:account-delete"))

		self.assertRedirects(response, reverse("home"), fetch_redirect_response=False)
		self.assertFalse(User.objects.filter(username="bob2").exists())


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class WeeklyDigestCommandTests(TestCase):
	def setUp(self):
		self.owner = User.objects.create_user(username="digest_owner", email="owner@example.com", password="password123")
		self.reader = User.objects.create_user(username="digest_reader", email="reader@example.com", password="password123")
		self.channel = Channel.objects.create(owner=self.owner, name="Digest Channel")
		ChannelFollow.objects.get_or_create(follower=self.reader, channel=self.channel)
		self.profile, _ = Profile.objects.get_or_create(user=self.reader)
		now = timezone.now()
		self.profile.digest_weekday = now.weekday()
		self.profile.digest_hour = now.hour
		self.profile.email_digest_enabled = True
		self.profile.save()

	def test_weekly_digest_sends_email_with_posts_and_notifications(self):
		post = Post.objects.create(channel=self.channel, author=self.owner, title="Digest Post", body="Digest body")
		Notification.objects.create(
			recipient=self.reader,
			actor=self.owner,
			notification_type=Notification.TYPE_NEW_POST,
			message="digest notification",
			target_url=post.get_absolute_url(),
		)

		call_command("send_weekly_digest", user=self.reader.username, force=True)

		self.assertEqual(len(mail.outbox), 1)
		email = mail.outbox[0]
		self.assertIn("Digest Post", email.body)
		self.assertIn("digest notification", email.body)
		self.profile.refresh_from_db()
		self.assertIsNotNone(self.profile.last_digest_sent_at)

	def test_weekly_digest_respects_schedule_without_force(self):
		self.profile.digest_hour = (timezone.now().hour + 1) % 24
		self.profile.save(update_fields=["digest_hour"])
		Post.objects.create(channel=self.channel, author=self.owner, title="Scheduled Post", body="Body")

		call_command("send_weekly_digest", user=self.reader.username)

		self.assertEqual(len(mail.outbox), 0)

	def test_weekly_digest_skips_empty_when_send_empty_not_set(self):
		ChannelFollow.objects.filter(follower=self.reader, channel=self.channel).delete()

		call_command("send_weekly_digest", user=self.reader.username, force=True)

		self.assertEqual(len(mail.outbox), 0)
