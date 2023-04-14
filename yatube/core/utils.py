from django.core.paginator import Paginator


def get_paginator_obj(request, posts, COUNT_POSTS):
    paginator = Paginator(posts, COUNT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
