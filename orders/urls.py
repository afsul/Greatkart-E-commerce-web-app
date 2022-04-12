from django.urls import path
from . import views

urlpatterns = [
   
   path('place_orders/', views.place_order, name='place_order'),
 
   path('order_complete/', views.order_complete , name='order_complete'),
   path('cod_order_complete/<int:order_number>/',views.cod_order_complete, name='cod_order_complete'),
   path('user_order_cancel/<int:order>',views.user_order_cancel, name='user_order_cancel'),
   path('user_order_return/<int:order>',views.user_order_return, name='user_order_return'),
  

   





] 