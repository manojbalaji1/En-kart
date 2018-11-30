# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Product, Payment, Customer, Cart, CartItem, Category, Brand, Order, OrderDetails, Variation, ProductImage, ProductFeature, LinoCredit
from django.contrib import admin

class CartItemInLine(admin.TabularInline):
    model = CartItem


class CartAdmin(admin.ModelAdmin):
    inlines = [
        CartItemInLine
    ]
    class Meta:
        model = Cart


# Register your models here.
admin.site.register(Product)
admin.site.register(Payment)
admin.site.register(Customer)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Order)
admin.site.register(OrderDetails)
admin.site.register(Variation)
admin.site.register(ProductImage)
admin.site.register(ProductFeature)
admin.site.register(LinoCredit)

