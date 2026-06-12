from django.shortcuts import render, redirect, get_object_or_404

from django.db.models import Q
from django.http import JsonResponse, HttpResponse
import random, hashlib
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from . models import Product, Category, Customer,Orders,ShoppingCart
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request,'index.html')
def about(request):
    return render(request,'about.html')


def productPage(request):
    if request.method == "POST":
        return redirect('product')
    else:
        category_id=request.GET.get('category')
        data = {}
        if category_id:
           products= Product.get_products_by_categoryid(category_id)
        else:
          products = Product.get_all_products()
        category = Category.get_all_category()
        data['products'] = products
        data['category'] = category
        return render(request, 'product.html', data)


def register(request):
    if request.method == 'POST':
        err=None
        name= request.POST.get('name')
        email = request.POST.get('email')
        passwd = request.POST.get('password')
        addr = request.POST.get('address')
        pin = request.POST.get('pincode')
        phone = request.POST.get('phone')
        gen = request.POST.get('gender')

        #Validation
        values={'name':name,
                'email':email,
                'addr':addr,
                'pin':pin,
                'phone':phone,
                'gen':gen,}
        customer = Customer(name=name, gender=gen, address=addr, pincode=pin, contactno=phone, emailaddress=email,
                            password=make_password(passwd))

        if not name.isalpha():
            err="Invalid Name, please try again"
        if not phone.isnumeric() or len(phone)<10:
            err="Invalid Contact Number, please try again"
        if not pin.isnumeric():
            err="Invalid Pincode, please try again"
        if customer.is_exists():
            err="Email Already Exists"
        data={}
        data['err']=err
        data['values']=values
        if err:
            return render(request, 'register.html',data)
        #customer.password=make_password(passwd)
        customer.save()
        myuser = User.objects.create_user(username=email,email=email, password=make_password(passwd))
        myuser.save()

        err = "You are registered! Try Logging in"
        return render(request, 'login.html',{'err':err})
    else:
        return render(request, 'register.html')

def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        myuser = authenticate(username=email, password=password)
        if myuser is not None:
            login(request, myuser)
            try:
                cart=ShoppingCart.objects.filter(customer=Customer.objects.get(emailaddress=request.user.username))
            except Exception as e:
                print(e)
                cart=[]
            request.session['cart']=len(cart)
            return redirect('user')
        else:
            msg="Incorrect Id or password"
            return render(request,'login.html',{'msg':msg})
    return render(request,'login.html')

@login_required(redirect_field_name='login')
def user(request):
    customer = Customer.get_customer_by_email(request.user.username)
    data={}
    if request.method=='POST':
        msg=None
        err=None
        current_password=request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if check_password(current_password, customer.password):
            if new_password==confirm_password:
                customer.password=new_password
                customer.save()
                myuser=User.objects.get(username=request.user.username)
                myuser.password=make_password(new_password)
                myuser.save()
                data['msg']='Password Changed successfully.'

            else:
                return render(request, 'changepass.html', {'err': 'New password and confirm password does not match'})
        else:
            return render(request,'changepass.html',{'err':'Incorrect Password'})
    data['customer']=customer
    return render(request,'user.html',data)

@login_required(redirect_field_name='login')
def orders(request):
    orders=Orders.objects.filter(customer=request.user.username).order_by('-order_date')
    return render(request,'orders.html',{'orders':orders})

@login_required(redirect_field_name='login')
def changepass(request):
    return render(request,'changepass.html')

def signout(request):
    logout(request)
    request.session.flush()
    return redirect('index')


@login_required(redirect_field_name='login')
def buynow(request):
    data={}
    if request.method=='GET':
        total=request.GET.get('total')
        if int(total) < 1:
            err="Total cannot be zero"
            return redirect('/mycart/?err='+err)
        method = "add_to_cart"
        customer = Customer.get_customer_by_email(request.user.username)
        cart=ShoppingCart.objects.filter(customer=customer)
        data['cart']=cart

    else:
        method = "buy_now"
        productid=request.POST.get('product')
        #print(productid)
        product=Product.get_product_by_id(productid)
        email=request.user.username
        customer=Customer.get_customer_by_email(email)
        data['product']=product
        data['customer']=customer
    data['method']=method
    return render(request,'confirm.html',data)

@login_required(redirect_field_name='login')
def checkout(request):
    if request.method=='GET':
        customer = Customer.get_customer_by_email(request.user.username)
        cart = ShoppingCart.objects.filter(customer=customer)
        for items in cart:
            order = Orders(customer=items.customer, product=items.product, quantity=items.quantity,
                           price=items.product.price, address=items.customer.address, pincode=items.customer.pincode)
            order.save()
        ShoppingCart.objects.filter(customer=Customer.get_customer_by_email(request.user.username)).delete()
        request.session['cart'] = 0

    else:
        product=Product.get_product_by_id(request.POST.get('productid'))
        customer =Customer.get_customer_by_email(request.POST.get('email'))
        quantity = request.POST.get('quantity')
        order=Orders(customer=customer,product=product,price=product.price,address=customer.address,pincode=customer.pincode,quantity=quantity)
        order.save()

    return render(request,'checkout.html')


@login_required(redirect_field_name='login')
def mycart(request):
    if request.method == "GET" and request.GET.get('flag') == "add_to_cart":
        category=request.GET.get('category')
        product = Product.objects.get(id=request.GET.get('product_id'))
        customer = Customer.get_customer_by_email(request.user.username)
        cart = ShoppingCart(customer=customer, product=product, quantity=1)
        cart.save()
        print(request.session.get('cart'))
        request.session['cart']=request.session.get('cart')+1
        msg="Product Added to Cart"
        #return render(request, 'product.html', {'msg':msg})
        return redirect('/product/?msg='+msg+'&category='+category)
    cart=ShoppingCart.objects.filter(customer=Customer.objects.get(emailaddress=request.user.username))
    total=sum([cartitem.product.price*cartitem.quantity for cartitem in cart])
    return render(request,'mycart.html',{'cart':cart,'total':total})

