from rest_framework import serializers
from .models import *


class BetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Beta
        fields = "__all__"
