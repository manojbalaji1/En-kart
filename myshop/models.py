# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.conf import settings

# Create your models here.


class Customer(models.Model):
    customer_id = models.OneToOneField( User, primary_key=True, on_delete=models.CASCADE )
    full_name = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    pincode = models.IntegerField(max_length=6, null=True)
    address1 = models.CharField(max_length=100)
    address2 = models.CharField( max_length=100, null=True)
    phone = models.CharField(max_length=10)
    country = models.CharField(max_length=20)

    def __unicode__(self):
        return self.customer_id.username

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(customer_id=instance)
    instance.customer.save()
# checkview

# Order Model


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    customer_id = models.IntegerField
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=20, default="pending")
    due_amount = models.DecimalField( max_digits=50, decimal_places=2, default=0 )
    invoice_no = models.IntegerField(null=False, unique=True)
    total_products = models.IntegerField(max_length=5)
    cart = models.IntegerField(max_length=7, null=True)

    def __unicode__(self):
        return "%s" %self.order_id


#Payment Model


class Payment(models.Model):
    order_id = models.ForeignKey(Order, to_field='order_id',related_name='order_id_payment')
    payment_id = models.AutoField(primary_key=True)
    # invoice_no = models.ForeignKey(Order, to_field='invoice_no', related_name='invoice_no_payment')
    payment_type = models.CharField(max_length=20)
    ref_no = models.IntegerField(unique=True)


# Category Model


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=20)
    slug = models.SlugField(unique=True, null=True)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)

    def __unicode__(self):
        return self.category_name


    def get_absolute_url(self):
        return reverse("category_detail",kwargs={"slug": self.slug})

# Brand Model


class Brand(models.Model):
    brand_id = models.AutoField(primary_key=True)
    brand_name = models.CharField(max_length=100)
    def __unicode__(self):
        return self.brand_name


# ProductModel
class ProductQuerySet(models.query.QuerySet):
    def product_status(self):
        return self.filter(product_status=True)

class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self, *args, **kwargs):
        return self.get_queryset().product_status()

    def get_related(self, instance):
        products_one = self.get_queryset().filter(category__in=instance.category.all())
        products_two = self.get_queryset().filter(category_id=instance.category_id)
        qs = ( products_one | products_two).exclude(product_id=instance.product_id).distinct()
        return qs


class Product(models.Model):
    product_id = models.AutoField( primary_key=True )
    product_name = models.CharField(max_length=100)
    unit_price = models.DecimalField(decimal_places=2 ,max_digits=20)
    product_description = models.CharField(max_length=200)
    product_status = models.BooleanField(default=True)
    category_id = models.ForeignKey(Category, to_field='category_id', related_name='category_id_product')
    category =models.ManyToManyField(Category)
    brand_id = models.ForeignKey(Brand, to_field='brand_id', related_name='brand_id_product')

    objects = ProductManager()

    class Meta:
        ordering = ["-product_name"]

    def __unicode__(self):
        return self.product_name

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"pk":self.pk})

    def get_image_url(self):
        img= self.productimage_set.first()
        if img:
            return img.image.url
        else:
            return img # None


class Variation(models.Model):
    product = models.ForeignKey(Product)
    variation_name = models.CharField(max_length=100)
    unit_price = models.DecimalField(decimal_places=2 ,max_digits=20)
    sale_price = models.DecimalField( decimal_places=2, max_digits=20, null=True, blank=True )
    product_status = models.BooleanField( default=True )

    def __unicode__(self):
        return self.variation_name

    def get_price(self):
        if self.sale_price is not None:
            return self.sale_price
        else:
            return self.unit_price

    def get_html_price(self):
        if self.sale_price is not None:
            html_text="<span class='sale-price'>%s</span> <span class='og-price' style='color: red; text-decoration:line-through;'>%s</span>" %(self.sale_price, self.unit_price)

            return mark_safe(html_text)
        else:
            html_text = "<span class='sale-price'>%s</span>" % self.unit_price

            return mark_safe(html_text)

    def get_absolute_url(self):
        return self.product.get_absolute_url()

    def add_to_cart(self):
        return "%s?item=%s&qty=1" %(reverse("cart"), self.id)

    def remove_from_cart(self):
        return "%s?item=%s&qty=1&delete=True" %(reverse("cart"), self.id)

    def get_title(self):
        return "%s - %s" %(self.product.product_name, self.variation_name)

