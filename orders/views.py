

from datetime import datetime
from multiprocessing import context
from traceback import print_tb
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from pytz import timezone
from accounts.models import UserProfile
from carts.models import CartItem
from coupon.forms import CouponApplyForm
from coupon.models import Coupon
from greatkart import settings
from greatkart.settings import RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY
from orders.models import Address, Order, OrderProduct, Payment
from store.models import Product
from .forms import OrderForm
import simplejson as json
from decimal import Decimal
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from paypal.standard.forms import PayPalPaymentsForm
from django.contrib import messages




# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))

@login_required
def place_order(request, total=0, quantity=0,):
    print('inside place order')

    import datetime
    try:
        address_id = request.POST['ship_address']
        
    except:
        messages.error(request,'Select a valid address')
        return redirect('checkout')
        
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <=0:
        return redirect('store')

    grand_total = 0
    tax         = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (5 * total)/100
    grand_total = total + tax 
    

    if request.method == 'POST':
        address_id = request.POST['ship_address']
        address = Address.objects.filter(id = address_id, user = request.user.id)
        order_note = request.POST['order_note']
        user = request.user
        for i in address:
            address_line_1 = i.address_line_1
            address_line_2 = i.address_line_2
            country = i.country
            state = i.state
            city = i.city
        # Store all the billing information inside Order table
        data = Order()
        data.user               = current_user
        data.first_name         = user.first_name
        data.last_name          = user.last_name
        data.phone              = user.phone_number
        data.email              = user.email
        data.address_line_1     = address_line_1
        data.address_line_2     = address_line_2
        data.country            = country
        data.state              = state
        data.city               = city
        data.order_note         = order_note
        data.order_total        = grand_total

        data.tax                = tax
        data.ip                 = request.META.get('REMOTE_ADDR')
        data.save()
        #Generate the order number

        yr                      = int(datetime.date.today().strftime('%Y'))
        dt                      = int(datetime.date.today().strftime('%d'))
        mt                      = int(datetime.date.today().strftime('%m'))
        d                       = datetime.date(yr,mt,dt)
        current_date            = d.strftime("%Y%m%d")
        order_number            = current_date + str(data.id)
        data.order_number       = order_number
        data.save()


        
        
       
        order = Order.objects.get(user = request.user,order_number= order_number,is_ordered = False)
        print('order found------>', order)
        code = order.coupon
        print(code,'checking coupon')
        from datetime import datetime   
        now = datetime.now()
        print('going to check coupon')
        try:
          
            coupon = Coupon.objects.get(code=code,active=True)

            print(coupon,'%$'*45)
            if coupon:
                    
                    discount = coupon.discount
                    order_no = order.order_number            
                    current_user = request.user
                    cart_items = CartItem.objects.filter(user = current_user)
                    grand_total = 0
                    tax = 0
                    total = 0
                    quantity = 0
                    for cart_item in cart_items:
                        total   += (cart_item.product.price * cart_item.quantity)
                        quantity += cart_item.quantity
                   
                    tax = round((5 * total)/100,2)
                    grand_total = round(total + tax,2)
                    discount_amount = round(grand_total * discount/100,2)
            print(discount_amount,'discount amount')
            total_after_coupon = round(float(grand_total - discount_amount),2)
            print(grand_total,'total')
            print(total_after_coupon,'amount after discount')
            
            order.discount_amount = discount_amount
            order.nett_paid = total_after_coupon
            order.coupon_use_status = True
            order.save()
        except Coupon.DoesNotExist:
            print("Entered to except"+"89"*45)
            order_no = order.order_number  
            current_user = request.user
            cart_items = CartItem.objects.filter(user = current_user)
            grand_total = 0
            tax = 0
            total = 0
            quantity = 0
            for cart_item in cart_items:
                total   += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity
            tax = round((5 * total)/100,2)
            grand_total = round(total + tax,2)
            order.nett_paid = grand_total
            order.coupon_use_status = False
            order.save()
           
                
               


        # Paypal
        host = request.get_host()
        paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': order.nett_paid,
        'item_name': 'Order {}'.format(order.id),
        'invoice': str(order.id),
        'currency_code': 'USD',
        'notify_url': 'http://{}{}'.format(host,
                                           reverse('paypal-ipn')),
        'return_url': 'http://{}{}'.format(host,
                                           reverse('order_complete')),
        'cancel_return': 'http://{}{}'.format(host,
                                              reverse('place_order')),
        }

        form = PayPalPaymentsForm(initial=paypal_dict)
        

        print("Entering to this view razorpa")
        amount = int(order.nett_paid  * 100)
        print(amount, "printed amount")
        client = razorpay.Client(auth = ("rzp_test_N9YYgyoIQNNsad" , "4WwWBrZdRQIc2PyicXlcHd5O"))
        print(client)
        payment = client.order.create({'amount':amount, 'currency':'INR', 'payment_capture':'1' })   
        print(payment)
       

 
       
    

        context = {
            'user':user,
            'order' : order,
            'cart_items' : cart_items,
            'total' : total,
            'tax' : tax,
            'grand_total' : grand_total,
            'form' : form,
            'payment':payment,
            'amount':amount

                }
        return render(request,'orders/payments.html',context)
    else:
        return redirect('checkout')


