from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import JsonResponse
from store.forms import ReviewForm
from django.contrib import messages
from .models import * 
import json


# Create your views here.

def store(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		#Create empty cart for now for non-logged in user
		items = []
		order = {'get_cart_total':0, 'get_cart_items':0,'shipping':False}
		cartItems = order['get_cart_items']

	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)

def cart(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		#Create empty cart for now for non-logged in user
		items = []
		order = {'get_cart_total':0, 'get_cart_items':0,'shipping':False}
		cartItems = order['get_cart_items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)


#@login_required(login_url="../users/login")
def checkout(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		#Create empty cart for now for non-logged in user
		items = []
		order = {'get_cart_total':0, 'get_cart_items':0,'shipping':False}
		cartItems = order['get_cart_items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def product_details(request,product_id):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		#Create empty cart for now for non-logged in user
		items = []
		order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
		cartItems = order['get_cart_items']

	product_details = Product.objects.get(id=product_id)
	if request.user.is_authenticated:
		try:
			orderproduct = OrderItem.objects.filter(order__customer__user=request.user, product_id=product_id).exists()
		except Order.DoesNotExist:
			orderproduct = None
	else:
		orderproduct = None

	# Get the reviews
	reviews = ProductReview.objects.filter(product_id=product_id)

	context = {'product_details':product_details,'order':order, 'cartItems':cartItems,'reviews':reviews,'orderproduct':orderproduct}
	return render(request, 'store/product_details.html',context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']

	customer = request.user.customer
	print(customer)
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
	print(request)
	if request.method == 'POST':
		try:
			reviews = ProductReview.objects.get(user__id=request.user.id, product__id=product_id)
			form = ReviewForm(request.POST, instance=reviews)
			form.save()
			messages.success(request, 'Thank you! Your review has been updated.')
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
				messages.success(request, 'Thank you! Your review has been submitted.')
				return redirect(url)

def search(request):
	q=request.GET['q']
	data=Product.objects.filter(name__icontains=q).order_by('-id')
	return render(request,'store/search.html',{'data':data})