# makes sure product has variations everytime it is created or saved


def product_post_saved_receiver(sender, instance, created, *args, **kwargs):
    product = instance
    variations = product.variation_set.all()
    if variations.count() == 0:
        new_var = Variation()
        new_var.product= product
        new_var.variation_name= "Default"
        new_var.unit_price=product.unit_price
        new_var.save()

post_save.connect(product_post_saved_receiver, sender=Product)

# Product image handle


class ProductImage(models.Model):
    product = models.ForeignKey(Product)
    image = models.ImageField(upload_to='myshop/product/images')

    def __unicode__(self):
        return self.product.product_name

# OrderDetail Model


class OrderDetails(models.Model):
    order_id = models.ForeignKey(Order, to_field='order_id', primary_key=True,related_name='order_id_order_details')
    product_id = models.ForeignKey(Product, to_field='product_id', related_name='product_id_order_details')
    quantity = models.IntegerField
    # order_status = models.ForeignKey(Order, to_field='order_status', related_name='order_status_order_details')
    # invoice_no = models.ForeignKey(Order, to_field='invoice_no', related_name='invoice_no_order_details')


# Cart Model
class CartItem(models.Model):
    cart = models.ForeignKey("Cart")
    item = models.ForeignKey(Variation)
    quantity = models.PositiveIntegerField(default=1)
    line_item_total = models.DecimalField( max_digits=10, decimal_places=2, null=True)

    def __unicode__(self):
        return self.item.variation_name

    def remove(self):
        return self.item.remove_from_cart()


def cart_item_pre_save_receiver(sender, instance, *args, **kwargs):
    qty = instance.quantity
    if int(qty) > 1:
        price = instance.item.get_price()
        line_item_total = Decimal(qty) * Decimal(price)
        instance.line_item_total = line_item_total


pre_save.connect(cart_item_pre_save_receiver, sender=CartItem)


def cart_item_post_save_receiver(sender, instance, *args, **kwargs):
    instance.cart.update_subtotal()

post_save.connect(cart_item_post_save_receiver, sender=CartItem)
post_delete.connect(cart_item_post_save_receiver, sender=CartItem)


class Cart(models.Model):
    cart_id=models.AutoField(primary_key=True)
    user = models.ForeignKey( settings.AUTH_USER_MODEL, null=True, blank=True )
    items = models.ManyToManyField( Variation, through=CartItem )
    timestamp = models.DateTimeField( auto_now_add=True, auto_now=False )
    updated = models.DateTimeField( auto_now_add=False, auto_now=True )
    subtotal = models.DecimalField( max_digits=50, decimal_places=2, default=0 )
    tax_percentage = models.DecimalField( max_digits=50, decimal_places=2, default=0.085 )
    taxtotal = models.DecimalField( max_digits=50, decimal_places=2, default=0 )
    total = models.DecimalField( max_digits=50, decimal_places=2, default=0 )

    # ip_addr = models.CharField(max_length=15, primary_key=True)
    # quantity = models.IntegerField
    #
    # amount = models.FloatField
    def __unicode__(self):
        return str( self.cart_id )

    def update_subtotal(self):
        subtotal=0
        items = self.cartitem_set.all()
        for item in items:
            if item.line_item_total is not None:
                subtotal += item.line_item_total
        self.subtotal = subtotal
        self.save()

def do_tax_and_total_receiver(sender, instance, *args, **kwargs):
    subtotal = instance.subtotal
    tax_total = round(subtotal * instance.tax_percentage, 2)
    total =round(subtotal + Decimal(tax_total) ,2)
    instance.taxtotal = "%.2f" %tax_total
    instance.total=total


pre_save.connect(do_tax_and_total_receiver, sender=Cart )

# product feature


class ProductFeature(models.Model):
    product=models.ForeignKey(Product)
    image = models.ImageField(upload_to="myshop/product/featured")
    title = models.CharField(max_length=120, null=True, blank=True)
    text = models.CharField(max_length=220, null=True, blank=True)
    text_right = models.BooleanField(default=False)
    show_price = models.BooleanField(default=False)
    make_image_background = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.product.product_name


class LinoCredit(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    credit = models.FloatField(max_length=20)
    used = models.FloatField(max_length=20)