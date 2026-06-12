
from django.urls import path, include
from . import views

urlpatterns = [
    path('', include('ossapp.urls')),

    path('products/', views.product_list, name='product_list'),
    path('orders/search/', views.order_search, name='order_search'),
    path('customers/search/', views.customer_search, name='customer_search'),
    path('otp/generate/', views.generate_email_otp, name='generate_email_otp'),
    path('otp/verify/', views.verify_email_otp, name='verify_email_otp'),
    path('payment/create/', views.create_payment, name='create_payment'),
    path('order/<int:order_id>/update-location/', views.update_driver_location, name='update_driver_location'),
    path('order/<int:order_id>/status/', views.order_status_api, name='order_status_api'),
    path('order/<int:order_id>/track/', views.track_order_page, name='track_order_page'),
]
