from django.urls import path
from . import views


urlpatterns = [ 
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'), 
    path('new_user_otp_varification/', views.new_user_otp_varification, name='new_user_otp_varification'),
    path('dashboard',views.dashboard, name='dashboard'),
    path('my_orders',views.my_orders, name='my_orders'),
    path('edit_profile',views.edit_profile, name='edit_profile'),
    path('change_password',views.change_password, name='change_password'),

    # path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]