from django.conf import settings
#from django.core.cache.backends.base import DEFAULT_TIMEOUT
#from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import JsonResponse
from store.forms import ReviewForm
from django.contrib import messages
from .models import *
from .utils import cookieCart,cartData, guestOrder
import datetime
import json


# Create your views here.
#CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

#@cache_page(CACHE_TTL)
def store(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)

def cart(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)


#@login_required(login_url="../users/login")
def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	Countrys = Country.objects.all()
	context = {'items':items, 'order':order, 'cartItems':cartItems,'countrys':Countrys}
	return render(request, 'store/checkout.html', context)

def product_details(request,product_id):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	product_details = Product.objects.get(id=product_id)
	#colors=ProductAttribute.objects.filter(product=product_id).values('color__id','color__title').distinct()
	sizes = ProductAttribute.objects.filter(product=product_id).values('size__id','size__title').distinct()
	if request.user.is_authenticated:
		try:
			orderproduct = OrderItem.objects.filter(order__customer__user=request.user, product_id=product_id).exists()
		except Order.DoesNotExist:
			orderproduct = None
	else:
		orderproduct = None

	# Get the reviews
	reviews = ProductReview.objects.filter(product_id=product_id)

	context = {'product_details':product_details,'order':order, 'cartItems':cartItems,'reviews':reviews,'orderproduct':orderproduct,'sizes':sizes}
	return render(request, 'store/product_details.html',context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)
	#import pdb;
	#pdb.set_trace()
	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def reviewAdd(request,product_id):
	url = request.META.get('HTTP_REFERER') 
	if request.method == 'POST':
		try:
			reviews = ProductReview.objects.get(user__id=request.user.id, product__id=product_id)
			form = ReviewForm(request.POST, instance=reviews)
			form.save()
			messages.success(request, 'Thank you! Your review has been.')
			return redirect(url)
		except ProductReview.DoesNotExist:
			form = ReviewForm(request.POST)
			if form.is_valid():
				data = ProductReview()
				data.rating = form.cleaned_data['rating']
				data.comment = form.cleaned_data['comment']
				data.product_id = product_id
				data.user_id = request.user.id
				data.save()
				messages.success(request, 'Thank you! Your review has been.')
				return redirect(url)

def search(request):
	q=request.GET['q']
	data=Product.objects.filter(name__icontains=q).order_by('-id')
	return render(request,'store/search.html',{'data':data})

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		
	else:
		customer,order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == float(order.get_cart_total):
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=State.objects.get(id=data['shipping']['state']),
		country=Country.objects.get(id=data['shipping']['country']),
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)

# AJAX
def load_states(request):
	country_id = request.GET.get('country_id')
	states = State.objects.filter(country_id=country_id).all()
	return render(request, 'store/states_list.html', {'states': states})
