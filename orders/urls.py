from django.urls import path
from . import views

urlpatterns = [
   
   path('/place_orders', views.place_order, name='place_order'),    
   path('/payments', views.payments, name='payments'),
   path('/order_complete', views.order_complete , name='order_complete'),
   path('cod_order_complete/<int:order_number>',views.cod_order_complete, name='cod_order_complete'),
   path('cancel_order/<int:order_number>',views.cancel_order, name='cancel_order'),



] 