from django.contrib import admin
from django import forms
from django.forms import TextInput, Textarea
from django.core.files.base import ContentFile
from .models import Post, PostImage
# Register your models here.


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 3


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        widgets = {
            'body': Textarea(attrs={'rows': 30, 'cols': 100}),
            'title': TextInput(attrs={'size': 40}),
        }
        exclude = ('toc', 'excerpect', 'created_time',
                   'modified_time', 'count_read')


class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    inlines = [PostImageInline]
    list_display = ['title', 'author', 'created_time', 'modified_time', ]
    list_filter = ['created_time']
    search_fields = ['title', 'author']

    def save_model(self, request, obj, form, change):
        if obj:
            if change and any(map(lambda x: x in form.changed_data,
                                  ('title', 'body', 'html_file'))):
                obj.html_file.delete()

            if 'html_file' in form.changed_data:
                html_file = request.FILES['html_file']
                with html_file.open() as f:
                    obj.html_file.save(obj.title+'.html', ContentFile(
                        f.read()), save=False)
                    obj.html_file.close()

            obj.save()


admin.site.register(Post, PostAdmin)
