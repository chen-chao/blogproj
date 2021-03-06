# coding: utf-8
import os.path
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager


class Post(models.Model):
    """Post"""

    title = models.CharField(max_length=70, unique=True)
    html_file = models.FileField(upload_to='source/%Y/')
    toc = models.TextField(blank=True)

    created_time = models.DateTimeField('date published', auto_now_add=True)
    modified_time = models.DateTimeField('last edited', auto_now=True)

    # 文章摘要
    excerpect = models.CharField(max_length=200, blank=True)

    tags = TaggableManager(blank=True)

    # keep posts when user deleted
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})

    # overwrite models.save
    def save(self, toc=None, excerpt=None, *args, **kwargs):
        if toc:
            self.toc = toc
        if excerpt:
            self.excerpect = excerpt
        super().save(*args, **kwargs)

    # delete html file when post deleted
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

    def __str__(self):
        return os.path.basename(self.image.path)
