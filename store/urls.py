from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('products/', views.product_list),
    path('products/<int:id>/', views.product_detail),#to get only integer values
    path('collections/<int:pk>/', views.collection_detail,name='collection_detail')#to get only integer values

]