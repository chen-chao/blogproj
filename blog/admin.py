from django.contrib import admin
from django import forms
from django.forms import TextInput
from django.core.files.base import ContentFile
from .models import Post, PostImage
import os.path
import markdown
import docutils.core
import lxml.html


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 3


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        widgets = {
            'title': TextInput(attrs={'size': 40}),
        }
        exclude = ('toc', 'excerpect', 'created_time',
                   'modified_time', 'count_read', 'html_file')
    # original uploading file
    original_file = forms.FileField(required=False)


def _original_file_to_html(f):
    _, ext = os.path.splitext(f.name)
    ext = ext.lower()
    if ext in ('.md', '.markdown'):
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
        ])
        content = md.convert(f.read().decode('utf-8'))
        html = ContentFile(content.encode('utf-8'))
    elif ext in ('.html', '.htm'):
        html = f
    elif ext in ('.rst', '.rest', '.restructuredtext'):
        # from https://wiki.python.org/moin/reStructuredText
        content = docutils.core.publish_string(
            source=f.read().decode('utf-8'),
            writer_name='html'
        )
        content = content[
            content.find(b'<body>')+6:content.find(b'</body>')].strip()
        html = ContentFile(content)
    else:
        # unknown file extension, keep original
        html = f
    return html


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


class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    inlines = [PostImageInline,]
    list_display = ['title', 'author', 'created_time', 'modified_time', ]
    list_filter = ['created_time']
    search_fields = ['title', 'author']

    def save_model(self, request, obj, form, change):
        if obj and form.is_valid():
            toc = None
            excerpt = None
            if 'original_file' in form.changed_data:
                if obj.html_file:
                    obj.html_file.delete(save=False)
                f = request.FILES['original_file']
                html = _original_file_to_html(f)
                obj.html_file.save(obj.title+'.html', html, save=False)
                obj.html_file.close()
                html.seek(0)
                htmltree = lxml.html.fromstring(html.read().decode('utf-8'))
                toc = get_html_toc(htmltree)
                excerpt = get_html_excerpt(htmltree)
                f.close()

            obj.save(toc, excerpt)


admin.site.register(Post, PostAdmin)
