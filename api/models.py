from django.db import models


# Create your models here.
class Stock(models.Model):
    stock_name = models.CharField(max_length=255)
    stock_type = models.CharField(max_length=255)
    stock_code = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.stock_name}:{self.stock_type}"