@login_required(redirect_field_name='login')
def update_cart(request):
    err=None
    if request.method=='POST':
        cart_item_id=request.POST.get('cart_item_id')
        quantity=request.POST.get('quantity')
        if int(quantity) > 0:
            cart=ShoppingCart.objects.get(id=cart_item_id)
            cart.quantity=quantity
            cart.save()
            return redirect('mycart')
        else:
            err="Quantity cannot be less than 1"
    elif request.method=='GET' and request.GET.get('cart_item'):
        cart_item_id=request.GET.get('cart_item')
        try:
            ShoppingCart.objects.get(id=cart_item_id).delete()
            request.session['cart'] = request.session.get('cart') -1
        except Exception as e:
            print(e)
            pass
    else:
        try:
            ShoppingCart.objects.filter(customer=Customer.get_customer_by_email(request.user.username)).delete()
            request.session['cart'] = 0
            err="Cart Empty"
        except Exception as e:
            pass
    if err:
        return redirect('/mycart/?err='+err)
    else:
        return redirect('/mycart/')

def product_list(request):
    query = request.GET.get('q', '').strip()
    products = []
    try:
        products = Products.objects.all()
        if query:
            products = products.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__icontains=query)
            )
    except Exception:
        products = []
    return render(request, 'products.html', {'products': products, 'query': query})

def order_search(request):
    query = request.GET.get('q', '').strip()
    orders = Orders.objects.all()
    if query:
        orders = orders.filter(
            Q(id__icontains=query) |
            Q(customer__name__icontains=query) |
            Q(status__icontains=query)
        )
    return render(request, 'orders.html', {'orders': orders, 'query': query})

def customer_search(request):
    query = request.GET.get('q', '').strip()
    customers = Customer.objects.all()
    if query:
        customers = customers.filter(
            Q(name__icontains=query) |
            Q(emailaddress__icontains=query) |
            Q(contactno__icontains=query)
        )
    return render(request, 'customers.html', {'customers': customers, 'query': query})

# OTP generation and verification (email)
def generate_email_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            return JsonResponse({'ok': False, 'error': 'Email required'}, status=400)
        code = f"{random.randint(100000,999999)}"
        h = hashlib.sha256(code.encode()).hexdigest()
        valid_until = timezone.now() + timezone.timedelta(minutes=10)
        otp_obj = OTP.objects.create(email=email, code_hash=h, valid_until=valid_until)
        # send email (console backend recommended in dev)
        subject = 'Your OTP Code'
        message = f'Your OTP code is {code}. It is valid for 10 minutes.'
        from_email = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'no-reply@example.com'
        try:
            send_mail(subject, message, from_email, [email], fail_silently=False)
        except Exception as e:
            # if email fails, still return ok for dev but include note
            pass
        return JsonResponse({'ok': True, 'message': 'OTP sent (if email configured).'})
    return JsonResponse({'ok': False, 'error': 'POST required'}, status=400)

def verify_email_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('code')
        if not email or not code:
            return JsonResponse({'ok': False, 'error': 'email and code required'}, status=400)
        otp_qs = OTP.objects.filter(email=email).order_by('-created')
        if not otp_qs.exists():
            return JsonResponse({'ok': False, 'error': 'OTP not found'}, status=404)
        otp = otp_qs.first()
        if otp.is_valid(code):
            return JsonResponse({'ok': True, 'message': 'OTP valid'})
        else:
            return JsonResponse({'ok': False, 'error': 'Invalid or expired OTP'}, status=400)
    return JsonResponse({'ok': False, 'error': 'POST required'}, status=400)

# Simple payment simulation (or Stripe if keys provided)
def create_payment(request):
    if request.method == 'POST':
        amount = float(request.POST.get('amount', 0))  # rupees
        # If stripe keys present, attempt to create PaymentIntent (user must set keys in settings)
        try:
            import stripe
            stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
            if stripe.api_key:
                intent = stripe.PaymentIntent.create(
                    amount=int(amount*100),
                    currency='inr',
                    metadata={'integration_check': 'accept_a_payment'}
                )
                return JsonResponse({'ok': True, 'client_secret': intent.client_secret})
        except Exception:
            # fallback to simulated payment
            pass
        return JsonResponse({'ok': True, 'message': 'Payment simulated (no stripe key).'})
    return JsonResponse({'ok': False, 'error': 'POST required'}, status=400)

# Live tracking: update driver location for an order (authenticate driver in production)
def update_driver_location(request, order_id):
    if request.method == 'POST':
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        try:
            order = Orders.objects.get(pk=order_id)
            order.driver_lat = lat
            order.driver_lng = lng
            order.save()
            return JsonResponse({'ok': True})
        except Orders.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Order not found'}, status=404)
    return JsonResponse({'ok': False, 'error': 'POST required'}, status=400)

def order_status_api(request, order_id):
    try:
        order = Orders.objects.get(pk=order_id)
        data = {
            'id': order.id,
            'status': order.status,
            'driver_lat': order.driver_lat,
            'driver_lng': order.driver_lng,
            'total_amount': str(order.total_amount)
        }
        return JsonResponse({'ok': True, 'order': data})
    except Orders.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Order not found'}, status=404)

def track_order_page(request, order_id):
    # A simple page that polls order_status_api and shows coordinates (frontend does map)
    return render(request, 'track_order.html', {'order_id': order_id})
