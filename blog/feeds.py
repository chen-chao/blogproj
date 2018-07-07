from django.contrib.syndication.views import Feed
from .models import Post


class AllPostsRssFeed(Feed):
    """docstring for AllPostsRssFeed"""
    title = "CChao"

    link = "/"

    description = "CChao's blog"

    def items(self):
        return Post.objects.all()

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.display()
