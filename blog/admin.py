from django.contrib import admin
from django import forms
from django.forms import TextInput, Textarea
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
        exclude = ('html_file', 'created_time', 'modified_time')


class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    inlines = [PostImageInline]
    list_display = ['title', 'author', 'created_time', 'modified_time', ]
    list_filter = ['created_time']
    search_fields = ['title', 'author']

    def save_model(self, request, obj, form, change):
        # TODO: update same name images
        if obj:
            if any(map(lambda x: x in form.changed_data,
                       ('title', 'body'))):
                obj.html_file.delete()
            obj.save()


admin.site.register(Post, PostAdmin)
