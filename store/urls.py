from django.urls import path
from . import views

# from rest_framework.routers import SimpleRouter,DefaultRouter
from django.urls.conf import include
from rest_framework_nested import routers
# from pprint import pprint

router=routers.DefaultRouter()


router.register('products',views.ProductViewSet,basename='products')
router.register('collections',views.CollectionViewSet)
router.register('carts',views.CartViewSet)
router.register('customers',views.CustomerViewSet)
router.register('orders',views.OrderViewset,basename='order')#if query_set is removed and we are using get funciton we have to give base name of the model


#base of the product router
products_router=routers.NestedDefaultRouter(router,'products', lookup='product')
products_router.register('reviews',views.ReviewViewSet,basename='product-reviews')
products_router.register('images',views.ProductImageViewSet,basename='product-images') #declaring the nested router on product router


carts_router=routers.NestedDefaultRouter(router,'carts',lookup='cart')
carts_router.register('items',views.CartItemViewSet,basename='cart-items')

urlpatterns=router.urls + products_router.urls + carts_router.urls


# pprint(router.urls)
# URLConf
# urlpatterns = [
#     path('products/', views.ProductList.as_view()),
#     path('products/<int:pk>/', views.ProductDetail.as_view()),
#     path('collections/<int:pk>/', views.ColletionDetail.as_view()),
#     path('collections/',views.CollectionList.as_view())
#     # path('products/', views.product_list),
#     # path('products/<int:id>/', views.product_detail),#to get only integer values
#     # path('collections/<int:pk>/', views.collection_detail,name='collection_detail'),#to get only integer values
#     # path('collections/',views.collection_list),
# ]

