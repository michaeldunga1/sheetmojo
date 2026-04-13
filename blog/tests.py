from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Channel, ChannelFollow, Comment, Post, Profile

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


class BlogViewAccessTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username="alice2", password="password123")
		self.other_user = User.objects.create_user(username="bob2", password="password123")
		self.channel = Channel.objects.create(owner=self.user, name="Alice channel")
		self.post = Post.objects.create(channel=self.channel, author=self.user, title="Hello", body="World")

	def test_user_can_comment_on_other_users_post(self):
		self.client.login(username="bob2", password="password123")

		response = self.client.post(
			reverse("blog:comment-create", kwargs={"post_pk": self.post.pk}),
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
			reverse("blog:comment-create", kwargs={"post_pk": self.post.pk}),
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

	def test_channel_detail_page_loads_by_slug(self):
		self.client.login(username="bob2", password="password123")

		response = self.client.get(reverse("blog:channel-detail", kwargs={"channel_slug": self.channel.slug}))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.channel.name)
		self.assertContains(response, self.post.title)

	def test_post_detail_page_loads(self):
		self.client.login(username="bob2", password="password123")

		response = self.client.get(reverse("blog:post-detail", kwargs={"pk": self.post.pk}))

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
