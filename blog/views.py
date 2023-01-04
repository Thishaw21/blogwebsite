from django.core import paginator
from datetime import date
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.utils.text import slugify
from django.http import HttpResponse
from user_profile.models import User
from django.contrib.auth.decorators import user_passes_test

from .models import (
    Blog,
    Category,
    Reply,
    Tag,
    Comment,
    Summary
)
from .forms import TextForm, AddBlogForm
from .algorithms.frequency import extraction, kmeans

def home(request):
    blogs = Blog.objects.order_by('-id')
    tags = Tag.objects.order_by('-created_date')
    context = {
        "blogs": blogs,
        "tags": tags
    }
    return render(request, 'home.html', context)

def blogs(request):
    queryset = Blog.objects.order_by('-created_date')
    tags = Tag.objects.order_by('-created_date')
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 4)
    
    try:
        blogs = paginator.page(page)
    except EmptyPage:
        blogs = paginator.page(1)
    except PageNotAnInteger:
        blogs = paginator.page(1)
        return redirect('blogs')
    
    context = {
        "blogs": blogs,
        "tags": tags,
        "paginator": paginator
    }
    return render(request, 'blogs.html', context)


def category_blogs(request, slug):
    category = get_object_or_404(Category, slug=slug)
    queryset = category.category_blogs.all()
    tags = Tag.objects.order_by('-created_date')[:5]
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 2)
    all_blogs = Blog.objects.order_by('-created_date')[:5]
    
    try:
        blogs = paginator.page(page)
    except EmptyPage:
        blogs = paginator.page(1)
    except PageNotAnInteger:
        blogs = paginator.page(1)
        return redirect('blogs')

    context = {
        "blogs": blogs,
        "tags": tags,
        "all_blogs": all_blogs
    }
    return render(request, 'category_blogs.html', context)


def tag_blogs(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    queryset = tag.tag_blogs.all()
    tags = Tag.objects.order_by('-created_date')[:5]
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 2)
    all_blogs = Blog.objects.order_by('-created_date')[:5]
    
    try:
        blogs = paginator.page(page)
    except EmptyPage:
        blogs = paginator.page(1)
    except PageNotAnInteger:
        blogs = paginator.page(1)
        return redirect('blogs')

    context = {
        "blogs": blogs,
        "tags": tags,
        "all_blogs": all_blogs
    }
    return render(request, 'category_blogs.html', context)


def blog_details(request, slug):
    form = TextForm()
    blog = get_object_or_404(Blog, slug=slug)
    category = Category.objects.get(id=blog.category.id)
    related_blogs = category.category_blogs.all()
    tags = Tag.objects.order_by('-created_date')[:5]
    liked_by = request.user in blog.likes.all()

    if request.method == "POST" and request.user.is_authenticated:
        form = TextForm(request.POST)
        if form.is_valid():
            Comment.objects.create(
                user=request.user,
                blog=blog,
                text=form.cleaned_data.get('text')
            )
            return redirect('blog_details', slug=slug)

    context = {
        "blog": blog,
        "related_blogs": related_blogs,
        "tags": tags,
        "form": form,
        "liked_by": liked_by
    }
    return render(request, 'blog_details.html', context)


@login_required(login_url='login')
def add_reply(request, blog_id, comment_id):
    blog = get_object_or_404(Blog, id=blog_id)
    if request.method == "POST":
        form = TextForm(request.POST)
        if form.is_valid():
            comment = get_object_or_404(Comment, id=comment_id)
            Reply.objects.create(
                user=request.user,
                comment=comment,
                text=form.cleaned_data.get('text')
            )
    return redirect('blog_details', slug=blog.slug)


@login_required(login_url='login')
def like_blog(request, pk):
    context = {}
    blog = get_object_or_404(Blog, pk=pk)
    
    if request.user in blog.likes.all():
        blog.likes.remove(request.user)
        context['liked'] = False
        context['like_count'] = blog.likes.all().count()
        
    else:
        blog.likes.add(request.user)
        context['liked'] = True
        context['like_count'] = blog.likes.all().count()

    return JsonResponse(context, safe=False)


def search_blogs(request):
    search_key = request.GET.get('search', None)
    recent_blogs = Blog.objects.order_by('-created_date')
    tags = Tag.objects.order_by('-created_date')
    
    if search_key:
        blogs = Blog.objects.filter(
            Q(title__icontains=search_key) |
            Q(category__title__icontains=search_key) |
            Q(user__username__icontains=search_key) |
            Q(tags__title__icontains=search_key)
        ).distinct()

        context = {
            "blogs": blogs,
            "recent_blogs": recent_blogs,
            "tags": tags,
            "search_key": search_key
        }

        return render(request, 'search.html', context)

    else:
        return redirect('home')

def check_view_blog(user):
    return user.has_perm('blog.view_blog')

