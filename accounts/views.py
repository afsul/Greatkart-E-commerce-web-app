# from email.message import EmailMessage
from audioop import add
from email.mime import message
from multiprocessing import context
import os
from django.contrib import messages,auth
# from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from twilio.rest import Client
from accounts.models import Account, UserProfile
from carts.models import Cart, CartItem
from carts.views import _cart_id
from orders.models import Order
import razorpay
from .forms import RegistrationfForm, UserForm, UserProfileForm
import requests
from .private import TWILIO_SERVICE_SID,TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN

# #Vefication email
# from django.contrib.sites.shortcuts import get_current_site
# from django.template.loader import render_to_string
# from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
# from django.utils.encoding import force_bytes
# from django.core.mail import EmailMessage


# Create your views here.

def register(request):

    if request.method == 'POST':
        form = RegistrationfForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password, phone_number=phone_number)
            user.save()


            # Create User Profile
            profile = UserProfile()
            profile.user_id = user.id
            profile.save()



           
            # otp account varification

            request.session["mobile"] = phone_number
            user = Account.objects.filter(phone_number=phone_number)

            for m in user:
                if m.phone_number == phone_number:
                    user_mobile = "+91" + phone_number

                    # Your Account Sid and Auth Token from twilio.com / console
                    account_sid = TWILIO_ACCOUNT_SID
                    auth_token = TWILIO_AUTH_TOKEN
                    client = Client(account_sid, auth_token)
                    verification = client.verify.services(TWILIO_SERVICE_SID).verifications.create(to=user_mobile, channel="sms")

                    print(verification.status)
                    return redirect("new_user_otp_varification")
    else:
        form = RegistrationfForm()
    context = {
        "form": form,
    }
    return render(request, "accounts/register.html", context)


def new_user_otp_varification(request):
    try:
        if request.method == "POST":
            otp = request.POST["otp"]
            mobile = request.session["mobile"]
            user_mobile = "+91" + mobile

            # twilio code for otp generation
            account_sid = TWILIO_ACCOUNT_SID
            auth_token = TWILIO_AUTH_TOKEN
            client = Client(account_sid, auth_token)

            verification_check = client.verify \
                            .services(TWILIO_SERVICE_SID) \
                            .verification_checks \
                            .create(to=user_mobile, code=otp)
            print(verification_check.status)

            # checking otp is valid or not. If valid redirect home
            if verification_check.status == "approved":
                messages.success(request, "OTP verified successfully.")
                user = Account.objects.get(phone_number=mobile)  # user details
                user.is_active = True
                user.save()
                auth.login(request, user)
                return redirect("home")
                # try: 
                #     del request.session["mobile"]
                # except:
                #     pass

                # return redirect("home")
            else:
                messages.error(request, "Invalid OTP")
                return render(request, "accounts/new_user_otp_page.html")
        else:
            return render(request, "accounts/new_user_otp_page.html")
    except:
        messages.error(request, "Enter a valid OTP")
        return render(request, "accounts/new_user_otp_page.html")

    
def login(request):
  if  request.session.get('user_login'):
        return redirect('home')

  else:    
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']

            user = auth.authenticate(email=email, password=password)

            if user is not None:
                try:
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                    if is_cart_item_exists:
                        cart_item = CartItem.objects.filter(cart=cart)

                        for item in cart_item:
                            item.user = user
                            item.save()
                except:
                    pass
  
                auth.login(request, user)
                request.session['user_login'] = 'user_signin' 
                messages.success(request, "You are now logged in.")
                url = request.META.get('HTTP_REFERER')
                try:
                    query = requests.utils.urlparse(url).query
                    # next/cart/checkout/
                    params = dict(x.split('=') for x in query.split('&'))
                    if 'next' in params:
                        nextPage = params['next']
                        return redirect(nextPage)
                except:
                    return redirect('home')
            else:
                messages.error(request, 'Invalid login credentials')
                return redirect('login')
  return render(request, 'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
    try:
        del request.session['user_login']
    except:
        pass
    auth.logout(request)
   
    messages.success(request, 'You are logged out')
    return redirect('login')

# def activate(request, uidb64, token):
#     return HttpResponse('ok')

@login_required(login_url = 'login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered = True)
    orders_count = orders.count()
    context = {
        'orders_count':orders_count,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url = 'login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)

    
@login_required(login_url = 'login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
        else:
            user_form = UserForm(instance = request.user)
            profile_form = UserProfileForm(instance = userprofile)
    
        context = {
                'user_form' :user_form,
                'profile_form':profile_form,
                  }
    else:
            user_form = UserForm(instance = request.user)
            profile_form = UserProfileForm(instance = userprofile)
    
            context = {
                'user_form' :user_form,
                'profile_form':profile_form,
                  }
            return render(request, 'accounts/edit_profile.html', context)
    
# change password
@login_required(login_url = 'login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact = request.user.username)
        if confirm_password == new_password:
                success = user.check_password(current_password)
                if success:
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'password updated succesfully')
                    return redirect(change_password)
                else:
                    messages.error(request, 'Please enter a valid password')
                    return redirect(change_password)
        else:
            messages.error(request, 'Password does not match!')
            return redirect(change_password)

    return render(request, 'accounts/change_password.html')    

def my_address(request):
    user =request.user
    address = UserProfile.objects.filter(user=user)
    context={
        'address':address,
    }
    return render(request, 'accounts/my_address.html',context)


def add_address(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST)
        if form.is_valid():
            user = Account.objects.get(id = request.user.id)
            address_line_1 = form.cleaned_data['address_line_1']
            address_line_2 = form.cleaned_data['address_line_2']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            country = form.cleaned_data['country']
    
            new_address = UserProfile.objects.create(user=user, address_line_1=address_line_1, address_line_2=address_line_2, city=city, state=state, country=country)
            new_address.save()       

            return redirect ('my_address')
        else:
            form = UserProfileForm()    
            context = {
                    'form':form
            }
            return render(request, 'accounts/add_address.html', context)
    else:
        form = UserProfileForm()    
        context = {
                    'form':form
            }
        return render(request, 'accounts/add_address.html', context)