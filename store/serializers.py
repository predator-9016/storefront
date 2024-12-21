from decimal import Decimal
from rest_framework import serializers
from django.db import transaction
from .signals import order_created
from store.models import Product,Collection,Review,Cart,CartItem,Customer,Order,OrderItem


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Collection
        fields=['id','title','products_count']
    
    products_count=serializers.IntegerField(read_only=True)

    # id = serializers.IntegerField()
    # title= serializers.CharField(max_length=255)

#the role of the serializer file is to convert the upcoming data into json dictionary 
# class ProductSerializer(serializers.Serializer):
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        #this will call from the model of the product & we dont have to write more no of codes
        model = Product
        fields = ['id','title','description','slug','inventory','price','price_with_tax','collection']
        # fields='__all__' for getting all from the model class


    # id=serializers.IntegerField()
    # title=serializers.CharField(max_length=255)
    price=serializers.DecimalField(max_digits=6,decimal_places=2,source='unit_price')#if the name is differaent from the modelsa we have to give source 
    price_with_tax=serializers.SerializerMethodField(method_name='calculate_tax')# if want to change something we can write in the sub part of the modelserializer it will change the ui
    # collection = serializers.HyperlinkedRelatedField(
    #     queryset=Collection.objects.all(),
    #     view_name='collection_detail',
    #     lookup_field='pk'
    # )
    # collection =CollectionSerializer()#the name points the collection name
    # collection=serializers.StringRelatedField()#this will return the string name of the field

    # collection=serializers.PrimaryKeyRelatedField(#to get the id of the collection that product will have
    #     queryset=Collection.objects.all()
    # )

    def calculate_tax(self,product:Product):
        return product.unit_price*Decimal(1.1)
    
    # def validate(self,data):
    #     if data['password']!= data['confirm_password']:
    #         return serializers.ValidationError('Passwords do not match')
    #     return data


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model=Review
        fields=['id','date','name','description']

    def create(self, validated_data):
        product_id=self.context['product_id']
        return Review.objects.create(product_id=product_id,**validated_data)
    


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields=['id','title','unit_price']

class CartItemSerializer(serializers.ModelSerializer):
    product=SimpleProductSerializer()#for displaying only some part of the product details
    total_price=serializers.SerializerMethodField()#method field indicates that it would get output from the methods

    #method to find the total price the fields used are present on cart items
    def get_total_price(self,cart_item:CartItem):#get and then variable name is used to get the variable output
        return cart_item.quantity * cart_item.product.unit_price
    class Meta:
        model=CartItem
        fields=['id','product','quantity','total_price']

class CartSerializer(serializers.ModelSerializer):
    id=serializers.UUIDField(read_only=True)#as we dont want id we just want empty object when creting therefore making it to readonly field
    items=CartItemSerializer(many=True,read_only=True)#as we dont want to create items
    total_price=serializers.SerializerMethodField()#method field as we are going to get by creating the method

    def get_total_price(self,cart):#totalprice method
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])
    
    class Meta:
        model=Cart
        fields=['id','items','total_price']

class AddCartItemSeializer(serializers.ModelSerializer):
    product_id=serializers.IntegerField()

    def validate_product_id(self,value):
        if not Product.objects.filter(pk=value).exists():#if product not found , conditon will become true and will raise the error
            raise serializers.ValidationError('Product does not exist of the given id')
        return value#if found return the value means id

#behing the scene there is serializer isvalid then we can get it from validated data currently we are inside the serializer class so we will access through self.validate data
    def save(self, **kwargs):
        cart_id=self.context['cart_id']
        product_id=self.validated_data['product_id']
        quantity=self.validated_data['quantity']

        try:#Updating an existing item
            cart_item=CartItem.objects.get(cart_id=cart_id ,product_id=product_id)#if the cartid and product id is same just increasing the quantity
            cart_item.quantity+=quantity
            cart_item.save()
            self.instance=cart_item
        except CartItem.DoesNotExist:#Creating a new item,if not same creating a new cart item
            self.instance=CartItem.objects.create(cart_id=cart_id,**self.validated_data)#unpacking all the validated data
    
        return self.instance

    class Meta:
        model=CartItem
        fields=['id','product_id','quantity']

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=CartItem
        fields=['quantity']


class CustomerSerializer(serializers.ModelSerializer):
    user_id=serializers.IntegerField(read_only=True)
    class Meta:
        model=Customer
        fields=['id','user_id','phone','birth_date','membership']

class OrderItemSerializer(serializers.ModelSerializer):
    product=SimpleProductSerializer()
    class Meta:
        model=OrderItem
        fields=['id','product','unit_price','quantity']

class OrderSerializer(serializers.ModelSerializer):

    items=OrderItemSerializer(many=True)
    class Meta:
        model=Order
        fields=['id','customer','placed_at','payment_status','items']

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=['payment_status']





#while creating the order the all we have to send is the only cart_id for placing the order
#we are not using the Model Serializer as we are not using Model we are going to define explicitly cart_id
class CreateOrderSerializer(serializers.Serializer):
    cart_id=serializers.UUIDField()

    payment_option=serializers.CharField(max_length=20)
    # if the cart item has zero items,and if wront id give what error should show
    def validate_cart_id(self,cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError("No Cart with the given Id")
        if CartItem.objects.filter(cart_id=cart_id).count()==0:
            raise serializers.ValidationError("The cart is empty")
        return cart_id


    def save(self,**kwargs):
        with transaction.atomic():
            carts_id=self.validated_data['cart_id']
            customer=Customer.objects.get(user_id=self.context['user_id'])
            order=Order.objects.create(customer=customer)
            cart_items=CartItem.objects.select_related('product').filter(cart_id=carts_id)
            order_items=[
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                )for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(pk=carts_id).delete()
            order_created.send_robust(self.__class__,order=order)
            return order