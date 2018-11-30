# -*- coding: utf-8 -*-
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from . models import Product, Category, ProductFeature, Variation, CartItem, Cart, Order, LinoCredit
from .forms import UserResgisterForm
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404, Http404, redirect
from django.http import JsonResponse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin



# Create your views here.
# def signup(request):
#     form = CustomerForm( request.POST or None )
#     print(form.is_valid())
#     if form.is_valid():
#         print(form.cleaned_data['name'])
#         instance = form.save( commit=False )
#         form.save()
#         return HttpResponseRedirect( 'signup' )
#     context = {
#         "form": form,
#     }
#     return render( request, "signup.html", context )

def index(request):
    featured_image = ProductFeature.objects.first()
    products = Product.objects.all().order_by("?")[:6]
    products2 = Product.objects.all().order_by("?")[:6]
    context={
        "featured_image":featured_image,
        "products":products,
        "products2":products2,
    }
    return render(request,"index.html",context)

# def login_view(request):
#     form = UserLoginForm(request.POST or None)
#     if form.is_valid():
#         email = form.cleaned_data.get("email")
#         password = form.cleaned_data.get('password')
#         user = authenticate(email=email, password=password)
#
#         login(request, user)
#
#     return render(request, "login.html", {"form":form})

def register_view(request):
    title = "Register"
    if request.method == 'POST':
        form = UserResgisterForm( request.POST )
        if form.is_valid():
            user_data = form.save()
            user_data.refresh_from_db()  # load the profile instance created by the signal
            user_data.customer.full_name = form.cleaned_data.get( 'full_name' )
            user_data.customer.city = form.cleaned_data.get( 'city' )
            user_data.customer.pincode = form.cleaned_data.get( 'pincode' )
            user_data.customer.address1 = form.cleaned_data.get( 'address1' )
            user_data.customer.address2 = form.cleaned_data.get( 'address2' )
            user_data.customer.phone = form.cleaned_data.get( 'phone' )
            user_data.customer.country = form.cleaned_data.get( 'country' )
            user_data.save()
            raw_password = form.cleaned_data.get( 'password1' )
            user_data = authenticate( username=user_data.username, password=raw_password )
            login( request, user_data )
            return HttpResponseRedirect( reverse('index') )
    else:
        form = UserResgisterForm()
    context = {
        "form": form,
    }
    return render(request, "signup.html", context)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


class ItemCountView(View):

    def get(self,request, *args, **kwargs):
        if request.is_ajax():
            cart_id = self.request.session.get( "cart_id" )

            if cart_id == None :
                count = 0
            else:
                cart = Cart.objects.get(cart_id=cart_id)
                count = cart.items.count()
                request.session["count"]=count
            return JsonResponse({"count":count})
        else:
            raise Http404



# category views

class CategoryListView(ListView):
    model = Category
    queryset = Category.objects.all()
    template_name = "myshop/product_list.html"


