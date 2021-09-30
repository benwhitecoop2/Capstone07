from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='Home'),
    path('1/', views.img1, name='Img1'),
    path('2/', views.img1, name='Img2'),
    path('3/', views.img1, name='Img3'),
    path('4/', views.img1, name='Img4'),
]
