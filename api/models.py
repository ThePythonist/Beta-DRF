from django.db import models
from django.core.validators import MinLengthValidator


# Create your models here.

class Market(models.Model):
    start_date = models.CharField(max_length=8, validators=[MinLengthValidator(8)])
    end_date = models.CharField(max_length=8, validators=[MinLengthValidator(8)])
    market_index = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Market Index from {self.start_date} to {self.end_date}"


class Stock(models.Model):
    stock_name = models.CharField(max_length=255)
    stock_type = models.CharField(max_length=255)
    stock_code = models.CharField(max_length=100)
    start_date = models.CharField(max_length=8, validators=[MinLengthValidator(8)])
    end_date = models.CharField(max_length=8, validators=[MinLengthValidator(8)])
    beta = models.FloatField(null=True, blank=True)
    market = models.ForeignKey(Market, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.stock_name}-{self.start_date}-{self.end_date}"

    def save(self, *args, **kwargs):
        # Automatically set the market field based on start_date and end_date
        try:
            self.market = Market.objects.get(start_date__lte=self.start_date, end_date__gte=self.end_date)
        except Market.DoesNotExist:
            self.market = None  # Handle the case where no matching Market record is found
        super().save(*args, **kwargs)  # Call the original save method
