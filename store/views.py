from django.shortcuts import redirect, render
from .models import *
from django.http import JsonResponse
import json
import datetime
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib import messages
from .forms import *
# Create your views here.

def login_user(request):
  if request.method == 'POST':
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
      login(request, user)
      messages.success(request, ('You have been logged in'))
      return redirect('store')
    else:
      messages.success(request, ('Error Logging In - Please Try Again...'))
      return redirect('login')
  else:
    return render(request, 'store/login.html')

def logout_user(request):
  logout(request)
  messages.success(request, ('You Have Been Logged Out...'))
  return redirect('store')

def register_user(request):
  if request.method == 'POST':
    form = SignUpForm(request.POST)
    if form.is_valid():
      form.save()
      username = form.cleaned_data['username']
      password = form.cleaned_data['password1']
      user = authenticate(username=username, password=password)
      login(request, user)
      messages.success(request, ('You Have Registered...'))
      return redirect('store')
  else:
    form = SignUpForm()
  
  context = {'form' : form}
  return render(request, 'store/register.html', context)

def store(request):
  if request.user.is_authenticated:
	  customer = request.user.customer
	  order, created = Order.objects.get_or_create(customer=customer, complete=False)
	  items = order.orderitem_set.all()
	  cartItems = order.get_cart_items
  else:
	  items = []
	  order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
	  cartItems = order['get_cart_items']

  products = Product.objects.all()
  context = {'products':products, 'cartItems' : cartItems}
  return render(request, 'store/store.html', context)

def cart(request):
  if request.user.is_authenticated:
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    items = order.orderitem_set.all()
    cartItems = order.get_cart_items
  else:
    items = []
    order = {'get_cart_total':0, 'get_cart_items': 0, 'shipping':False}
    cartItems = order['get_cart_items']

  context = {'items': items, 'order': order, 'cartItems':cartItems}
  return render(request, 'store/cart.html', context)

def checkout(request):
  if request.user.is_authenticated:
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    items = order.orderitem_set.all()
    cartItems = order.get_cart_items
  else:
    items = []
    order = {'get_cart_total':0, 'get_cart_items': 0, 'shipping':False}
    cartItems = order['get_cart_items']
  context = {'items': items, 'order': order, 'cartItems':cartItems}
  return render(request, 'store/checkout.html', context)

def update_item(request):
  data = json.loads(request.body)
  productId = data['productId']
  action = data['action']
  print('Action: ', action)
  print('Product: ', productId)

  customer = request.user.customer
  product = Product.objects.get(id=productId)
  order, created = Order.objects.get_or_create(customer=customer, complete=False)
  orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

  if action == 'add':
    orderItem.quantity = (orderItem.quantity + 1)
  elif action == 'remove': 
    orderItem.quantity = (orderItem.quantity - 1)  
  
  orderItem.save()
  if orderItem.quantity <= 0:
    orderItem.delete()

  return JsonResponse('Item was added', safe=False)


def process_order(request):
  transaction_id = datetime.datetime.now().timestamp()
  data = json.loads(request.body)

  if request.user.is_authenticated:
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
      order.complete = True
    order.save()

    if order.shipping == True:
      ShippingAddress.objects.create(
        customer=customer,
        order=order,
        address=data['shipping']['address'],
        city=data['shipping']['city'],
        state=data['shipping']['state'],
        zip_code=data['shipping']['zipcode'],
      )
    else:
      print('log in')

  return JsonResponse('Payment submitted..', safe=False)