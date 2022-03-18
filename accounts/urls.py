from django.urls import path
from . import views


urlpatterns = [ 
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'), 
    path('new_user_otp_varification/', views.new_user_otp_varification, name='new_user_otp_varification'), 

    # path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]