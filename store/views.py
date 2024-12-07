
from django.shortcuts import *#get_object_or_404
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Product,Collection
from django.db.models import Count
from .serializers import ProductSerializer,CollectionSerializer

# Create your views here.

#product list in form of class
class ProductList(APIView):
    def get(self,request):
        queryset=Product.objects.select_related('collection').all()#we can preload the collection field to increase efficiency of query processing
        serializer =ProductSerializer(queryset,many=True,context={'request':request})
        return Response(serializer.data)

    def post(self,request):
        serializer=ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # print(serializer.validated_data)
        return Response(serializer.data,status=status.HTTP_201_CREATED)    


#prodcut detial view in form of class
class ProductDetail(APIView):
    def get(self,request,id):
        product=get_object_or_404(Product,pk=id) 
        serializer=ProductSerializer(product)    
        return Response(serializer.data)

    def put(self,request,id):
        product=get_object_or_404(Product,pk=id)
        serializer=ProductSerializer(product,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def delete(self,request,id):
        product=get_object_or_404(Product,pk=id)
        if product.orderitems.count()>0:
            return Response({'error':'Product cannot be deleted, because it is associated with an order item. ' },status=status.HTTP_400_BAD_REQUEST)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)






@api_view(['GET','POST'])
def collection_list(request):
    if request.method =='GET':
        queryset=Collection.objects.annotate(products_count=Count('products')).all()
        serializer=CollectionSerializer(queryset,many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer=CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    

@api_view(['GET','PUT','DELETE'])
def collection_detail(request,pk):
    collection=get_object_or_404(Collection.objects.annotate(products_count=Count('products')),pk=pk)
    if request.method == 'GET':
        serializer=CollectionSerializer(collection)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer=CollectionSerializer(collection,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if collection.products.count()>0:
            return Response({'error':'Collection cannot be deleted because its included in one or more products'},status.HTTP_204_NO_CONTENT)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# @api_view(['GET','POST'])
# def product_list(request):
#     if request.method == 'GET':
#         queryset=Product.objects.select_related('collection').all()#we can preload the collection field to increase efficiency of query processing
#         serializer =ProductSerializer(queryset,many=True,context={'request':request})
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         serializer=ProductSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         # print(serializer.validated_data)
#         return Response(serializer.data,status=status.HTTP_201_CREATED)


# @api_view(['GET','PUT','DELETE'])#For Updating all properties & Patch for updating subset of the properties
# def product_detail(request,id):
#     # product=Product.objects.get(pk=id)#getting the details of the id provided and storing in the product
#     product=get_object_or_404(Product,pk=id)#this will throw the error if the object is not found, its an       shortcut we donot have to apply try catch block for this
#     if request.method == 'GET':
#         serializer=ProductSerializer(product)#getting the converted data and storing it     
#         return Response(serializer.data)# .data is used to get the data stored      
#     elif request.method == 'PUT':
#         serializer=ProductSerializer(product,data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     elif request.method == 'DELETE':
#         if product.orderitems.count()>0:
#             return Response({'error':'Product cannot be deleted, because it is associated with an order item. ' },status=status.HTTP_204_NO_CONTENT)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)



# @api_view()
# def collection_detail(request,pk):
#     return Response('ok')