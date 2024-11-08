# from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import *
from .serializers import *
from .models import *
from django.db.models import Q
from .scrape import *
from .logging_conf import make_log
import os


class BetaView(ListCreateAPIView):
    """
    Get : Returns a list of stocks based on query parameters.
    Post : Not allowed.
    """
    serializer_class = BetaSerializer

    def get_queryset(self):
        stock_name = self.request.GET.get('stock_name', )
        start_date = self.request.GET.get('start_date', )
        end_date = self.request.GET.get('end_date', )

        if stock_name and start_date and end_date:
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

            # Prepare the filter criteria
            filters = Q()

            if stock_name:
                filters &= Q(stock_name__icontains=stock_name)

            if start_date:
                filters &= Q(start_date__icontains=start_date)  # Filter using icontains for start_date

            if end_date:
                filters &= Q(end_date__icontains=end_date)  # Filter using icontains for end_date

            # Query for stocks that match the filters
            queryset = Beta.objects.filter(filters)

            if len(queryset) == 1:
                return queryset
            elif len(queryset) == 0:  # Beta doesnt exists
                return Beta.objects.none()
            else:
                print("There was a problem with the queryset")
        else:
            return Beta.objects.none()

    def post(self, request, *args, **kwargs):
        return Response({"status": "POST method is not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
