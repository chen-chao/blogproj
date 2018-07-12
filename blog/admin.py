from django.contrib import admin
from django import forms
from django.forms import TextInput
from django.core.files.base import ContentFile
from .models import Post, PostImage
from comments.models import Comment
import os.path
import markdown
import docutils.core


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 3


class CommentInline(admin.StackedInline):
    model = Comment
    extra = 1
    exclude = ('url',)


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


class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    inlines = [PostImageInline, CommentInline]
    list_display = ['title', 'author', 'created_time', 'modified_time', ]
    list_filter = ['created_time']
    search_fields = ['title', 'author']

    def save_model(self, request, obj, form, change):
        if obj and form.is_valid():
            if change and any(map(lambda x: x in form.changed_data,
                                  ('title', 'original_file'))):
                obj.html_file.delete(save=False)

            if 'original_file' in form.changed_data:
                f = request.FILES['original_file']
                html = _original_file_to_html(f)
                obj.html_file.save(obj.title+'.html', html, save=False)
                obj.html_file.close()
                f.close()

            obj.save()


admin.site.register(Post, PostAdmin)
