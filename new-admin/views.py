
from multiprocessing import context
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages,auth
from accounts.models import Account, UserProfile
from category.forms import CategoryForm
from category.models import Category
from django.contrib.auth.decorators import login_required
from orders.forms import OrderStatusForm
from orders.models import Order
from store.forms import ProductForm
from django.utils.text import slugify
from store.models import Product 
from django.db.models import Count



#Home
def admin_home(request):
    orders = Order.objects.filter(is_ordered=True).order_by('-created_at')
    category_chart = Category.objects.all()
    # products = Product.objects.get(category__id=category_chart).count()
    products_count = Category.objects.annotate(total_products=Count('product'))

    order_count = Order.objects.all().count()
    users_count = UserProfile.objects.all().count()
    total_products = Product.objects.all().count()
 
    print(products_count)   

  
    
    context = {
        'orders':orders,
        'category_chart':category_chart,
        'products_count':products_count,
        'order_count':order_count,
        'users_count':users_count,
        'total_products':total_products,
        
    }
    return render(request, 'admin/admin-home.html',context)


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
                    product_name = request.POST['product_name']
                    slug = slugify(product_name)
                    description = request.POST['description']
                    price = request.POST['price']
                    images = request.POST['image1']
                    # images = request.POST['image2']
                    # images = request.POST['image3']
                    # images = request.POST['image4']
                    stock = request.POST['quantity']
                    category = Category.objects.get(category_name=request.POST['category'])
                    cat_id = category.id
                    print(cat_id,"category ID")
                    print(category,"category")
                    product = Product.objects.create(product_name=product_name, slug=slug, description=description, price=price, stock=stock,category=category,images=images)
                    product.save()
                    messages.success(request,'Product Added Succesfully')
                    print('products saved')
                    return redirect(products_list)
                    # products = Product.objects.all()
                    
                    # context = {
                    #             'products':products,
                                
                                

                    #         }
                    # return render(request, 'admin/products/add_product.html', context)
                    
                
                else:
                    print('Entered to else case')
                    categories = Category.objects.only('category_name')
                    context = {
                                'categories': categories,
                            }
                    return render(request, 'admin/products/add_product.html',context)
                

            

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
    orders = Order.objects.filter(is_ordered=True).order_by('-created_at')
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

@login_required(login_url='admin_login')
def update_order_status(request, order_number):

    instance = get_object_or_404(Order, order_number = order_number)
    
    form = OrderStatusForm(request.POST or None, instance=instance)
    print(form) 
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request,'Order Status has been updated')
            return redirect('orders_list')
    else:  
        context = {
            'form': form,
            'order': instance,
            }
        return render(request, 'admin/orders/update_order_status.html',context)
    context = {
                'form': form,
                'order': instance,
                }
    return render(request, 'admin/orders/update_order_status.html',context)

# # charts
# def doughnut(request):
#     return render(request, 'admin/admin-home.html')



def trial(request):
    return render(request,'admin/Trial/Cropper.html')