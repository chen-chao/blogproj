# coding: utf-8
import os.path
from django.utils.html import strip_tags
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.six import python_2_unicode_compatible
from django.core.files.base import ContentFile
from taggit.managers import TaggableManager
import markdown
import requests
import json
import lxml
from lxml.html import tostring
from datetime import datetime


def _github_parse_markdown(text, mode='gfm', context=None):
    payload = {'text': text, 'mode': mode}
    if context:
        payload['conext'] = context
    resp = requests.post('https://api.github.com/markdown/',
                         data=json.dumps(payload))
    if resp.ok:
        return resp.content.decode('utf-8')

    raise TypeError('Cannot parse markdown file, status code {}'.format(
        resp.status_code))


def get_html_toc_excerpt(html: str, level=3, length=200):
    tree = lxml.html.fromstring(html)
    headings = '//h2'
    for i in range(3, level+1):
        headings += '|//h%d' % i

    toc = '<ul> '
    last_tag = 2
    for heading in tree.xpath(headings):
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

    try:
        h1 = tree.xpath('//h1')[0]
        h1.drop_tree()
    except IndexError:
        pass

    html_no_h1 = tostring(tree, encoding='unicode')
    return toc, strip_tags(html_no_h1)[:length]


@python_2_unicode_compatible
class Post(models.Model):
    """Post"""

    def get_upload_name(self, filename):
        # created_time will be saved after the directly uploaded html file
        year = (self.created_time.year if self.created_time
                else datetime.now().year)
        return os.path.join('source', str(year), self.title+'.html')

    title = models.CharField(max_length=70, unique=True)
    body = models.TextField(blank=True)
    html_file = models.FileField(upload_to=get_upload_name, blank=True)
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
        if self.body and not self.html_file:
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
            ])
            html = md.convert(self.body)

            self.html_file.save(self.title + '.html',
                                ContentFile(html.encode('utf-8')), save=False)
            self.html_file.close()
        else:
            html = self.display()
        self.toc, self.excerpect = get_html_toc_excerpt(html)

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
