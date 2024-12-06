from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer



# Create your views here.


@api_view()
def product_list(request):
    queryset=Product.objects.select_related('collection').all()#we can preload the collection field to increase efficiency of query processing
    serializer =ProductSerializer(queryset,many=True,context={'request':request})
    return Response(serializer.data)


@api_view()
def product_detail(request,id):
        # product=Product.objects.get(pk=id)#getting the details of the id provided and storing in the product
        product=get_object_or_404(Product,pk=id)#this will throw the error if the object is not found, its an shortcut we donot have to apply try catch block for this
        serializer=ProductSerializer(product)#getting the converted data and storing it
        return Response(serializer.data)# .data is used to get the data stored


@api_view()
def collection_detail(request,pk):
    return Response('ok')