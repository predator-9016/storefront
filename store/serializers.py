from decimal import Decimal
from rest_framework import serializers

from store.models import Product

#the role of the serializer file is to convert the upcoming data into json dictionary 
class ProductSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    title=serializers.CharField(max_length=255)
    price=serializers.DecimalField(max_digits=6,decimal_places=2,source='unit_price')#if the name is differaent from the modelsa we have to give source 
    price_with_tax=serializers.SerializerMethodField(method_name='calculate_tax')

    def calculate_tax(self,product:Product):
        return product.unit_price*Decimal(1.1)