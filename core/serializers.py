from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers

class UserCreateSerializer(BaseUserCreateSerializer):
    birt_date=serializers.DateField()
    class Meta(BaseUserCreateSerializer.Meta):
        fields=['id','username','password','email','first_name','last_name']



#this field will for the display when the we get the user by the jwt
class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields=['id','username','email','first_name','last_name']