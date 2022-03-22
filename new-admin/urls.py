from django.urls import path
from . import views

urlpatterns = [
  
    path('',views.admin_home,name='admin_home'),
    path('/login', views.admin_login, name='admin-login'),
    path('/logout', views.admin_logout, name='admin-logout'),
    path('/usertable',views.user_list,name='user-table'),
    path('/category', views.category, name='category'),
    path('/add_category',views.add_category,name='add_category'),
    path('/edit_category/<int:id>',views.edit_category,name='edit_category'),
    path('/delete_category/<int:id>',views.delete_category,name='delete_category'),
    path('deactivate/<int:user_id>',views.user_deactivate,name='deactivate_user'),
    path('user_activate/<int:user_id>',views.user_activate,name='user_activate'),
    path('/products_list',views.products_list,name='products_list'),
    path('/add_product',views.add_product,name='add_product'),
    path('/edit_product/<int:id>',views.edit_product,name='edit_product'),
    path('/product_delete/<int:id>',views.product_delete,name='product_delete'),
    path('/orders_list',views.orders_list,name='orders_list'),
    path('/cancel_order_admin/<int:id>',views.cancel_order_admin,name='cancel_order_admin'),

    




    




    

] 