from django.db import models
from django.core.validators import MinLengthValidator


# Create your models here.

class Stock(models.Model):
    stock_name = models.CharField(max_length=255)
    date = models.CharField(max_length=8, validators=[MinLengthValidator(8)])
    price = models.FloatField(null=True, blank=True)


class MarketIndex(models.Model):
    date = models.CharField(max_length=8, validators=[MinLengthValidator(8)])
    price = models.FloatField(null=True, blank=True)


class Beta(models.Model):
    stock_name = models.CharField(max_length=255)
    start_date = models.CharField(max_length=8, validators=[MinLengthValidator(8)])
    end_date = models.CharField(max_length=8, validators=[MinLengthValidator(8)])
    value = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.stock_name}-{self.start_date}-{self.end_date}"
