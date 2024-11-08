from django.urls import path
from .views import *

urlpatterns = [
    path('v1/beta/', BetaView.as_view(), name='stock'),
]
