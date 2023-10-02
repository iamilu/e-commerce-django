from django.shortcuts import render, redirect, HttpResponseRedirect
from .models import *
from django.http import JsonResponse
import json
import datetime

# Create your views here.

from django.views import View
from django.contrib.auth.hashers import make_password, check_password
import random
from django.conf import settings
from django.core.mail import send_mail

def test(request):
    a = request.user
    return JsonResponse(str(a), safe=False)

def store(request):
    products = Product.objects.all()
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, is_complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_items':0, 'get_cart_total':0}
        cartItems = order['get_cart_items']
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, is_complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_items':0, 'get_cart_total':0}
        cartItems = order['get_cart_items']

    context = {'items': items, 'order':order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, is_complete=False)
        # try:
        #     order = Order.objects.get(customer=customer, is_complete=False)
        # except Order.DoesNotExist:
        #     order = Order.objects.create(customer=customer)
        items = order.orderitem_set.all()
        # items = OrderItem.objects.all(order)
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_items':0, 'get_cart_total':0, 'shipping': False}
        cartItems = order['get_cart_items']

    context = {'items': items, 'order':order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body) #POST data coming to backend from cart.js using fetch api
    #need to convert it to a dict object as POST data is coming as a string
    productId = data.get('productId')
    action = data.get('action')
    print(productId, action)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, is_complete=False)
    orderItem, created = OrderItem.objects.get_or_create(product=product, order=order)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    data = json.loads(request.body)
    userInfo = data.get('userInfo')
    shippingInfo = data.get('shippingInfo')
    print(userInfo, shippingInfo)

    transaction_id = datetime.datetime.now().timestamp()
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, is_complete=False)
        total = float(data['userInfo']['total'])
        order.transaction_id = transaction_id

        if total == round(order.get_cart_total,2):
            order.is_complete = True
        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order = order,
                address = data['shippingInfo']['address'],
                city = data['shippingInfo']['city'],
                zipcode = data['shippingInfo']['zipcode'],
                state = data['shippingInfo']['state'],
                country = data['shippingInfo']['country'],
            )
    else:
        print('user is not logged in...')
    return JsonResponse('Payment submitted', safe=False)

def send_email_to_user(username=None, otp=None, email=None):
    subject = 'Welcome to our E-Commerce Store'
    message = '''Hello {0}, 
                    Greetings and welcome to our E-Commerce Store.
                    For sign up, you need to use OTP is {1}.
                    We are delighted to onboard you'''.format(username.capitalize(),int(otp))
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    print(email_from, recipient_list)
    send_mail(subject, message, email_from, recipient_list, fail_silently=True)
    Sendmail.objects.create(send_to=email, subject=subject, message=message).save()

class Signup (View):
    def get(self, request):
        return render (request, 'store/signup.html')

    def post(self, request):
        postData = request.POST
        first_name = postData.get ('firstname')
        last_name = postData.get ('lastname')
        phone = postData.get ('phone')
        email = postData.get ('email')
        password = postData.get ('password')
        confirm_password = postData.get ('confirmpassword')
        otp = postData.get ('otp')
        # validation
        value = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'email': email,
            'password': password
        }
        error_message = None

        customer = NewUser (first_name=first_name,
                             last_name=last_name,
                             phone=phone,
                             email=email,
                             password=password)
        error_message = self.validateCustomer (customer)

        new_user = User(email=email, password=password, username=first_name)

        if password != confirm_password:
            error_message = 'Password is not matching, please re-enter'

        if not error_message:
            print (first_name, last_name, phone, email, password)
            customer.password = make_password (customer.password)
            if not otp:
                new_otp = random.randrange(1000, 9999)
                try:
                    print(first_name, new_otp, email)
                    send_email_to_user(first_name, new_otp, email)
                except:
                    data = {
                        'error': 'Fail to send OTP to the registered email address',
                        'values': value
                    }
                    return render (request, 'store/signup.html', data)
                Otp.objects.create(email=email, otp=new_otp).save()
                data = {
                    'otp': True,
                    'error': 'OTP is sent to your registered email address, please enter otp',
                    'values': value
                }
                return render (request, 'store/signup.html', data)
            else:
                try:
                    otp_obj = Otp.objects.get(email=email)
                except:
                    pass
                if int(otp_obj.otp) != int(otp):
                    data = {
                        'otp': True,
                        'error': 'Please enter correct OTP',
                        'values': value
                    }
                    return render (request, 'store/signup.html', data)
                customer.register()
                new_user.save()
                print (first_name, last_name, phone, email, password)
                return redirect ('login')
        else:
            data = {
                'error': error_message,
                'values': value
            }
            return render (request, 'store/signup.html', data)

    def validateCustomer(self, customer):
        error_message = None
        if (not customer.first_name):
            error_message = "Please Enter your First Name !!"
        elif len (customer.first_name) < 3:
            error_message = 'First Name must be 3 char long or more'
        elif not customer.last_name:
            error_message = 'Please Enter your Last Name'
        elif len (customer.last_name) < 3:
            error_message = 'Last Name must be 3 char long or more'
        elif not customer.phone:
            error_message = 'Enter your Phone Number'
        elif len (customer.phone) < 10:
            error_message = 'Phone Number must be 10 char Long'
        elif len (customer.password) < 5:
            error_message = 'Password must be 5 char long'
        elif len (customer.email) < 5:
            error_message = 'Email must be 5 char long'
        elif customer.isExists ():
            error_message = 'Email Address Already Registered..'
        # saving

        return error_message

class Login(View):
    return_url = None

    def get(self, request):
        Login.return_url = request.GET.get ('return_url')
        return render (request, 'store/login.html')

    def post(self, request):
        email = request.POST.get ('email')
        password = request.POST.get ('password')
        customer = NewUser.get_customer_by_email (email)
        error_message = None
        print(customer.password)
        if customer:
            flag = check_password (password, customer.password)
            print(flag)
            if flag:
                request.session['customer'] = customer.id
                print(request.session['customer'])
                if Login.return_url:
                    return HttpResponseRedirect (Login.return_url)
                else:
                    Login.return_url = None
                    return redirect ('store')
            else:
                error_message = 'Please enter correct password'
        else:
            error_message = 'Please enter valid email address'

        print (email, password)
        return render (request, 'store/login.html', {'error': error_message})

def logout(request):
    request.session.clear()
    return redirect('login')