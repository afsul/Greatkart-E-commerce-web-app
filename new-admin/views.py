from django.shortcuts import render

from accounts.models import Account

# Create your views here.

def admin_home(request):
    users = Account.objects.all()
    context = {'users':users}
    return render(request, 'admin/admin-home.html', context)