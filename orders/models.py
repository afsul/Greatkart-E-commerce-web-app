from django.db import models
from accounts.models import Account
from coupon.models import Coupon
from store.models import Product

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.deletion import SET_NULL

# Create your models here.
class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return self.payment_id
class Address(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=12, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    address_line_1 = models.CharField(max_length=100,  blank=True, null=True)
    address_line_2 = models.CharField(max_length=100, blank=True, null=True)
    city            = models.CharField(max_length=50)
    district        = models.CharField(max_length=501)
    country            = models.CharField(max_length=50)
    state           = models.CharField(max_length=50)
    country         = models.CharField(max_length=50, blank=True, null=True)
    pincode         = models.CharField(max_length=10,blank=True, null=True) 

    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    def  full_name(self):
        return f'{self.first_name} {self.last_name}'
        
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'
class Order(models.Model):

    STATUS = (
        ('New','New'),
        ('Accepted','Accepted'),
        ('Order Shipped','Order Shipped'),
        ('Order Out for Delivery','Order Out for Delivery'),
        ('Order Delivered','Order Delivered'),
        ('Return','Return'),
        ('Return collected','Return collected'),
        ('Cancelled','Cancelled'),
        
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=30)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=50, choices=STATUS, default='New')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    coupon = models.ForeignKey(Coupon,null=True,on_delete=SET_NULL, blank=True)
    coupon_use_status= models.BooleanField(default=False)
    discount_amount = models.FloatField(null=True,blank=True)
    nett_paid  = models.FloatField(null=True,blank=True)
    discount   = models.IntegerField(default=0,validators=[MinValueValidator(0),MaxValueValidator(100)])


    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
        return self.first_name
    def __unicode__(self):
        return self.order_number

        
class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name