class CategoryDetailView(DetailView):
    model = Category

    def get_context_data(self,*args, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(*args, **kwargs)
        obj = self.get_object()
        products = obj.product_set.all()
        default_product = obj.category_id_product.all()
        products = (products | default_product).distinct()
        context["products"] = products
        return context


# Product detailed view
import random
class ProductDetailView(DetailView):
    model = Product

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        instance = self.get_object()
        context["related"] = sorted(Product.objects.get_related(instance), key=lambda x: random.random(), reverse=True)
        return context


def product_detail_view_func(request,id):
    product_instance=Product.objects.get(product_id=id)
    print(product_instance.product_name)
    template="product_detail.html"
    context={
        "object": product_instance,
    }

    return render(request, template, context)

# Product List view


class ProductListView(ListView):
    model = Product
    template_name = "myshop/product_list.html"

    def get_context_data(self,*args, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        print (context)
        context["now"] = timezone.now()
        return context

    # for doing search through search bar content-wise

    def get_queryset(self, *args,**kwargs):
        qs = super(ProductListView, self).get_queryset(*args, **kwargs)
        query =  self.request.GET.get("q")
        if query:
            qs = self.model.objects.filter(
                Q(product_name__icontains=query) |
                Q(product_description__icontains= query)
                # Q(produc)
            )
            try:
                qs2=self.model.objects.filter(
                    Q(price=query)
                )
                qs = (qs | qs2).distinct()
            except:
                pass

        return qs

# cart view


class CartView(SingleObjectMixin, View):
    model = Cart
    template_name = "myshop/view.html"

    def get_object(self, *args, **kwargs):
        self.request.session.set_expiry( 0 )
        cart_id = self.request.session.get( "cart_id" )
        if cart_id is None:
            cart = Cart()
            cart.tax_percentage=0.085
            cart.save()
            cart_id = cart.cart_id
            self.request.session["cart_id"] = cart_id

        cart = Cart.objects.get( cart_id=cart_id )
        if self.request.user.is_authenticated():
            cart.user = self.request.user
            cart.save()
        return cart

    def get(self, request, *args, **kwargs):
        cart  = self.get_object()
        item_id = request.GET.get("item")
        delete_item =request.GET.get("delete", False)
        if item_id:
            item_instance = get_object_or_404(Variation, id=item_id)
            qty = request.GET.get("qty", 1)
            try:
                if int(qty) < 1:
                    delete_item=True
            except:
                raise Http404
            cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item_instance)
            item_added = False
            if created:
                item_added = True
            if delete_item:
                cart_item.delete()
            else:
                cart_item.quantity = qty
                cart_item.save()
            if not request.is_ajax():
                return HttpResponseRedirect(reverse("cart"))
        if request.is_ajax():
            try:
                total = cart_item.line_item_total
            except:
                total=None
            try:
                subtotal = cart_item.cart.subtotal
            except:
                subtotal = None
            try:
                taxtotal = cart_item.cart.taxtotal
            except:
                taxtotal = None
            try:
                total = cart_item.cart.total
            except:
                total = None
            data={
                "deleted": delete_item,
                "item_added": item_added,
                "line_total": total,
                "subtotal": subtotal,
                "taxtotal": taxtotal,
                "total": total,
            }
            return JsonResponse(data)
        context = {
            "object": self.get_object(),
        }
        template = self.template_name
        return render(request, template, context)


class CheckoutView(DetailView):
    model = Cart
    template_name = "myshop/checkout_view.html"

    def get_object(self, *args, **kwargs):
        cart_id = self.request.session.get( "cart_id" )
        if cart_id is None:
            return HttpResponseRedirect(reverse("cart"))
        cart = Cart.objects.get( cart_id=cart_id )
        return cart

    def get_context_data(self, *args, **kwargs):
        context = super(CheckoutView, self).get_context_data(*args, **kwargs)
        context["user_auth"] = True
        context["cart"] = self.get_object()
        if not self.request.user.is_authenticated:
            context["user_auth"]=False
            context["login_form"] = AuthenticationForm()
            context["next_url"] = self.request.build_absolute_uri()

        return context


class OrderView(ListView):
    model = Order
    template_name = "myshop/orders.html"

    def get_object(self, *args, **kwargs):
        user = self.request.user
        cart_id = self.request.session.get( "cart_id" )
        cart = Cart.objects.get( cart_id=cart_id )
        order = Order()
        if order.cart == cart_id:
            return [order]
        try:
            print (order.customer_id)
            order.customer_id = user.id
            order.due_amount = cart.total
            order.total_products = cart.cartitem_set.all().count()
            order.invoice_no = user.id
            order.cart = cart_id
            order.save()
        except:
            return [order]

        return [order]

    def get_context_data(self, *args, **kwargs):
        context = super(OrderView, self).get_context_data(*args, **kwargs)
        context["order"] = self.get_object()
        context["user_auth"] = True
        if not self.request.user.is_authenticated:
            context["user_auth"]=False
            context["login_form"] = AuthenticationForm()
            context["next_url"] = self.request.build_absolute_uri()

        return context


def payment_gateway_view(request, amount):
    template = "payment_gateway.html"
    amount = round(float(amount),2)
    interest = 0.02
    commission = round(interest * float(amount), 2)
    if commission < 10:
        commission = 10

    ecr = amount - commission
    context = {
        "amount": amount,
        "commission": commission,
        "ecr": ecr,

    }
    return render(request, template, context)


def order_history(request):
    context = {
            "order": queryset
            }
    return render(request, "myshop/order_history.html", context)

def lineo_credit(request):
    model = LinoCredit()
    queryset = LinoCredit.objects.all()
    context = {}
    if request.method == 'GET':
        for obj in queryset:
            balance = obj.credit - obj.used
            context = {
                "credit": obj.credit,
                "used": obj.used,
                "balance": balance
            }
            break
    else:
        model.save()
    return render(request, "user_profile.html", context)


def payment(request):
    return