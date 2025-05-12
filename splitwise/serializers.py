    
from rest_framework import serializers
from .models import Group, Expense
from django.contrib.auth.models import User

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']
        

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'group', 'paid_by', 'amount', 'description', 'date']