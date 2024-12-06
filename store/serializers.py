from decimal import Decimal
from rest_framework import serializers

from store.models import Product,Collection


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Collection
        fields=['id','title','products_count']
    
    products_count=serializers.IntegerField()

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


