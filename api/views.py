from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import *
from .serializers import *
from .models import *


class StockView(ListCreateAPIView):
    """
    Get method : A stock info if it exists
    Post method : Not allowed
    """
    serializer_class = StockSerializer

    def get_queryset(self):
        student_name = self.request.GET.get('name', None)
        if student_name:
            return Stock.objects.filter(name__icontains=student_name)
        return Stock.objects.none()

    def post(self, request, *args, **kwargs):  # Can be used to override post method
        return Response({"status": "POST method is not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
