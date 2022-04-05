from django.shortcuts import render
from coupon.models import CategoryOffer, ProductOffer
from store.models import Product
from datetime import timezone
from datetime import datetime



def home(request):
    now = datetime.now()
    products    = Product.objects.all().filter(is_available=True).order_by('created_date')
    
    for product in products:
        p_offer = 0
        c_offer = 0
        prod_id = product.id
        try:
            prod_offer = ProductOffer.objects.get(product_id = product, valid_from__lte=now, valid_to__gte=now, is_active = True)
            p_offer = prod_offer.discount
            
            
        except:
            pass
        
        try:
            categ_offer = CategoryOffer.objects.get(category_id = product.category,valid_from__lte=now, valid_to__gte=now, is_active = True)
            c_offer = categ_offer.discount
            
        except:
            pass

        if p_offer > c_offer:
            disc_price = product.mrp_price - (product.mrp_price * p_offer)/100
            product.price = round(disc_price, 2)
            product.discount_percentage = p_offer
            product.save()
        elif p_offer < c_offer:
            disc_price = product.mrp_price - (product.mrp_price * c_offer)/100
            product.price = round(disc_price,2)
            product.discount_percentage = c_offer
            product.save()
            
        elif p_offer == c_offer and p_offer !=0 :
       
            disc_price = product.mrp_price - (product.mrp_price * p_offer)/100
            product.discount_percentage = p_offer
            product.price = round(disc_price,2)
            product.save()

        elif p_offer == c_offer == 0:
            product.price = product.mrp_price
            product.save()
        
    
    # reviews = ReviewRating.objects.filter(product_id = prod_id, status = True)

    context     = {
        'products': products,
    }
    return render(request, 'home.html',context)
