from django.contrib import admin
from .models import *
from tags.models import *
from . import models

from django.db.models import Count#this is used to find the count of some..
from django.utils.html import format_html,urlencode #for writting some html code like giving link we have to give html code
from django.urls import reverse #for setting up the urls
from django.contrib.contenttypes.admin import GenericTabularInline
# Register your models here.



class ProductImageInline(admin.TabularInline):
    model=models.ProductImage
    readonly_fields=['thumbnail']

    def thumbnail(self,instance):
        if instance.image.name != '':
            return format_html (f'<img src="{instance.image.url}" class="thumbnail" />')
        return ''



@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):

    autocomplete_fields=['collection']#we can search the collection
    prepopulated_fields={ # it will automatically populate the slug while giving the title
        'slug':['title']
    }
    actions=['clear_inventory']#new actions if want to add any
    # inlines=[TagInline]
    inlines=[ProductImageInline]#this is used to show the images in the admin page
    search_fields=['title']#search field that , how can we found the user
    list_display = ('title','unit_price','inventory','inventory_status','collection_title')# this are the lists that are going to be displayed
    list_editable=['unit_price']#This will make editable while showing during the admin page, we not need to go inside
    list_per_page=10#how much data will be shown in the page

#format of addning new column, its for the column of inventory_status
    @admin.display(ordering='inventory')
    def inventory_status(self , product):
        if product.inventory < 10:
            return 'LOW'
        return 'OK'
    
    list_select_related=['collection']#this is used to load the data before executing which will reduce the queries and efficiency of the loading
    #hence we need to grab the collection__title from the collection model so we are preloading, collection model so that it doesnot take time while loading the data , we donot provide the colleciton than the loading time would be taken

    def collection_title(self,product):# joining the two tables and displaying the particular table
        return product.collection.title


    @admin.action(description='Clear Inventory')
    def clear_inventory(self,request,queryset):
        updated_count= queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} products were sussessfully Cleared & Upadated ')
        
    class Media:
        css={
            'all':['store/style.css']
        }





@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name','last_name','membership','customer_orders')
    list_editable=['membership']
    list_per_page=25
    list_select_related=['user']
    ordering=['user__first_name','user__last_name']
    search_fields=['first_name__istartswith','last_name__istartswith']#starts with is used to give the result that starts with the serach letter, i is used for making insesitive

    @admin.display(ordering='customer_orders')
    def customer_orders(self,customer):
        #adding link so that if clicked on the orders all the orders list would be displayed
        url=(reverse('admin:store_order_changelist') + '?' + urlencode({'customer_id':str(customer.id)})) #store is the app name, order indicates that we are going to see the order, changelist is used to open the page that will open 
        return format_html('<a href="{}">{}<a/>',url,customer.customer_orders)


    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            customer_orders=Count('order')
        )
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# this model would display the result in tabular form
class OrderItemInline(admin.TabularInline):
    autocomplete_fields=['product']
    model=models.OrderItem
    extra=0


@admin.register(models.Order)
class OrdersAdmin(admin.ModelAdmin):
    autocomplete_fields=['customer']
    inlines=[OrderItemInline]#to show the result in tabular form
    list_display = ('customer_name', 'id', 'placed_at', 'payment_status', 'customer_membership')
    list_per_page=25
    list_select_related=['customer']

    @admin.display(ordering='customer__first_name')
    def customer_name(self, order):
        return f"{order.customer.first_name} {order.customer.last_name}"

    @admin.display(ordering='customer__membership')
    def customer_membership(self, order):
        return order.customer.membership
    customer_name.short_description = 'Customer Name'





@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display=['title','products_count']
    search_fields=['title']#this is written that we can search from any other area

    @admin.display(ordering='products_count')
    def products_count(self,collection):
        url=(reverse('admin:store_product_changelist') + '?' + urlencode({'collection_id':str(collection.id)})) # admin:app_model_page we have to follow this all steps
        return format_html('<a href="{}">{}<a/>',url,collection.products_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('products')
        )



# my mistake

# @admin.register(models.Order)
# class OrdersAdmin(admin.ModelAdmin):
#     list_display = ('customer_name','id','placed_at','payment_status','customer_membership')
#     list_select_related=['collection']
#     def customer_name(self,Order):
#         return Order.customer.first_name#('first_name','last_name')
    
#     def customer_membership(self,Order):
#         return Order.customer.membership

