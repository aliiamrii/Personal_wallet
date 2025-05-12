from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Group, Expense, GroupInvitation
from .utils import calculate_balances
from rest_framework import status
from .serializers import GroupSerializer, ExpenseSerializer
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


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
def generate_invite_link(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    if request.user not in group.members.all():
        return Response({"error": "You are not a member of this group."}, status=403)
    
    invite = GroupInvitation.objects.create(group=group)
    link = f"http://your-frontend.com/join-group/{invite.token}/"
    return Response({"invite_link": link})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_group_by_token(request, token):
    try:
        invitation = GroupInvitation.objects.get(token=token)
        if invitation.used_by:
            return Response({"error": "Link already used."}, status=400)

        user = request.user
        invitation.group.members.add(user)
        invitation.used_by = user
        invitation.save()

        return Response({"message": "Joined group successfully."})
    except GroupInvitation.DoesNotExist:
        return Response({"error": "Invalid token."}, status=404)

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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    username = request.GET.get('username', '').strip()
    if not username:
        return Response({'error': 'Username is required.'}, status=400)

    try:
        user = User.objects.exclude(id=request.user.id).get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=404)

    result = {'id': user.id, 'username': user.username}
    return Response(result, status=200)


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
    groups = Group.objects.filter(members=request.user)
    serializer = GroupSerializer(groups, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_group_members(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Response({'error': 'Group not found'}, status=404)
    
    if request.user not in group.members.all():
        return Response({'error': 'You are not a member of this group'}, status=403)

    members = group.members.all()
    result = [{'id': user.id, 'username': user.username} for user in members]
    return Response(result)


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