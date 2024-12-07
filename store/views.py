
from django.shortcuts import *#get_object_or_404
from django.shortcuts import render
from django.http import HttpResponse
# from rest_framework.mixins import ListModelMixin,CreateModelMixin
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet #shortcut for all 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Product,Collection
from django.db.models import Count 
from .serializers import ProductSerializer,CollectionSerializer

# Create your views here.

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        return {'request':self.request}

    def delete(self,request,pk): #ovveridding the delete class from the generic file
        product=get_object_or_404(Product,pk=id)
        if product.orderitems.count()>0:
            return Response({'error':'Product cannot be deleted, because it is associated with an order item. ' },status=status.HTTP_400_BAD_REQUEST)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CollectionViewSet(ModelViewSet):
    queryset=Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class=CollectionSerializer

    def delete(self,request,pk):
        collection=get_object_or_404(Collection,pk=pk)
        if collection.products.count()>0:
            return Response({'error':'Collection cannot be deleted because its included in one or more products'},status.HTTP_204_NO_CONTENT)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



#product list in form of class
class ProductList(ListCreateAPIView):

    queryset=Product.objects.all()
    serializer_class=ProductSerializer
    # def get_queryset(self):#this is used when we have to implement some special condition 
    #     return Product.objects.select_related('collection').all()
    
    # def get_serializer_class(self):
    #     return ProductSerializer

    def get_serializer_context(self):# get_serializer_context is used when we have added some additional context serializer class
        return {'request':self.request}

    # def get(self,request):
    #     queryset=Product.objects.select_related('collection').all()#we can preload the collection field to increase efficiency of query processing
    #     serializer =ProductSerializer(queryset,many=True,context={'request':request})
    #     return Response(serializer.data)

    # def post(self,request):
    #     serializer=ProductSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     # print(serializer.validated_data)
    #     return Response(serializer.data,status=status.HTTP_201_CREATED)    


#prodcut detial view in form of class
class ProductDetail(RetrieveUpdateDestroyAPIView):
    queryset =Product.objects.all()
    serializer_class=ProductSerializer
    # lookup_field='id' #this is used when we have to set something instead of inbuilt 


    # def get(self,request,id):
    #     product=get_object_or_404(Product,pk=id) 
    #     serializer=ProductSerializer(product)    
    #     return Response(serializer.data)

    # def put(self,request,id):
    #     product=get_object_or_404(Product,pk=id)
    #     serializer=ProductSerializer(product,data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data)
    
    def delete(self,request,pk): #ovveridding the delete class from the generic file
        product=get_object_or_404(Product,pk=id)
        if product.orderitems.count()>0:
            return Response({'error':'Product cannot be deleted, because it is associated with an order item. ' },status=status.HTTP_400_BAD_REQUEST)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)






#class for collection list
class CollectionList(ListCreateAPIView):
    queryset=Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class=CollectionSerializer

    # def get(self,request):
    #     queryset=Collection.objects.annotate(products_count=Count('products')).all()
    #     serializer=CollectionSerializer(queryset,many=True)
    #     return Response(serializer.data)
    
    # def post(self,request):
    #     serializer=CollectionSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data,status=status.HTTP_201_CREATED)
    
#class for Collection detail
class ColletionDetail(RetrieveUpdateDestroyAPIView):
    queryset=Collection.objects.annotate(products_count=Count('products'))
    serializer_class=CollectionSerializer
 



    # def get(self,request,pk):
    #     collection=get_object_or_404(Collection.objects.annotate(products_count=Count('products')),pk=pk)
    #     serializer=CollectionSerializer(collection)
    #     return Response(serializer.data)
    
    # def put(self,request,pk):
    #     collection=get_object_or_404(Collection.objects.annotate(products_count=Count('products')),pk=pk)
    #     serializer=CollectionSerializer(collection,data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data)
    
    def delete(self,request,pk):
        collection=get_object_or_404(Collection,pk=pk)
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

# @api_view(['GET','POST'])
# def collection_list(request):
#     if request.method =='GET':
#         queryset=Collection.objects.annotate(products_count=Count('products')).all()
#         serializer=CollectionSerializer(queryset,many=True)
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         serializer=CollectionSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data,status=status.HTTP_201_CREATED)


# @api_view(['GET','PUT','DELETE'])
# def collection_detail(request,pk):
#     collection=get_object_or_404(Collection.objects.annotate(products_count=Count('products')),pk=pk)
#     if request.method == 'GET':
#         serializer=CollectionSerializer(collection)
#         return Response(serializer.data)
#     elif request.method == 'PUT':
#         serializer=CollectionSerializer(collection,data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     elif request.method == 'DELETE':
#         if collection.products.count()>0:
#             return Response({'error':'Collection cannot be deleted because its included in one or more products'},status.HTTP_204_NO_CONTENT)
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)