from django.conf.urls import url, include
from . import views
from .views import ProductDetailView, ProductListView, CartView, ItemCountView, CheckoutView, OrderView
from . import url_categories
from django.contrib.auth import views as auth_views
urlpatterns =[
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    # url(r'^signup/$', views.signup),
    url(r'^register/$', views.register_view, name='register'),
    url(r'^index/$', views.index, name='index'),
    url(r'^product/(?P<pk>\d+)$', ProductDetailView.as_view(), name='product_detail'),
    url(r'^product/$', ProductListView.as_view(), name='product_list'),
    url(r'^categories', include(url_categories)),
    url(r'^cart/$', CartView.as_view(), name="cart"),
url(r'^cart/count$', ItemCountView.as_view(), name="item_count"),
url(r'^checkout/$', CheckoutView.as_view(), name="checkout"),
url(r'^order/$', OrderView.as_view(), name="order"),
url(r'^payment_gateway/(?P<amount>[0-9]*\.[0-9]*)$', views.payment_gateway_view, name="payment_gateway"),
url(r'^lineocredit/$', views.lineo_credit, name='lieno_credit'),
    # url(r'^payment_gateway_redirect/$', views.payment_gateway_redirect, name="payment_gateway_redirect")
    # url('^product/(?P<id>\d+)$', views.product_detail_view_func,name='product_detail_function'),
]
