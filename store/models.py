from uuid import uuid4
from django.contrib import admin
from django.db import models
from django.core.validators import MinValueValidator,FileExtensionValidator
from django.conf import settings
from .validators import validate_file_size

class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()


class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey(#related_name='+' will stop from making the reverse relatinship hence no collection would be created in Product
        'Product', on_delete=models.SET_NULL, null=True, related_name='+')#here we are defining 'Product' because product module is present after collection
    
    def __str__(self) -> str:
        return self.title
    class Meta:
        ordering =['title']


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(null=True,blank=True)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2,validators=[MinValueValidator(1,message='Enter the Number Greater than 1')])# the message passed is optional other wise the python will give its own predefined message
    inventory = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT,related_name='products')
    promotions = models.ManyToManyField(Promotion,blank=True)

    def __str__(self) -> str:
        return self.title
    class Meta:
        ordering =['title']


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')#product fields
    image = models.ImageField(upload_to='store/images',validators=[validate_file_size])#image field, FileExtensionValidator(['jpg','jpeg','png','gif']) can also be used to validate the file extension


class Customer(models.Model):
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, 'Bronze'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_GOLD, 'Gold'),
    ]
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE)#choices will set the choice field
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)#it will point to setting and there we have given user in core app so it will there

    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name
    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name
    
    class Meta:
        ordering =['user__first_name','user__last_name']
        permissions=[
            ('view_history', 'Can view history'),#this is used to give addition permission allocation in  Group to the user
        ]

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'



class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed')
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    class Meta:
        permissions=[
            ('cancel_order','Can Cancel Order')
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT,related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT,related_name='orderitems')
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE)


class Cart(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])#defining the minimum value

#unique is used as there may be case of adding two or more products adding in the cart, so in that case we have to increase the quantity not the items therfore we use unique
    class Meta:
        unique_together = [['cart', 'product']]


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description=models.TextField()
    date = models.DateField(auto_now_add=True)