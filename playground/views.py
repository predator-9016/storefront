from django.shortcuts import render
from django.http import HttpResponse
from store.models import Product,OrderItem,Order,Customer
from django.db.models import Q,F,Value,Func
from django.db.models.aggregates import *

from django.db.models.functions import Concat



def say_hello(request):
    # queryset=Product.objects.filter(Q(inventory__lt=10)| ~Q(unit_price__lt=20))
    # queryset=Product.objects.filter(inventory=F('unit_price'))
    #F is used to reference the data  we cannot directly do that so we use to use refference variable
    queryset=Product.objects.filter(id__in=OrderItem.objects.values('product_id').distinct()).order_by('title')[5:20]
    return render(request, 'hello.html', {'name': 'Krishna','products':list(queryset)})

# queryset = Product.objects.filter(unit_price__gt=20)
# gt =greater
# gte=greater than equal
# lt=less than
# lte= less than equal

# queryset = Product.objects.filter(unit_price__range=(20,30))
# queryset = Product.objects.filter(title__icontains='coffee')
# queryset = Product.objects.filter(title__contains='coffee')#case sensitive
# queryset = Product.objects.filter(collection__id__range=(1,2,3))
# queryset = Product.objects.filter(last_update__year=2021)date time etc....
# queryset = Product.objects.filter(description__isnull=True)
# queryset = Product.objects.filter(inventory__lt=10,unit_price__lt=20)
#another method to write the same query
# queryset = Product.objects.filter(inventory__lt=10).filter(unit_price__lt=10)


#sorting the data 
# queryset=Product.objects.order_by('unit_price',-title').reverse()
#reverse is used to reverse the complete result of what we would be getting in the query set
# using - in front of the title to descendig order

# queryset=Product.objects.filter(collection__id=1).orderby('unit_price')
# queryset=Product.objects.orderby('unit_price')[0]
#accessing the first element in this we are not returning any query set 
# queryset=Product.objects.earliest('unit_price') it will return the earliest result obtained while implementing this we have to change it from list to simple sinle line output in return
#earliest returns in ascending order
#latest returns in the descending order

# queryset=Product.objects.all()[0:5]# to limits the result by 5 
# queryset=Product.objects.values_list('id','title',collection__id)

#query to select products that have been ordered and sort them by title

# queryset=Product.objects.filter(id__in=OrderItem.objects.values('product_id').distinct()).order_by('title')





# queryset =Product.objects.select_related('collection').all()
#this is used when we have to preload the data item that is going to be used
# so when calling it doesnot waste time while ladinig instead it makes it faster and easier
#select_related is used when there is one to one relation
# if there is many realtion we use prefetch_related for exmaple promotions in product table

# we can call both this method by simply joining
# queryset =Product.objects.select_related('collection').select_related('collection').all()


# get the last 5 orders with their customers and items (incl products)
# queryset=Order.objects.selct_related('customer').prefetch_related('orderitem_set__product').orderby('-placed_at')[0:5]




# aggrigation
def say_bye(request):
    result =Product.objects.filter(collection__id=1).aggregate(count=Count('id'),min_price=Min('unit_price'))
    return render(request,'hello.html',{'name':'Krishna','result':'result'})

# to add a new column or fucntion in the table we use annotate fuction

# queryset =Customer.objects.annotate(is_new=Value(True))

# concat function
# full_name=Customer.objects.annotate(full_name=Concat('first_name',value(' '),'last_name'))
def concating(request):
    full_name=Customer.objects.annotate(full_name=Concat('first_name',Value(' '),'last_name'))
    # full_name2=Customer.objects.annotate(full_name=Func(F('first_name'),Value(' '),F('last_name'),function'CONCAT'))
    return render(request,'hello.html',{'name':'Krishna','result':'full_name'})






# order_by arranging
def grouping(request):
    queryset=Customer.objects.annotate(orders_count=Count('order'))
    return render(request,'hello.html',{'name':'Krishna','result':'full_name'})
