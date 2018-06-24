# coding: utf-8
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from taggit.models import Tag


from .models import Post, PostImage
from comments.forms import CommentForm
import os.path

global PAGE_NUM
PAGE_NUM = 10


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = PAGE_NUM

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')
        pagination_data = self.pagination_data(paginator, page, is_paginated)

        context.update(pagination_data)

        return context

    def pagination_data(self, paginator, page, is_paginated, radius=2):
        if not is_paginated:
            return {}

        current_page = page.number
        max_page = paginator.num_pages

        leftmost = max(current_page - radius, 1)
        left_has_more = True if leftmost > 1 else False

        rightmost = min(current_page + radius, max_page)
        right_has_more = True if rightmost < max_page else False

        data = {
            'left': range(leftmost, current_page),
            'right': range(current_page+1, rightmost),
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
        }

        return data


def ImageView(request, imagename, pk=None):
    imagename = 'images/' + imagename
    if pk:
        imageobj = Post.objects.get(pk=pk).images.get(image=imagename)
    else:
        imageobj = PostImage.objects.get(image=imagename)
    if imageobj:
        _, ext = os.path.splitext(os.path.basename(imageobj.image.path))
        image_type = 'image/' + ext
        with open(imageobj.image.path, 'rb') as im:
            return HttpResponse(im.read(), content_type=image_type)
    raise Http404('can not find %s' % imagename)


class ArchiveView(IndexView):

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchiveView, self).get_queryset().filter(
            created_time__year=year,
            created_time__month=month)


class TagView(IndexView):

    def get_queryset(self):
        # tags = list(self.kwargs.get('tag'))
        # return super(TagView, self).get_queryset().filter(
        #     tags__name__in=tags)
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=tag)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        response = super(PostDetailView, self).get(request, *args, **kwargs)
        self.object.increase_views()

        return response

    def get_context_data(self, **kwargs):

        context = super(PostDetailView, self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all()
        context.update({
            'form': form,
            'comment_list': comment_list
        })
        return context


def search(request):
    q = request.GET.get('q')
    error_msg = ''

    if not q:
        error_msg = "请输入关键词"
        return render(request, 'blog/index.html', {'error_msg': error_msg})

    post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))

    return render(request, 'blog/index.html', {'error_msg': error_msg,
                                               'post_list': post_list})


class BlogView(ListView):
    model = Post
    template_name = 'blog/blog.html'
    context_object_name = 'post_list'
    paginate_by = PAGE_NUM


class AboutView(ListView):
    model = Post
    template_name = 'blog/about.html'
    context_object_name = 'post_list'
    # paginate_by = PAGE_NUM


class ContactView(ListView):
    model = Post
    template_name = 'blog/contact.html'
    context_object_name = 'post_list'
    # paginate_by = PAGE_NUM
