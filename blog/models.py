# coding: utf-8
import os.path
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.six import python_2_unicode_compatible
from taggit.managers import TaggableManager
import lxml.html
from datetime import datetime


def get_html_toc(htmltree, level=3):
    headings = '//h2'
    for i in range(3, level+1):
        headings += '|//h%d' % i

    toc = '<ul> '
    last_tag = 2
    for heading in htmltree.xpath(headings):
        current_tag = int(heading.tag[1:])
        if current_tag > last_tag:
            toc += '<ul>\n'
        elif current_tag < last_tag:
            toc += ' </ul>\n'
        id_ = heading.attrib.get('id', '')
        text = heading.text_content()
        toc += '<li> <a href="#%s"> %s </a> </li>\n' % (id_, text)
        last_tag = current_tag
    toc += ' </ul>\n'

    return toc


def get_html_excerpt(htmltree, length=200):
    paragraph = htmltree.xpath('//p[1]')[0]
    return paragraph.text_content().strip()[:length]


@python_2_unicode_compatible
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
        html = self.display()
        tree = lxml.html.fromstring(html)
        self.toc = get_html_toc(tree)
        self.excerpect = get_html_excerpt(tree)

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
