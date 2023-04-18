from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .forms import PostForm
from .models import Post, Group, User
from core.utils import get_paginator_obj


def index(request):
    post_list = Post.objects.select_related('author', 'group')
    page_obj = get_paginator_obj(request, post_list, 10)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    page_obj = get_paginator_obj(request, posts, 10)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user_posts = author.posts.all()
    page_obj = get_paginator_obj(request, user_posts, 10)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    user_post = get_object_or_404(Post, id=post_id)
    context = {
        'user_post': user_post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        create_post = form.save(commit=False)
        create_post.author = request.user
        form.save()

        return redirect('posts:profile', create_post.author)

    context = {
        'title': 'Новая запись',
        'form': form
    }

    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    select_post = get_object_or_404(Post, id=post_id)
    if request.user != select_post.author:
        return HttpResponseForbidden()

    form = PostForm(request.POST or None, instance=select_post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    context = {
        'title': 'Редактировать запись',
        'form': form,
        'is_edit': True,
    }

    return render(request, 'posts/create_post.html', context)
