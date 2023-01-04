from django.urls import path

from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('blogs/', blogs, name='blogs'),
    path('category_blogs/<str:slug>/', category_blogs, name='category_blogs'),
    # path('summary_post/<int:blog_id>', summary_post, name='summary_post'),
    path('summary_post/<str:slug>', summary_post, name='summary_post'),
    path('tag_blogs/<str:slug>/', tag_blogs, name='tag_blogs'),
    path('blog/<str:slug>/', blog_details, name='blog_details'),
    path('add_reply/<int:blog_id>/<int:comment_id>/', add_reply, name='add_reply'),
    path('like_blog/<int>/', like_blog, name='like_blog'),
    path('search_blogs/', search_blogs, name='search_blogs'),
    path('my_blogs/', my_blogs, name='my_blogs'),
    path('add_blog/', add_blog, name='add_blog'),
    path('update_blog/<str:slug>/', update_blog, name='update_blog'),
    path('summarizer/', index_summarize,name='index_summarize'),
    path('summarize_page/',summarize_page,name='summarize_page'),
    path('save_summary/', save_summary, name='save_summary'),
    path('history/', history, name='history'),
    path('history/history_topic/', history_topic, name='history_topic'),
]