#COD
def cod_order_complete(request,order_number):
    print('entering cod complete')
    print(order_number)

    order_number = order_number

    
    order = Order.objects.get(user = request.user, is_ordered = False)
   
    try:
        code = order.coupon
        print(code,'coupon inside cod complete')
        from datetime import datetime
        now = datetime.now()
        try:
            print('cod checking whether coupon available')

            coupon = Coupon.objects.get(code=code)
            print('coupon available and this is the coupon -->', coupon)


            if coupon:
                discount = coupon.discount
                print('discount value',discount)
                order_no = order.order_number            
                current_user = request.user
                cart_items = CartItem.objects.filter(user = current_user)
                grand_total = 0
                tax = 0
                total = 0
                quantity = 0
                for cart_item in cart_items:
                    total   += (cart_item.product.price * cart_item.quantity)
                    # quantity += cart_item.quantity
            tax = round((5 * total)/100,2)
            grand_total = round(total + tax,2)
        
            discount_amount = round(grand_total * discount/100,2)
            print(discount_amount,'discount amount')
            total_after_coupon = round(float(grand_total - discount_amount),2)
            print(grand_total,'total')
            print(total_after_coupon,'amount after discount')
            order.discount_amount = discount_amount
            order.nett_paid = total_after_coupon
            order.coupon_use_status = True
            order.save()

            payment = Payment(
                user = request.user,
                payment_id = "COD - Payement pending",
                payment_method = "COD",
                amount_paid = order.nett_paid,
                status = "COD",
                )
            payment.save()
            order.payment= payment 
            order.is_ordered = True
            order.coupon_use_status = True
            order.save()
        except Coupon.DoesNotExist:
                order_no = order.order_number  
                current_user = request.user
                cart_items = CartItem.objects.filter(user = current_user)
                grand_total = 0
                tax = 0
                total = 0
                quantity = 0
                for cart_item in cart_items:
                    total   += (cart_item.product.price * cart_item.quantity)
                    quantity += cart_item.quantity
                tax = round((5 * total)/100,2)
                grand_total = round(total + tax,2)
                order.nett_paid = grand_total
                order.coupon_use_status = False
                order.save()
                payment = Payment(
                user = request.user,
                payment_id = "COD - Payement pending",
                payment_method = "COD",
                amount_paid = order.nett_paid,
                status = "COD",
                )
                payment.save()
                order.payment= payment 
                order.is_ordered = True
                order.coupon_use_status = False
                order.save()



        cart_items = CartItem.objects.filter(user = request.user)
        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            
            # qunatity decreaing on order
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        CartItem.objects.filter(user=request.user).delete()
        

        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        subtotal = 0
        for i in ordered_products:
            subtotal = subtotal + i.product_price * i.quantity

        tax = (subtotal * 5)/100
        grandtotal = subtotal + tax   
        payment = "Cash On Delivery"
        context = {
            'order' : order,
            'ordered_products' : ordered_products,
            'order_number': order.order_number,
            'payment':payment,
            'subtotal':subtotal,
            'tax':tax,
            'grandtotal':grandtotal,
        }
        return render(request, 'orders/order_complete.html' , context)
    
    except(Order.DoesNotExist):
        return redirect('home')

      
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        subtotal = 0
        for i in ordered_products:
            subtotal = subtotal + i.product_price * i.quantity

        tax = (subtotal * 5)/100
        grandtotal = subtotal + tax   

        payment = Payment.objects.get(payment_id = transID)
        context = {
            'order' : order,
            'ordered_products' : ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment':payment,
            'subtotal':subtotal,
            'tax':tax,
            'grandtotal':grandtotal,
        }
        return render(request, 'orders/order_complete.html' , context)

    except(Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')                        

def user_order_cancel(request,order):
    order = Order.objects.get(user = request.user, order_number = order)
    # print(order, 'this is the order')
    if request.method == "POST":
        status = request.POST['user_order_cancel']
        # print(status)
    
    order.status = status
    order.save()   
 
    return redirect('my_orders')


def user_order_return(request,order):
    order = Order.objects.get(user = request.user, order_number = order)
    # print(order, 'this is the order')
    if request.method == "POST":
        status = request.POST['user_order_return']
        # print(status)
    
    order.status = status
    order.save()

    return redirect('my_orders')
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))




