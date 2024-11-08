from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import *
from .serializers import *
from .models import *


class StockView(APIView):  # Using Serializers # Bobby
    def get(self, request):
        try:
            student_name = request.GET['name']
            student = Stock.objects.filter(stock_name__contains=student_name)

            data = StockSerializer(student, many=True).data
            return Response({"data": data}, status=status.HTTP_200_OK)

        except Exception as error:
            print(error)
            return Response({"status": "Internal Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        return Response({"status": "POST method is not allowed"}, status=status.HTTP_400_BAD_REQUEST)
