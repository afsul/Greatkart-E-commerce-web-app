
from multiprocessing import context
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages,auth
from accounts.models import Account
from category.forms import CategoryForm
from category.models import Category
from django.contrib.auth.decorators import login_required
from store.forms import ProductForm
from django.utils.text import slugify
from store.models import Product 

# Create your views here.

def admin_home(request):
    
    return render(request, 'admin/admin-home.html')

def admin_login(request):
  if  request.session.get('admin_login'):
    return render(request, 'admin/admin-home.html')

  else:   
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        superadmin = auth.authenticate(email=email, password=password)

        if superadmin is not None:
            auth.login(request, superadmin) 
            request.session['admin_login'] = 'admin_signin' 
            return redirect('admin_home')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('admin-login')
    return render(request, 'admin/admin-login.html')

def admin_logout(request):
   
    auth.logout(request)
    try:
        del request.session['admin_login']
    except:
        pass
   
    messages.success(request, 'You are logged out')
    return redirect('admin-login')

def user_list(request):
    users = Account.objects.all()
    context = {'users':users}
    return render(request, 'admin/user_table.html',context)

def user_edit(request):
    return render(request, 'user_edit.html')

@login_required()
def user_deactivate(request, user_id):
    user = Account.objects.get(pk=user_id)
    user.is_active = False
    user.save()
    messages.success(request, "User account has been succesfully deactivated!")    
    return redirect('user-table')
@login_required()
def user_activate(request, user_id):
    user = Account.objects.get(pk=user_id)
    user.is_active = True
    user.save()
    messages.success(request, "User account has been succesfully activated")
    return redirect('user-table')


# Category list
def category(request):
    category_items =  Category.objects.all()
    context ={'category_items':category_items}
    return render(request, 'admin/category/category-list.html',context)


# Category Add
def add_category(request):
    context={}
    form = CategoryForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
    context['form']= form
    return render(request, 'admin/category/add-category.html', context)

# Category edit
@login_required()
def edit_category(request ,id):
    if request.user.is_authenticated:
        if request.user.is_superadmin:
            instance = get_object_or_404(Category, id=id)
            form = CategoryForm(request.POST or None, request.FILES or None, instance=instance)
            if request.method == "POST":
                if form.is_valid():
                    form.save()
                    messages.success(request,'Product has been updated')
                    return redirect('category')
                else:
                    instance = get_object_or_404(Category, id=id)
                    form = CategoryForm(request.POST or None, request.FILES or None, instance=instance)  
                    context = {
                        'form'     : form,
                        'category':instance,
                        }
                    return render(request, 'admin/category/edit-category.html',context)
            else:
                instance = get_object_or_404(Category, id=id)
                form = CategoryForm(request.POST or None, request.FILES or None, instance=instance)  
                context = {
                    'form'     : form,
                    'category':instance,
                    }
                return render(request, 'admin/category/edit-category.html',context)

# Category delete
@login_required
def delete_category(request,id):
   category = Category.objects.get(id=id)
   category.delete()
   return redirect('category')


#products list

def products_list(request):
  
    products = Product.objects.all()
    context = {
        'product':products,
    }
    return render(request, 'admin/products/products_list.html', context)

#add product
def add_product(request):
        if request.user.is_authenticated:
            if request.user.is_superadmin:
                if request.method == 'POST':
                    form = ProductForm(request.POST or None, request.FILES or None)
                    if form.is_valid():
                        product_name = form.cleaned_data['product_name']
                        slug = slugify(product_name)
                        description = form.cleaned_data['description']
                        price = form.cleaned_data['price']
                        images = form.cleaned_data['images']
                        stock = form.cleaned_data['stock']
                        # is_available = form.cleaned_data['is_available']
                        category = form.cleaned_data['category']
                        
                        product = Product.objects.create(product_name=product_name, slug=slug, description=description, price=price, images=images, stock=stock,category=category)
                        product.save()
                        return redirect('products_list')
                
                    else:
                        form = ProductForm(request.POST or None, request.FILES or None)
                        context = {
                                'form':form
                            }
                    return render(request, 'admin/products/add_product.html', context)

                else:
                    form = ProductForm(request.POST or None, request.FILES or None)
                    context = {
                                'form':form
                            }
                    return render(request, 'admin/products/add_product.html', context)
            else:
                return redirect('admin/admin_login')

        else:
            return redirect('admin_login')  



# Product edit
def edit_product(request ,id):
    
     if request.user.is_authenticated:
        if request.user.is_superadmin:
            instance = get_object_or_404(Product, id=id)
            form = ProductForm(request.POST or None, request.FILES or None, instance=instance)
            if request.method == "POST":
                if form.is_valid():
                    form.save()
                    messages.success(request,'Product has been updated')
                    return redirect('products_list')
                else:
                    instance = get_object_or_404(Product, id=id)
                    form = ProductForm(request.POST or None, request.FILES or None, instance=instance)  
                    context = {
                        'form'     : form,
                        'product':instance,
                        }
                    return render(request, 'admin/products/edit_product.html',context)
            else:
                instance = get_object_or_404(Product, id=id)
                form = ProductForm(request.POST or None, request.FILES or None, instance=instance)  
                context = {
                    'form'     : form,
                    'product':instance,
                    }
                return render(request, 'admin/products/edit_product.html',context)
# product delete
def product_delete(request,id):
    product = Product.objects.get(id=id)
    product.delete()
    # messages.success(request,"Product deleted successfully.")
    return redirect('products_list')