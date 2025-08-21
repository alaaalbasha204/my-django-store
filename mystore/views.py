from pyexpat.errors import messages
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render ,redirect
from .models import Category,Product,Order,OrderItem,Customer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from decouple import config, Csv
import requests
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from .forms import SignUpForm ,LoginForm
from django.views import View
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.db.models import Q 
from .models import Customer
from django.views.decorators.csrf import csrf_protect
from django.utils.html import escape
from django.core.cache import cache
# def ratelimit_exceeded_view(request, exception=None):
#     return JsonResponse(
#         {'error': '📛 تم تجاوز الحد المسموح به من الطلبات. الرجاء الانتظار قليلاً والمحاولة مجددًا.'},
#         status=429
#     )
@method_decorator(ratelimit(key='ip', rate='20/m', method='POST', block=True), name='dispatch')
class IndexView(View):

    valid_categories = ['clothes', 'food', 'kitchin','elctronic']

    def get_all_products_cached(self):
        """جلب المنتجات من الكاش أو من قاعدة البيانات"""
        products = cache.get('all_products')
        if products is None:
            products = (Product.objects.all())
            cache.set('all_products', products, 60)  # نخزنها 60 ثانية
        return products
    
    def get_category_products_cached(self, category):
      cache_key = f'category_products_{category}'
      products = cache.get(cache_key)
      if products is None:
        products = (Product.objects.filter(category__name=category))
        cache.set(cache_key, products, 60)  # نخزنها 60 ثانية
      return products

    def get(self, request):

        query = request.GET.get('q')
        products = self.get_all_products_cached()
        category = request.GET.get('category') # جلب التصنيف من الرابط

        if category in self.valid_categories:
         products = self.get_category_products_cached(category)
        else:
           products = self.get_all_products_cached()
      
        if query:
           products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        cart = request.session.get('cart', {})
        cart_product_ids = list(map(int, cart.keys()))
        category_pro=set()

        for x in products:
            category_pro.add(x.category)
        context = {
            'category':category_pro,#Category.objects.all(),
            'products': products,
            'cart': cart,
            'cart_product_ids': cart_product_ids,
            'search_query': query or ''
        }
        return render(request, 'index.html', context)

    def post(self, request):

        cart = request.session.get('cart', {})
        product_id = request.POST.get('product')
        remove = request.POST.get('remove') is not None

        try:
            product_obj = Product.objects.get(id=product_id)
        except (TypeError, ValueError, Product.DoesNotExist):
            messages.error(request, "❌ هذا منتج غير موجود.")
            return redirect('index')

        quantity = cart.get(product_id, 0)
        if remove:
            if quantity <= 1:
                cart.pop(product_id, None)
                messages.info(request, f"🗑️ تمت إزالة {product_obj.name} من السلة.")
            else:
                cart[product_id] = quantity - 1
                messages.info(request, f"➖ تم تقليل الكمية من {product_obj.name}.")
        else:
            if quantity >= product_obj.quantitystock:
                messages.warning(request, "⚠️ الكمية المطلوبة غير متوفرة في المخزون.")
                return redirect('index')
            if quantity >= 12:
                messages.warning(request, "⚠️ الحد الأقصى للكمية هو12 .")
                return redirect('index')
            
            cart[product_id] = quantity + 1 if quantity else 1
            messages.success(request, f"✅ تم إضافة {product_obj.name} إلى السلة.")

        request.session['cart'] = cart
        request.session.modified = True
        return redirect('index')


def productdetail(request,product_id):

    try:
        product_id = int(product_id)
    except (ValueError, TypeError):
        return HttpResponseBadRequest("Invalid product ID.")
    product=Product.objects.get(id=product_id)
    context={
        'product':product,
    
    }
    return render(request,"productdetail.html",context)



