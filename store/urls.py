from django.urls import path
from . import views
from rest_framework.routers import SimpleRouter
from pprint import pprint

router=SimpleRouter()
router.register('products',views.ProductViewSet)
router.register('collections',views.CollectionViewSet)
# pprint(router.urls)

urlpatterns=router.urls


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

