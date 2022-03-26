
from multiprocessing import context
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages,auth
from accounts.models import Account
from category.forms import CategoryForm
from category.models import Category
from django.contrib.auth.decorators import login_required
from orders.models import Order
from store.forms import ProductForm
from django.utils.text import slugify
from store.models import Product 



#Home
def admin_home(request):
    
    return render(request, 'admin/admin-home.html')


#Admin Login/logout
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


#User Managememt
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
                print('Entered to add product')
                if request.method == 'POST':
                    print('Entered to request ot method')
                    form = ProductForm(request.POST or None, request.FILES or None)
                    if form.is_valid():
                        print('form is valid')
                        product = Product()
                        product.product_name = form.cleaned_data['product_name']
                        product.slug = slugify(product.product_name)
                        product.description = form.cleaned_data['description']
                        product.price = form.cleaned_data['price']
                        product.images = form.cleaned_data['images']
                        product.stock = form.cleaned_data['stock']
                        product.category = form.cleaned_data['category']
                        product = Product.objects.create(product_name=product.product_name, slug=product.slug, description=product.description, price=product.price, images= product.images, stock=product.stock,category=product.category)
                        product.save()
                        print('products saved')
                        return redirect(products_list)
                    products = Product.objects.all()
                    category = Category.objects.only('category_name')
                    context = {
                                'products':products,
                                'category':category,
                            }
                    return render(request, 'admin/products/add_product.html', context)
                
                else:
                    form = ProductForm(request.POST or None, request.FILES or None)
                    context = {
                                'form':form
                            }
                    return render(request, 'admin/products/add_product.html', context)
                

            

# Product edit
def edit_product(request ,id):
    
     if request.user.is_authenticated:
        if request.user.is_superadmin:
            instance = get_object_or_404(Product, id=id)
            form = ProductForm(request.FILES or None, instance=instance)
            if request.method == "POST":
                if form.is_valid():
                    form.save()
                    messages.success(request,'Product has been updated')
                    return redirect('products_list')
                else:
                    instance = get_object_or_404(Product, id=id)
                    form = ProductForm(request.FILES or None, instance=instance)  
                    context = {
                        'form'     : form,
                        'product':instance,
                        }
                    return render(request, 'admin/products/edit_product.html',context)
            else:
                instance = get_object_or_404(Product, id=id)
                form = ProductForm(request.FILES or None, instance=instance)  
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

#Order Management
def orders_list(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders':orders
    }
    return render(request, 'admin/orders/orders_list.html', context)

def cancel_order_admin(request, id):
    print('entered to cancel function')
    order = Order.objects.get(user = request.user, order_number = id)
    
    if request.method == "POST":
        # status = request.POST['cancel_order']
        order.status = "Cancelled"
        order.save()   
        print('order cancelled')
    
    return redirect('orders_list')


def trial(request):
    return render(request,'admin/Trial/Cropper.html')