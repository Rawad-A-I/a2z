from django.urls import path
from home.views import *

urlpatterns = [
    path('', redirect_homepage, name="redirect_homepage"),
    path('mart/', index, name="index"),
    path('bar/', a2z_bar, name='a2z_bar'),
    path('rayan/', rayan_brayan, name='rayan_brayan'),
    path('search/', product_search, name='product_search'),
    path('contact/', contact, name='contact'),
    path('about/', about, name='about'),
    path('terms-and-conditions/', terms_and_conditions, name='terms-and-conditions'),
    path('privacy-policy/', privacy_policy, name='privacy-policy'),
]
