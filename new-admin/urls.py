from random import triangular
from django.urls import path
from . import views

urlpatterns = [
    #Home
    path('',views.admin_home,name='admin_home'),

    #Admin Login/logout
    path('login/', views.admin_login, name='admin-login'),
    path('logout/', views.admin_logout, name='admin-logout'),

    #User management
    path('usertable/',views.user_list,name='user-table'),
    path('deactivate/<int:user_id>/',views.user_deactivate,name='deactivate_user'),
    path('user_activate/<int:user_id>/',views.user_activate,name='user_activate'),

    #Category Management
    path('category/', views.category, name='category'),
    path('add_category/',views.add_category,name='add_category'),
    path('edit_category/<int:id>/',views.edit_category,name='edit_category'),
    path('delete_category/<int:id>/',views.delete_category,name='delete_category'),

    #Product Management
    path('products_list/',views.products_list,name='products_list'),
    path('add_product/',views.add_product,name='add_product'),
    path('edit_product/<int:id>/',views.edit_product,name='edit_product'),
    path('product_delete/<int:id>/',views.product_delete,name='product_delete'),
    path('add_product_gallery/',views.add_product_gallery_image,name='add_product_gallery'),
    

    #Order Management
    path('orders_list/',views.orders_list,name='orders_list'),
    path('cancel_order_admin/<int:id>/',views.cancel_order_admin,name='cancel_order_admin'),
    path('update_order_status/<int:order_number>',views.update_order_status, name='update_order_status'),


    #sales report
    # path('sales_report/',views.sales_report, name = 'sales_report'),
    path('export_csv/',views.export_csv,name="export_csv"),
    path('adminsale',views.adminsale,name='adminsale'),
    # path('export_excel',views.export_excel,name='export_excel'),
    


    #offer management
    path('admin_offers/',views.admin_offers, name='admin_offers'),
    path('add_coupon/',views.add_coupon, name = 'add_coupon'),
    path('edit_coupon/<int:c_id>/',views.edit_coupon, name = 'edit_coupon'),    
    path('activate_coupon/',views.activate_coupon, name = 'activate_coupon'),     
    path('block_coupon/',views.block_coupon, name = 'block_coupon'),
    path('delete_coupon/',views.delete_coupon, name = 'delete_coupon'),

    path('add_product_offer/',views.add_product_offer, name = 'add_product_offer'),
    path('edit_product_offer/<int:prod_id>/',views.edit_product_offer, name = 'edit_product_offer'),    
    path('activate_product_offer/',views.activate_product_offer, name = 'activate_product_offer'),     
    path('block_product_offer/',views.block_product_offer, name = 'block_product_offer'),
    path('delete_product_offer/',views.delete_product_offer, name = 'delete_product_offer'),

    path('add_cat_offer/',views.add_cat_offer, name = 'add_cat_offer'),
    path('edit_cat_offer/<int:cat_id>/',views.edit_cat_offer, name="edit_cat_offer"),
    path('activate_cat_offer/',views.activate_cat_offer, name = 'activate_cat_offer'),     
    path('block_cat_offer/',views.block_cat_offer, name = 'block_cat_offer'),
    path('delete_cat_offer/',views.delete_cat_offer, name = 'delete_cat_offer'),

    #charts
    # path('doughnut/',views.doughnut,name='doughnut'),



    # path('delete_everything/',views.delete_everything,name='delete_everything')

] 