from datetime import datetime
import datetime
from multiprocessing import context
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from carts.models import CartItem
from greatkart import settings
from greatkart.settings import RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY
from orders.models import Order, OrderProduct, Payment
from store.models import Product
from .forms import OrderForm
import json
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control
# Create your views here.
def billing_adrress(request):
    # current_user = request.user
    # if request.method == 'POST':
        form = OrderForm(request.POST)  
        # if form.is_valid():
        #     data = Order()
        #     data.user = current_user
        #     data.first_name =  form.cleaned_data['first_name']
        #     data.last_name =  form.cleaned_data['last_name']
        #     data.phone =  form.cleaned_data['phone']
        #     data.email =  form.cleaned_data['email']
        #     data.address_line_1 =  form.cleaned_data['address_line_1']
        #     data.address_line_2 =  form.cleaned_data['address_line_2']
        #     data.country =  form.cleaned_data['country']
        #     data.state =  form.cleaned_data['state']
        #     data.city =  form.cleaned_data['city']
        context ={
                'form':form,
            }
        return render(request, 'store/checkout.html', context)
    # return render(request, 'store/checkout.html')

def place_order(request, total=0, quantity=0,):
    current_user = request.user

    
    # if the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax


    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the building information inside order table
            data = Order()
            data.user = current_user
            data.first_name =  form.cleaned_data['first_name']
            data.last_name =  form.cleaned_data['last_name']
            data.phone =  form.cleaned_data['phone']
            data.email =  form.cleaned_data['email']
            data.address_line_1 =  form.cleaned_data['address_line_1']
            data.address_line_2 =  form.cleaned_data['address_line_2']
            data.country =  form.cleaned_data['country']
            data.state =  form.cleaned_data['state']
            data.city =  form.cleaned_data['city']
            data.order_total = grand_total
            data.tax  = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            #generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20220305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order' : order,
                'cart_items' : cart_items,
                'tax':tax,
                'total': total,
                'grand_total':grand_total,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')

def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    #store transaction details in payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],

    )
    payment.save()

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



#COD
def cod_order_complete(request,order_number):
    order_number = order_number
    order = Order.objects.filter(user = request.user, is_ordered = False)
    
    try:
        order = Order.objects.get(user = request.user, is_ordered = False, order_number = order_number)
        payment = Payment(
            user = request.user,
            payment_id = "COD - Payement pending",  
            payment_method = "COD",
            amount_paid = order.order_total,
            status = "COD",
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

def cancel_order(request, order_number):
    order = Order.objects.get(user = request.user, order_number = order_number)
    
    if request.method == "POST":
        status = request.POST['cancel_order']
        order_number.status = status
        order.save()   
        print('order cancelled')
    
    return redirect('my_orders')

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
@csrf_exempt
@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def proceed_payment(request):
    print("call received")
   
    order_id = request.POST['ord_no']
    print(order_id)
    
    

  
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

        # return render(request,'orders/proceed_payment.html',context)



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

        # #for variation - Many to Many field, first save data and then update.
        # cart_item = CartItem.objects.get(id = item.id)
        # product_variation = cart_item.variations.all()
        # orderproduct = OrderProduct.objects.get(id = orderproduct.id)
        # orderproduct.variations.set(product_variation)
        # orderproduct.save()
        
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

    
            


