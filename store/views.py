from django.db.models import Count 
from django.shortcuts import *#get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters     import SearchFilter,OrderingFilter
from rest_framework.mixins      import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,UpdateModelMixin
from rest_framework.response    import Response 
from rest_framework.viewsets    import ModelViewSet,GenericViewSet#shortcut for all 
from rest_framework.decorators  import action
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser,DjangoModelPermissions
from rest_framework import status
from .models        import OrderItem, Product,Collection,Review,Cart,CartItem,Customer,Order,ProductImage
from .serializers   import ProductSerializer,CollectionSerializer,ReviewSerializer,CartSerializer,CartItemSerializer,AddCartItemSeializer,UpdateCartItemSerializer,CustomerSerializer,OrderSerializer,CreateOrderSerializer,UpdateOrderSerializer,ProductImagesSerializer
from .filters       import ProductFilter
from .pagination    import DefaultPagination
from .permissions   import IsAdminOrReadOnly,FullDjangoModelPermissions,ViewCustomerHistoryPermission

#unused imports.........
# from django.http import HttpResponse
# from rest_framework.views import APIView
# from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
# from rest_framework.mixins import ListModelMixin,CreateModelMixin
# from django.shortcuts import render
# from rest_framework.decorators import api_view
# from rest_framework.pagination import PageNumberPagination #as we are importing from pagination class

# Create your views here.

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related('images').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]#types of filter backend that are going to be applied
    filterset_class =ProductFilter#its for maiking filter in api 
    permission_classes=[IsAdminOrReadOnly]
    pagination_class = DefaultPagination#pagination can be done from Settings file or by maually importing as done in pagination.py
    # pagination_class=PageNumberPagination  # WE DONT HAVE DO DECLARE PAGINATION IF WE HAVE DECLARE GLOBALLY IN SETTINGS FILE
    search_fields=['name','description','collection__title']#search fields for api
    ordering_fields=['unit_price','last_update']#ordering fields,Format of Ordering
    

    
    def get_serializer_context(self):
        return {'request':self.request}
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count()>0:
            return Response({'error':'Product cannot be deleted, because it is associated with an order item. ' },status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

class CollectionViewSet(ModelViewSet):
    queryset=Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class=CollectionSerializer
    permission_classes=[IsAdminOrReadOnly]

    #if collection is linked with proucts, this fucntion will check that if there is product associated by the collection by checking count if not u can delete else not
    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).count()>0:
            return Response({'error':'Collection cannot be deleted because its included in one or more products'},status.HTTP_204_NO_CONTENT)
        return super().destroy(request, *args, **kwargs)

class ReviewViewSet(ModelViewSet):
    queryset=Review.objects.all()
    serializer_class=ReviewSerializer

    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}

#as we donot want to show the id therefore we are not using model view set therefore to to restrict get we use differently all arguments
class CartViewSet(CreateModelMixin,GenericViewSet,RetrieveModelMixin,DestroyModelMixin):
    queryset=Cart.objects.prefetch_related('items__product').all() #using prefetch beacuse a cart can have multiple items if only have we use select related where we have foreign key to many relationship
    serializer_class=CartSerializer


#as we want to get the cart items by its id only not all carti items must be display therfore we would use queryset to obtain particular id query set
class CartItemViewSet(ModelViewSet):
    http_method_names=['get','post','patch','delete']#all must be in lower case
    # queryset=CartItem.objects.all()
    serializer_class=CartItemSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSeializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id':self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')

class CustomerViewSet(CreateModelMixin,RetrieveModelMixin,UpdateModelMixin,GenericViewSet):
    queryset=Customer.objects.all()
    serializer_class=CustomerSerializer
    permission_classes=[FullDjangoModelPermissions]

    # def get_permissions(self):
    #     if self.request.method =='GET':
    #         return [AllowAny()]
    #     return[IsAdminUser]
    @action(detail=True,permission_classes=[ViewCustomerHistoryPermission])
    def history(self,request,pk):
        return Response('ok')


    #Getting Current User
    @action(detail=False,methods=['GET','PUT'],permission_classes=[IsAuthenticated])
    def me(self,request):
        #first value is customer object and second value is the boolean 
        customer=Customer.objects.get(user_id=request.user.id)


        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer=CustomerSerializer(customer,data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class OrderViewset(ModelViewSet):
    http_method_names=['get','post','patch','delete','head','options']
    # serializer_class=OrderSerializer
    def get_permissions(self):#making permission that only authenticated user can do this stuff
        if self.request.method in ['PATCH','DELETE']:
            return [IsAdminUser()]
        return[IsAuthenticated()]
    

    def get_serializer_class(self):
        if self.request.method =='POST':
            return CreateOrderSerializer
        elif self.request.method =='PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serialzer=CreateOrderSerializer(data=request.data,context={'user_id':self.request.user.id})
        serialzer.is_valid(raise_exception=True)
        order=serialzer.save()
        serialzer=OrderSerializer(order)
        return Response(serialzer.data)

#commenting as we are not using mixin for getting the context
    # def get_serializer_context(self):
    #     return {'user_id':self.request.user.id}

    #introducing get query set method so that only the user with particular id can view the data
    def get_queryset(self):
        user=self.request.user
        if user.is_staff:
            return Order.objects.all()
        
        customer_id = Customer.objects.only('id').get(user_id=user.id) #get_or_create uses two values therfore we have to make it in bracket
        return Order.objects.filter(customer_id=customer_id)



class ProductImageViewSet(ModelViewSet):
    serializer_class=ProductImagesSerializer
    # queryset=Product.objects.all() #as we donot wnat to return all the products we want to return only the images of the product with the particular id
    # we will use queryset to get the images of the product with the particular id
    # we want to take the product id from the url therefore we willuse product_id=self.kwargs['product_pk']

    #to get the product id
    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])
        
    














































































































