def cart(request):
    cart = request.session.get('cart', {})

    try:
        product_ids = [int(id) for id in cart.keys() if id.isdigit()]
    except ValueError:
        product_ids = []

    if len(product_ids) > 12 :
           messages.error(request, "لا يمكن إضافة أكثر من 12 منتج في السلة.")
           return HttpResponseBadRequest("عدد المنتجات كبير.")

    products = Product.objects.filter(id__in=product_ids)    
    cart_items = []
    total=0

    for product in products:
        
        try:
            quantity = int(cart.get(str(product.id), 0))
        except (ValueError, TypeError):
            messages.warning(request, f"⚠️ الكمية غير صالحة لمنتج {product.name}.")
            continue

        if quantity < 0 or quantity > 12:
            messages.warning(request, f"⚠️ تم تجاهل {product.name} بسبب كمية غير صالحة: {quantity}.")
            continue
            #MESSAGEEEEEE_________________-
        cart_items.append({
            'product': product,
            'quantity': cart.get(str(product.id), 0)  # Use str because session keys are strings
        })
        total+=int(product.price*int(cart.get(str(product.id))))

    return render(request, 'cart.html', {'cart_items': cart_items,'total':total})



def signup(request):
    #form = SignUpForm(request.POST or None)
    if request.method == 'POST':
        form = SignUpForm(request.POST or None)
        if form.is_valid():
            user=form.save()
            user.set_password(form.cleaned_data['password'])  
            user.save()
            Customer.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address']
            )
            messages.success(request, "✅ تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.")
            return redirect('cart') 
        else :
           messages.error(request, "❌ هناك خطأ في البيانات. يرجى التحقق.")
           return render(request, 'signup.html', {'form': form})
    else :
        form = SignUpForm()


    return render(request, 'signup.html', {'form': form})


        
def login(request):
    form = LoginForm(request.POST or None)
    error = None

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                request.session.set_expiry(1800)  # الجلسة تنتهي بعد ساعة
                messages.success(request, f"✅ مرحبًا {user.username}! تم تسجيل الدخول بنجاح.")
                return redirect('cart')
            else:
               messages.error(request, "❌ اسم المستخدم أو كلمة المرور غير صحيحة.")
 
   

    return render(request, 'login.html', {'form': form})



@login_required(login_url='login')
def methodpay(request):
    if not request.user.is_authenticated:
        return redirect('login')

    session_cart = request.session.get('cart', {})
    if not session_cart:
        messages.warning(request, "🛒 السلة فارغة، الرجاء إضافة منتجات قبل المتابعة.")
        return redirect('cart') 

    return render(request,'methodpay.html')



@login_required(login_url='login')

def saveOrder(request):


    user = request.user
    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, "🛒 السلة فارغة، لا يمكن إنشاء الطلب.")
        return redirect('cart')

    total_price_order = 0
    order = Order.objects.create(customer=user, total_price_order=0)

    order_lines = []  # 📦 هنا نجمع تفاصيل كل منتج في الطلب

    for product_id_str, quantity in cart.items():
        try:
            product_id = int(product_id_str)
            quantity = int(quantity)
            if quantity <= 0 or quantity > 12:
                raise ValueError("كمية غير صالحة.")
        except (ValueError, TypeError):
            messages.error(request, "❌ هناك خطأ في السلة.")
            return redirect('cart')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            messages.error(request, f"❌ المنتج برقم {product_id} غير موجود.")
            return redirect('cart')

        if product.quantitystock < quantity:
            messages.warning(request, f"⚠️ الكمية المطلوبة من {product.name} غير متوفرة.")
            return redirect('cart')

        total = product.price * quantity
        OrderItem.objects.create(order=order, product=product, quantity=quantity, total=total)

        product.quantitystock -= quantity
        product.save()

        total_price_order += total

        # ✅ أضف سطر المنتج إلى تفاصيل الطلب
        order_lines.append(f"📦 {product.name} × {quantity} = {total} دينار")

    order.total_price_order = total_price_order
    order.save()

    request.session['cart'] = {}

    # ✅ تجهيز رسالة واحدة شاملة
    BOT_TOKEN = config('BOT_TOKEN')
    CHAT_ID = config('CHAT_ID')
    customer=Customer.objects.get(user=user)

    message = (
        f"🛒 طلب جديد من المستخدم: {escape(user.username)}\n\n"
        + "\n".join(order_lines) +
        f"\n\n💰 المجموع الكلي: {total_price_order} دينار"
        +f"\n \n 🏠 العنوان :{customer.address}"
        +f"\n \n  📞 الهاتف :{customer.phone}"
    )

    send_telegram_message(BOT_TOKEN, CHAT_ID, message)

    messages.success(request, "✅ تم إنشاء الطلب بنجاح!")
    return redirect('index')

def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message
    }
    requests.post(url, data=payload)

