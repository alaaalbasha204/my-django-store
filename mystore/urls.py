from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.urls import path

urlpatterns=[

    path('', views.IndexView.as_view(), name='index'),
    path('detail/<int:product_id>',views.productdetail,name="detail"),
    path('cart',views.cart,name="cart"),
    path('signup',views.signup,name="signup"),
    path('login',views.login,name="login"),
    path('pay',views.methodpay,name="pay"),
    path('saveOrder',views.saveOrder,name="saveOrder")
] 
urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)