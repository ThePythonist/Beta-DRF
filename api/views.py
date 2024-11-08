# from rest_framework.views import APIView
import os

from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import *
from .serializers import *
from .models import *
from .scrape import *
from .logging_conf import make_log


class StockView(ListCreateAPIView):
    """
    Get :
    Post :
    """
    serializer_class = StockSerializer

    def get_queryset(self):
        stock_name = self.request.GET.get('stock_name', None)
        start_date = self.request.GET.get('start_date', None)
        end_date = self.request.GET.get('end_date', None)

        if stock_name:
            #     if not os.path.exists(f"api/شاخص كل/شاخص كل-{start_date}-{end_date}.xlsx"):
            #         fetch_stock_historical_data('شاخص كل', start_date, end_date)
            #     else:
            #         make_log('info', f'market-history already exists for {start_date}-{end_date}')
            #
            #     if not os.path.exists(f"api/{stock_name}/{stock_name}-{start_date}-{end_date}.xlsx"):
            #         fetch_stock_historical_data(stock_name, start_date, end_date)
            #     else:
            #         make_log('info', f'stock-history for {stock_name} already exists for {start_date}-{end_date}')
            #
            #     beta = calculate_beta(stock_name, start_date, end_date)

            # print(f'Beta of {stock_name} in {start_date}-{end_date} is {calculate_beta(stock_name, start_date, end_date)}')

            beta = 1
            queryset = Stock.objects.filter(stock_name__icontains=stock_name, start_date__icontains=start_date,
                                            end_date__icontains=end_date)

            for stock in queryset:
                stock.beta = beta  # assuming `beta` is a calculated value that you have somewhere
                stock.save()

            return Stock.objects.filter(stock_name__icontains=stock_name)

        return Stock.objects.none()

    def post(self, request, *args, **kwargs):
        return Response({"status": "POST method is not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
