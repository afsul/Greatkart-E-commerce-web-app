from django.contrib import admin
from .models import  Address, Payment, Order, OrderProduct
# Register your models here.

class OrderProductInline(admin. TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0
    


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone', 'email', 'city', 'order_total', 'nett_paid','tax', 'status', 'is_ordered','coupon','coupon_use_status', 'created_at']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email','coupon_use_status']
    list_per_page = 20
    inlines = [OrderProductInline]
class AddressAdmin(admin.ModelAdmin):
     list_display = ['first_name', 'last_name', 'city', 'state']

admin.site.register(Payment)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderProduct)
admin.site.register(Address,AddressAdmin)