from itertools import product
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from carts.models import CartItem
from store.models import Product, ProductGallery
from category.models import Category
from carts.views import _cart_id


# Create your views here.

def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug = category_slug)
        products   = Product.objects.filter(category=categories, is_available=True)
        product_count =products.count()
        print(products)

    else:
        products = Product.objects.all().filter(is_available=True)
        product_count = products.count()
        print(products)
        
    context ={
        'products': products,
        'product_count':product_count,
    }
    
    return render(request, 'store/store.html',context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), product=single_product).exists()
    except Exception as e:  
        raise e
    #get product gallery
    product_gallery = ProductGallery.objects.filter(product_id = single_product.id)

    context ={'single_product': single_product,
              'in_cart'       : in_cart,
              'product_gallery':product_gallery,
    }
   
    return render(request, 'store/product_detail.html', context)


