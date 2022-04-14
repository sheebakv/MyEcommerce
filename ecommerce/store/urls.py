from django.urls import path
from . import views

urlpatterns = [

	#Leave as empty string for base url
	path('', views.store, name="store"),
	path('store/search', views.search, name="search"),
	path('store',views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
	path('product/<product_id>',views.product_details,name='product_details'),
	path('update_item/', views.updateItem, name="update_item"),
	path('review/<product_id>',views.reviewAdd,name="review"),

]

