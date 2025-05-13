from rest_framework import serializers
from .models import Purchase, TaskName

class TaskNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskName
        fields = '__all__'

class PurchaseSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    task_name_display = serializers.CharField(source='task_name.name', read_only=True)

    class Meta:
        model = Purchase
        fields = [
            'id',
            'user',
            'task_name',         
            'task_name_display', 
            'description',
            'cost',
            'purchase_date'
        ]