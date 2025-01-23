from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('top_smartwatches/', views.top_smartwatches, name='top_smartwatches'),
    path('seller_statistics/', views.seller_statistics, name='seller_statistics'),
    path('login/', views.login, name='login'),
    path('callback/', views.callback, name='callback'),
    path('logout/', views.logout, name='logout'),
]
