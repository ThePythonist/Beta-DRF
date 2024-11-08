from django.urls import path
from .views import *

urlpatterns = [
    path('v1/stock/', StockView.as_view(), name='stock'),
]
