from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
# Create your views here.


from taggit.models import TaggedItem
from taggit.models import Tag
from django.views.generic.base import TemplateView
from django.views import generic
from . import models
# class DetailView(TemplateView):

#     # def get(self, request, pk, *args, **kwargs):
#     #     return HttpResponse(f'Hello, World!{pk}')
#     template_name = "detail.html"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['latest_articles'] = Article.objects.all()[:5]
#         return context


class DetailView(generic.DetailView):
    template_name = 'post/detail.html'
    # context_object_name = 'post'
    # def get(request, pk):
    #     """Return the last five published questions."""
    #     return Post.objects.get(id=pk)
    model = models.Post
    context_object_name = 'detail'
    ordering = ['-created_on']
    # # 控制访问权限
    # @method_decorator(login_required)
    # @method_decorator(permission_required('dashboard.view_server'))
    # def get(self, request, *args, **kwargs):
    #     print("kwargs", kwargs)
    #     # context = self.model.objects.get(id=pk)
    #     context = super().get_context_data(**kwargs)
    #     # context['now'] = timezone.now()
    #     return context

    def get_context_data(self, *args, **kwargs):
        # print("kwargs",kwargs)
        # context = Post.objects.get(id=pk)
        context = super().get_context_data(**kwargs)

        # context['now'] = timezone.now()
        # context['title'] = "Post Details"
        # print(context)
        return context


class IndexView(generic.ListView):

    # def get(self, request, *args, **kwargs):
    #     return HttpResponse('Hello, World! index')

    template_name = 'post/blog_index.html'
    model = models.Post
    paginate_by = 10
    ordering = ['-created_on']


    # context_object_name = 'model_list'
    # def get(self, request, *args, **kwargs):
    #     return HttpResponse('Hello, World! index')
    #     # return {}
    def get_context_data(self, *args, **kwargs):
        # print("kwargs",kwargs)
        # context = Post.objects.get(id=pk)
        context = super().get_context_data(**kwargs)
        # context['now'] = timezone.now()
        # context['title'] = "Post Details"
        # print(context)
        return context


class TagListView(generic.ListView):
    model = models.Post
    template_name = 'post/article_list_by_tag.html'
    context_object_name = 'posts'
    paginate_by = 10
    ordering = ['-created_on']
    def get_queryset(self):
        # retrieve the tag from the URL
        tag_slug = self.kwargs['pk']
        # get the tag object based on the slug
        tag = Tag.objects.get(pk=tag_slug)
        # filter articles based on the tag
        articles = self.model.objects.filter(tags=tag)

        return articles

    def get_context_data(self, *args, **kwargs):
        """

        """
        context = super().get_context_data(**kwargs)
        # 获取tag的标签
        tag_slug = self.kwargs['pk']
        tag = Tag.objects.get(pk=tag_slug)
        context['title'] = tag
        return context