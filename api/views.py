# from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import *
from .serializers import *
from django.db.models import Q
from .scrape import *
from persiantools import characters
from .customlogs import make_log, tictoc
import jdatetime
from .scrape import funds


def is_valid_jalali_date(date_str):
    # Ensure the date_str has exactly 8 digits
    if len(date_str) != 8 or not date_str.isdigit():
        return False

    # Define the minimum allowed date (13870914)
    min_date = jdatetime.date(1387, 9, 14)

    # Parse the input string into a Jalali date
    try:
        year = int(date_str[:4])
        month = int(date_str[4:6])
        day = int(date_str[6:])
        jalali_date = jdatetime.date(year, month, day)
    except ValueError:
        return False  # Invalid date, such as out-of-range month or day

    # Check if the Jalali date is not earlier than the minimum date
    if jalali_date < min_date:
        return False

    # Check if the Jalali date is not later than today's date
    today = jdatetime.date.today()  # Get today's Jalali date
    if jalali_date > today:
        return False

    return True


class BetaView(ListCreateAPIView):
    """
    Get : Returns the beta coefficient for the requested stock in the requested timeframe
    Post : Not allowed.
    """
    serializer_class = BetaSerializer

    @tictoc  # log the response time
    def get_queryset(self):
        stock_name = self.request.GET.get('stock_name', )
        start_date = self.request.GET.get('start_date', )
        end_date = self.request.GET.get('end_date', )

        if stock_name and start_date and end_date:
            stock_name = characters.fa_to_ar(stock_name)  # Convert persian chars to arabic :/

            filters = Q()
            if stock_name:
                filters &= Q(stock_name__icontains=stock_name)

            if start_date:
                filters &= Q(start_date=start_date)  # or use start_date__gte=start_date if a range is intended

            if end_date:
                filters &= Q(end_date=end_date)  # or use end_date__lte=end_date if a range is intended

            # Query for stocks that match the filters
            queryset = Beta.objects.filter(filters)

            # print("SQL Query: ", queryset.query)
            # print("Queryset length: ", len(queryset))

            if len(queryset) == 1:
                return queryset
            elif len(queryset) == 0:  # Object doesnt exists

                today_year = jdatetime.datetime.now().strftime("%Y")
                today_month = jdatetime.datetime.now().strftime("%m")
                today_day = jdatetime.datetime.now().strftime("%d")

                fetch_stock_historical_data('شاخص كل', "13870914", f"{today_year}{today_month}{today_day}")

                if stock_name in [i["name"] for i in funds] and is_valid_jalali_date(
                        start_date) and is_valid_jalali_date(end_date):
                    fetch_stock_historical_data(f'{stock_name}', "13870914", f"{today_year}{today_month}{today_day}")

                    beta = calculate_beta(stock_name, start_date, end_date)

                    new_data = Beta.objects.create(
                        stock_name=stock_name,
                        start_date=start_date,
                        end_date=end_date,
                        value=beta,
                    )

                    return Beta.objects.filter(id=new_data.id)
                else:
                    return Beta.objects.none()
            else:
                print("There was a problem with the queryset")
        else:
            return Beta.objects.none()

    def post(self, request, *args, **kwargs):
        return Response({"status": "POST method is not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
