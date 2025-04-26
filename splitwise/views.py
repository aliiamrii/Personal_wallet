from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Group, Expense
from .utils import calculate_balances
from rest_framework import status
from .serializers import GroupSerializer, ExpenseSerializer
from django.contrib.auth.models import User


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group(request):
    serializer = GroupSerializer(data=request.data)
    if serializer.is_valid():
        group = serializer.save()
        group.members.add(request.user)
        return Response(GroupSerializer(group).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_member_to_group(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Response({'error': 'Group not found'}, status=404)

    username = request.data.get('username')
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    group.members.add(user)
    return Response({'message': f'{username} added to group.'}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_expense(request):
    serializer = ExpenseSerializer(data=request.data)
    if serializer.is_valid():
        expense = serializer.save()
        return Response(ExpenseSerializer(expense).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_groups(request):
    groups = request.user.groups.all()
    serializer = GroupSerializer(groups, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def split_expenses(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Response({'error': 'Group not found'}, status=404)

    expenses = Expense.objects.filter(group=group)
    members = group.members.all()

    per_person, transactions = calculate_balances(expenses, members)

    return Response({
        'per_person': per_person,
        'transactions': transactions
    })