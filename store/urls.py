from django.contrib.auth import logout
from django.urls import path
from . import views

urlpatterns = [
  path('', views.store, name="store"),
  path('login/', views.login_user, name="login"),
  path('register/', views.register_user, name="register"),
  path('logout/', views.logout_user, name="logout"),
  path('cart/', views.cart, name="cart"),
  path('checkout', views.checkout, name="store"),
  path('update_item/', views.update_item, name="update_item"),
  path('process_order/', views.process_order, name="process_order"),
]