#can be replaced by using django filtering
    # def get_queryset(self):
    #     queryset=Product.objects.all()
    #     collection_id=self.request.query_params.get('collection_id')
    #     if collection_id is not None:
    #         queryset=queryset.filter(collection_id=collection_id)
    #     return queryset


    # def delete(self,request,pk): #ovveridding the delete class from the generic file
    #     product=get_object_or_404(Product,pk=id)
    #     if product.orderitems.count()>0:
    #         return Response({'error':'Product cannot be deleted, because it is associated with an order item. ' },status=status.HTTP_400_BAD_REQUEST)
    #     product.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)

    # def delete(self,request,pk):
    #     collection=get_object_or_404(Collection,pk=pk)
    #     if collection.products.count()>0:
    #         return Response({'error':'Collection cannot be deleted because its included in one or more products'},status.HTTP_204_NO_CONTENT)
    #     collection.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)

#product list in form of class
# class ProductList(ListCreateAPIView):

#     queryset=Product.objects.all()
#     serializer_class=ProductSerializer
#     # def get_queryset(self):#this is used when we have to implement some special condition 
#     #     return Product.objects.select_related('collection').all()
    
#     # def get_serializer_class(self):
#     #     return ProductSerializer

#     def get_serializer_context(self):# get_serializer_context is used when we have added some additional context serializer class
#         return {'request':self.request}

#     # def get(self,request):
#     #     queryset=Product.objects.select_related('collection').all()#we can preload the collection field to increase efficiency of query processing
#     #     serializer =ProductSerializer(queryset,many=True,context={'request':request})
#     #     return Response(serializer.data)

#     # def post(self,request):
#     #     serializer=ProductSerializer(data=request.data)
#     #     serializer.is_valid(raise_exception=True)
#     #     serializer.save()
#     #     # print(serializer.validated_data)
#     #     return Response(serializer.data,status=status.HTTP_201_CREATED)    


# #prodcut detial view in form of class
# class ProductDetail(RetrieveUpdateDestroyAPIView):
#     queryset =Product.objects.all()
#     serializer_class=ProductSerializer
#     # lookup_field='id' #this is used when we have to set something instead of inbuilt 


#     # def get(self,request,id):
#     #     product=get_object_or_404(Product,pk=id) 
#     #     serializer=ProductSerializer(product)    
#     #     return Response(serializer.data)

#     # def put(self,request,id):
#     #     product=get_object_or_404(Product,pk=id)
#     #     serializer=ProductSerializer(product,data=request.data)
#     #     serializer.is_valid(raise_exception=True)
#     #     serializer.save()
#     #     return Response(serializer.data)
    
#     def delete(self,request,pk): #ovveridding the delete class from the generic file
#         product=get_object_or_404(Product,pk=id)
#         if product.orderitems.count()>0:
#             return Response({'error':'Product cannot be deleted, because it is associated with an order item. ' },status=status.HTTP_400_BAD_REQUEST)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)






# #class for collection list
# class CollectionList(ListCreateAPIView):
#     queryset=Collection.objects.annotate(products_count=Count('products')).all()
#     serializer_class=CollectionSerializer

#     # def get(self,request):
#     #     queryset=Collection.objects.annotate(products_count=Count('products')).all()
#     #     serializer=CollectionSerializer(queryset,many=True)
#     #     return Response(serializer.data)
    
#     # def post(self,request):
#     #     serializer=CollectionSerializer(data=request.data)
#     #     serializer.is_valid(raise_exception=True)
#     #     serializer.save()
#     #     return Response(serializer.data,status=status.HTTP_201_CREATED)
    
# #class for Collection detail
# class ColletionDetail(RetrieveUpdateDestroyAPIView):
#     queryset=Collection.objects.annotate(products_count=Count('products'))
#     serializer_class=CollectionSerializer




#     # def get(self,request,pk):
#     #     collection=get_object_or_404(Collection.objects.annotate(products_count=Count('products')),pk=pk)
#     #     serializer=CollectionSerializer(collection)
#     #     return Response(serializer.data)
    
#     # def put(self,request,pk):
#     #     collection=get_object_or_404(Collection.objects.annotate(products_count=Count('products')),pk=pk)
#     #     serializer=CollectionSerializer(collection,data=request.data)
#     #     serializer.is_valid(raise_exception=True)
#     #     serializer.save()
#     #     return Response(serializer.data)
    
#     def delete(self,request,pk):
#         collection=get_object_or_404(Collection,pk=pk)
#         if collection.products.count()>0:
#             return Response({'error':'Collection cannot be deleted because its included in one or more products'},status.HTTP_204_NO_CONTENT)
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)





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