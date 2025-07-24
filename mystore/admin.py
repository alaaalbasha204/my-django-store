

from django.contrib import admin
from .models import Category, Product, Order, OrderItem ,Customer
admin.site.register(Customer)
admin.site.site_header='ALBAHSA CONTROL'
admin.site.site_title='CONTROL PAGE'
# هذا الكلاس يعرض المنتجات المرتبطة بالطلبية في صفحة الطلب
class OrderItemInline(admin.TabularInline):  # يمكنك استخدام StackedInline إن أردت شكل مختلف
    model = OrderItem
    extra = 0  # لا يعرض صفوف فارغة إضافية
    readonly_fields = ['product', 'quantity', 'total']

# هذا الكلاس يعرض الطلبية مع تفاصيل المنتجات
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'date', 'total_price_order']
    inlines = [OrderItemInline]


class ProductAdmin(admin.ModelAdmin):
    list_display=['name','price','category','quantitystock']
    list_display_links=['name']
    list_editable=['price','category','quantitystock']
    search_fields=['name']
    #list_filter=['category','price']
    list_filter=['category']


admin.site.register(Category)
admin.site.register(Product,ProductAdmin)
admin.site.register(Order, OrderAdmin)






# from django.contrib import admin
# from .models import Category, Product, Order, OrderItem

# # لعرض OrderItems داخل صفحة الطلب نفسه
# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     extra = 0  # لا تضف صفوف إضافية فارغة
#     readonly_fields = ('product', 'quantity', 'total')

# # تخصيص عرض Order في لوحة التحكم
# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('id', 'customer', 'date', 'total_price_order')
#     inlines = [OrderItemInline]

# # تسجيل باقي الموديلات بشكل طبيعي
# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('name',)

# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('name', 'price', 'category', 'quantitystock')

# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ('order', 'product', 'quantity', 'total')
