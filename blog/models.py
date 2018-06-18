# coding: utf-8
from markdown2 import markdown
from django.utils.html import strip_tags
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.six import python_2_unicode_compatible
from django.core.files.base import ContentFile
from taggit.managers import TaggableManager


@python_2_unicode_compatible
class Post(models.Model):
    """Post"""
    title = models.CharField(max_length=70)
    body = models.TextField()
    html_file = models.FileField(upload_to='source/%Y/', blank=True)

    created_time = models.DateTimeField('date published', auto_now_add=True)
    modified_time = models.DateTimeField('date edited', auto_now_add=True)

    # 文章摘要
    excerpect = models.CharField(max_length=200, blank=True)

    tags = TaggableManager()

    # keep posts when user deleted
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    count_read = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})

    def increase_views(self):
        self.count_read += 1
        self.save(update_fields=['count_read'])

    # overwrite models.save
    def save(self, *args, **kwargs):
        # TODO: add support to .rst .org .html
        if not self.html_file:
            html = markdown(self.body, extras=['fenced-code-blocks', 'tables'])
            if not self.excerpect:
                # TODO: header included
                self.excerpect = strip_tags(html)[:100]
            self.html_file.save(self.title + '.html',
                                ContentFile(html.encode('utf-8')), save=False)
            self.html_file.close()
        super().save(*args, **kwargs)

    # delte html file when post deleted
    def delete(self, *args, **kwargs):
        if self.html_file:
            self.html_file.delete(save=False)
        super().delete(*args, **kwargs)

    def display(self):
        with open(self.html_file.path, encoding='utf-8') as f:
            return f.read()

    class Meta:
        ordering = ['-created_time', '-modified_time']


class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name='images',
                             on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
