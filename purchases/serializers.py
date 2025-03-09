from rest_framework import serializers
from .models import Purchase, TaskName

class TaskNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskName
        fields = '__all__'

class PurchaseSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Purchase
        fields = '__all__'