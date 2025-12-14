from django.urls import path
from . import views

app_name = 'fundraiser'

urlpatterns = [
    path('', views.home, name='home'),
]
