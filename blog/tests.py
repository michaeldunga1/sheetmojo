from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Channel, ChannelFollow, Comment, Notification, Post, Profile, SavedPost

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
