from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="ShopIndex"),
    path('about/', views.about, name="AboutUs"),
    path('contact/', views.contact, name="ContactUs"),
    path('tracker/', views.tracker, name="TrackingStatus"),
    path('search/', views.search, name="search"),
    path('productview/<int:myid>', views.prodView, name="ShopIndex"),
    path('checkout/', views.checkout, name="Checkout"),
    path('handlerequest/', views.handlerequest, name="HandleRequest"),
]
