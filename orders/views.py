from datetime import datetime
import datetime
from multiprocessing import context
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from accounts.models import UserProfile
from carts.models import CartItem
from coupon.forms import CouponApplyForm
from coupon.models import Coupon
from greatkart import settings
from greatkart.settings import RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY
from orders.models import Address, Order, OrderProduct, Payment
from store.models import Product
from .forms import OrderForm
import json
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required


@login_required
def place_order(request, total=0, quantity=0,):
    try:
        address_id = request.POST['ship_address']
        
    except:
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
    form = CouponApplyForm()
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
        yr                      = int(datetime.date.today().strftime('%Y'))
        dt                      = int(datetime.date.today().strftime('%d'))
        mt                      = int(datetime.date.today().strftime('%m'))
        d                       = datetime.date(yr,mt,dt)
        current_date            = d.strftime("%Y%m%d")
        order_number            = current_date + str(data.id)
        data.order_number       = order_number
        data.save()


        order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
        user = request.user

       
    

        context = {
            'user':user,
            'order' : order,
            'cart_items' : cart_items,
            'total' : total,
            'tax' : tax,
            'grand_total' : grand_total,
                }
        return render(request,'orders/payments.html',context)
    else:
        return redirect('checkout')

   
           
    

            
def payments(request):
    body = json.loads(request.body)
    print(body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    #store transaction details in payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = body['paid_amount'],
        status = body['status'],

    )
    payment.save()
    order.nett_paid = body['paid_amount']
    order.payment = payment
    order.is_ordered = True
    order.save()

    #Move the cart items to Order Product table.
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct =  OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment =payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = request.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()


        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()


    # Clear cart
    CartItem.objects.filter(user=request.user).delete()
     # send order number and  transaction backto send data method via json Response
    data = {
            'order_number': order.order_number,
            'transID': payment.payment_id,
        }
    return JsonResponse(data)
def proceed_payment(request):
   
    order_id = request.POST['ord_no']
    # print(order_id)
    now = datetime.now()
    order = Order.objects.get(user = request.user, is_ordered = False, order_number = order_id)
    code = order.coupon
    # print(code,'- this is coupon.')
    # print(order)
    try:
        coupon = Coupon.objects.get(code__exact = code, valid_from__lte=now, valid_to__gte=now, active = True)
        if coupon:
            # print('coupon available',coupon)
            discount = coupon.discount
            # print(discount)
            order_no = order.order_number
            
            # print(order_no)
            # print('got order')
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
        
            discount_amount = grand_total * discount/100
            # print(discount_amount,'discount amount')
            total_after_coupon = round(float(grand_total - discount_amount),2)
            # print(grand_total,'total')
            # print(total_after_coupon,'amount after discount')
            order.discount_amount = discount_amount
            order.nett_paid = total_after_coupon
            order.coupon_use_status = True
            
            order.save()
            
            
            first_name = order.first_name
            last_name = order.last_name
            phone = order.phone
            email = order.email
            total = order.nett_paid * 100
            order_number = order.order_number
            # print(first_name,'first name')
            # print(total,'total')
            # print(order_number,"order number")

            

            data = { 
                "amount": total, 
                "currency": "INR", 
                "receipt": order_number,
                
                }
            
            payment = razorpay_client.order.create(data=data)
            context = {
                'payment':payment,
                'order':order,
                'total':total,
                'first_name' :first_name,
                'last_name' :last_name,
                'phone' :phone,
                'email' :email,
                "order_number":order_number,
                
            }
            
            # return render(request,'orders/proceed_payment.html',context)
            return JsonResponse({'payment':payment})
    except:
        # here is the else case
        order = Order.objects.get(user = request.user, is_ordered = False, order_number = order_id)
        first_name = order.first_name
        last_name = order.last_name
        phone = order.phone
        email = order.email
        total = order.order_total * 100
        order_number = order.order_number
        # print(first_name,'first name')
        # print(total,'total')
        # print(order_number,"order number")

        

        data = { 
            "amount": total, 
            "currency": "INR", 
            "receipt": order_number,
            
            }
        
        payment = razorpay_client.order.create(data=data)
        context = {
            'payment':payment,
            'order':order,
            'total':total,
            'first_name' :first_name,
            'last_name' :last_name,
            'phone' :phone,
            'email' :email,
            "order_number":order_number,
            
        }
        # print("***********",context)
        return JsonResponse({'payment':payment})

    
    
    


#COD
def cod_order_complete(request,order_number):
    order_number = order_number

    now = datetime.now()
    order = Order.objects.filter(user = request.user, is_ordered = False)
    code = order.coupon
    try:
        order = Order.objects.get(user = request.user, is_ordered = False)
        code = order.coupon
        # print(code,'checking coupon')
        coupon = Coupon.objects.get(code__exact = code, valid_from__lte=now, valid_to__gte=now, active = True)
        # print('coupon available')
        if coupon:
            # print('coupon available',coupon)
            discount = coupon.discount
            # print(discount)
            order_no = order.order_number            
            # print(order_no)
            # print('got order')
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
            # print(discount_amount,'discount amount')
            total_after_coupon = round(float(grand_total - discount_amount),2)
            # print(grand_total,'total')
            # print(total_after_coupon,'amount after discount')
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

            # cart_item = CartItem.objects.get(id = item.id)
            # product_variation = cart_item.variations.all()
            # orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            # orderproduct.variations.set(product_variation)
            # orderproduct.save()

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

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def rzp_order_complete(request):
    # print("payment completed and saving")
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    # print(order_number,"- order No &", transID, "- Trans ID")
    order = Order.objects.get(user = request.user, is_ordered = False, order_number = order_number)
    # print(order)
    payment = Payment(
        user = request.user,
        payment_id = transID,
        payment_method = "Razor Pay",
        amount_paid = order.order_total,
        status = "COMPLETED",
        )
    payment.save()
    order.payment= payment 
    order.is_ordered = True
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
        
    # reduce the quantity of sold products
        product = Product.objects.get(id = item.product_id)
        product.stock -= item.quantity
        product.save()

    # clear the cart and send order received confirmation to customer
    CartItem.objects.filter(user=request.user).delete()
    
    try:
        # print("trying order ID")
        order = Order.objects.get(order_number = order_number)
        # print("fetched order ")
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        subtotal = 0
        for i in ordered_products:
            # prod_total = i.product_price * i.quantity
            subtotal += i.product_price * i.quantity


        # payment = Payment.objects.get(payment_id = transID)

        context = {
            # 'prod_total': prod_total,
            'order':order,
            'ordered_products' : ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal':subtotal,
        }
        CartItem.objects.filter(user=request.user).delete()
        return render(request, 'orders/order_complete.html',context)


    except (Payment.DoesNotExist, Order.DoesNotExist):

        # print("payment feedback not received. exiting without saving")
        return redirect('home')

    
            


