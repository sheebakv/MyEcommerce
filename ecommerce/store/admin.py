from django.contrib import admin
from .models import *

admin.site.register(Customer)
admin.site.register(Color)
admin.site.register(Size)
class ProductAdmin(admin.ModelAdmin):
    list_display=('id','name','price')
admin.site.register(Product,ProductAdmin)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display=('id','product','color','size')
admin.site.register(ProductAttribute,ProductAttributeAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(ShippingAddress)
admin.site.register(ProductReview)

