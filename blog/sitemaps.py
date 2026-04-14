from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Channel, Post


class StaticViewSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return ["home", "login", "blog:register"]

    def location(self, item):
        return reverse(item)


class ChannelSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Channel.objects.all().order_by("-created_at")


class PostSitemap(Sitemap):
    changefreq = "hourly"
    priority = 0.8

    def items(self):
        return Post.objects.select_related("channel").all().order_by("-created_at")
