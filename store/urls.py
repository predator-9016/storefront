from django.urls import path
from . import views

# URLConf
urlpatterns = [
    # path('products/', views.product_list),
    path('products/', views.ProductList.as_view()),
    # path('products/<int:id>/', views.product_detail),#to get only integer values
    path('products/<int:id>/', views.ProductDetail.as_view()),
    path('collections/<int:pk>/', views.collection_detail,name='collection_detail'),#to get only integer values
    path('collections/',views.collection_list)
]

