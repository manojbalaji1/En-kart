from django.conf.urls import url
from . import views
from .views import CategoryListView, CategoryDetailView
urlpatterns =[
    url(r'^/$', CategoryListView.as_view(), name='category_list'),
    url(r'^/(?P<slug>[\w]+)/$', CategoryDetailView.as_view(), name='category_detail'),
    # url('^product/(?P<id>\d+)$', views.product_detail_view_func,name='product_detail_function'),
]
