from django.shortcuts import redirect, render
from django.contrib import messages,auth
from accounts.models import Account

# Create your views here.

def admin_home(request):
    users = Account.objects.all()
    context = {'users':users}
    return render(request, 'admin/admin-home.html', context)

def admin_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        superadmin = auth.authenticate(email=email, password=password)

        if superadmin is not None:
            auth.login(request, superadmin) 
            return redirect('admin_home')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('admin-login')
    return render(request, 'admin/admin-login.html')

def admin_logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out')
    return redirect('admin-login')