@user_passes_test(check_view_blog)
@login_required(login_url='login')
def my_blogs(request):
    queryset = request.user.user_blogs.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, 6)
    delete = request.GET.get('delete', None)

    if delete:
        blog = get_object_or_404(Blog, pk=delete)
        
        if request.user.pk != blog.user.pk:
            return redirect('home')

        blog.delete()
        messages.success(request, "Your blog has been deleted!")
        return redirect('my_blogs')

    try:
        blogs = paginator.page(page)
    except EmptyPage:
        blogs = paginator.page(1)
    except PageNotAnInteger:
        blogs = paginator.page(1)
        return redirect('blogs')

    context = {
        "blogs": blogs,
        "paginator": paginator
    }
    
    return render(request, 'my_blogs.html', context)
    
def check_add_blog(user):
    return user.has_perm('blog.add_blog')

@user_passes_test(check_add_blog)
@login_required(login_url='login')
def add_blog(request):
    form = AddBlogForm()
    summary = Summary.objects.filter(user=request.user).order_by('-id')
    if request.method == "POST":
        form = AddBlogForm(request.POST, request.FILES)
        if form.is_valid():
            tags = request.POST['tags'].split(',')
            user = get_object_or_404(User, pk=request.user.pk)
            category = get_object_or_404(Category, pk=request.POST['category'])
            summary = get_object_or_404(Summary, pk=request.POST['summary'])
            blog = form.save(commit=False)
            blog.user = user
            blog.category = category
            blog.summary = summary
            blog.save()

            for tag in tags:
                tag_input = Tag.objects.filter(
                    title__iexact=tag.strip(),
                    slug=slugify(tag.strip())
                )
                if tag_input.exists():
                    t = tag_input.first()
                    blog.tags.add(t)

                else:
                    if tag != '':
                        new_tag = Tag.objects.create(
                            title=tag.strip(),
                            slug=slugify(tag.strip())
                        )
                        blog.tags.add(new_tag)

            messages.success(request, "Blog added successfully")
            return redirect('blog_details', slug=blog.slug)
        else:
            print(form.errors)

    context = {
        "form": form,
        'summaries': summary
    }
    return render(request, 'add_blog.html', context)


def check_update_blog(user):
    return user.has_perm('blog.change_blog')
@login_required(login_url='login')
@user_passes_test(check_update_blog)
def update_blog(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    form = AddBlogForm(instance=blog)
    summary = Summary.objects.filter(user=request.user).order_by('-id')

    if request.method == "POST":
        form = AddBlogForm(request.POST, request.FILES, instance=blog)
        
        if form.is_valid():
            
            if request.user.pk != blog.user.pk:
                return redirect('home')

            tags = request.POST['tags'].split(',')
            user = get_object_or_404(User, pk=request.user.pk)
            category = get_object_or_404(Category, pk=request.POST['category'])
            summary = get_object_or_404(Summary, pk=request.POST['summary'])
            blog = form.save(commit=False)
            blog.user = user
            blog.category = category
            blog.summary = summary
            blog.save()

            for tag in tags:
                tag_input = Tag.objects.filter(
                    title__iexact=tag.strip(),
                    slug=slugify(tag.strip())
                )
                if tag_input.exists():
                    t = tag_input.first()
                    blog.tags.add(t)

                else:
                    if tag != '':
                        new_tag = Tag.objects.create(
                            title=tag.strip(),
                            slug=slugify(tag.strip())
                        )
                        blog.tags.add(new_tag)

            messages.success(request, "Blog updated successfully")
            return redirect('blog_details', slug=blog.slug)
        else:
            print(form.errors)


    context = {
        "form": form,
        "blog": blog,
        "summaries": summary
    }
    return render(request, 'update_blog.html', context)

def index_summarize(request):
    return render(request, 'index_summarizer.html')


def summarize_page(request):
    long_text = request.GET.get('long-text')
    sentence_no = int(request.GET.get('number'))
    result_list = []

    original_text = long_text
    result_list = kmeans.summarize(long_text, sentence_no)

    summary = ' '.join(result_list)

    context = {'data': summary, 'original_text': original_text}
    return render(request, "index_summarizer.html", context)


@login_required
def save_summary(request):
    summary = request.POST.get('summary')
    topic = request.POST.get('topic')
    if len(topic) < 50:
        heading = topic
    else:
        heading = topic[:50] + '...'

    summaryTb = Summary(user=request.user, body=summary, original_link=heading, date_created=date.today())
    summaryTb.save()
    context = {'message': 'success'}
    return render(request, "index_summarizer.html", context)

@login_required
def history(request):
    summary = Summary.objects.filter(user=request.user).order_by('-id')
    context = {'data': summary}
    return render(request, "history.html", context)


def history_topic(request):
    if request.method == 'GET':
        topic = request.GET.get('topic')
        summary = request.GET.get('body')
        context = {'topic': topic, 'body': summary}
        return render(request, "history_topic.html", context)

# def summary_post(request, blog_id):
#     blog = Blog.objects.get(id = blog_id)
#     return HttpResponse(blog.summary.body)

def summary_post(request, slug):
    blog = Blog.objects.get(slug = slug)
    context = {'blog': blog}
    return render(request, 'summary_post.html', context)
    # return HttpResponse(blog.summary.body)
