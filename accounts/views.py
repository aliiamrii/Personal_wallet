from django.contrib.auth import authenticate, get_user_model, update_session_auth_hash
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from accounts.models import CustomUser
from .utils import get_tokens_for_user

#update the user modele from django to the costumed user
User = get_user_model()

@api_view(['POST'])
def register_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    full_name = request.data.get('full_name')
    profile_picture = request.FILES.get('profile_picture')  #Multipart

    if not username or not password or not email or not full_name:
        return Response({'error': 'All fields except profile picture are required'}, status=400)

    if CustomUser.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=400)
    if CustomUser.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=400)

    user = CustomUser.objects.create_user(
        username=username,
        password=password,
        email=email,
        full_name=full_name,
        profile_picture=profile_picture
    )

    tokens = get_tokens_for_user(user)

    return Response({
        'message': 'User created successfully',
        'tokens': tokens
    }, status=200)


@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is None:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    tokens = get_tokens_for_user(user)

    return Response({
        'message': 'Login successful',
        'tokens': tokens
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user
    profile_picture_url = request.build_absolute_uri(user.profile_picture.url) if user.profile_picture else None

    return Response({
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'profile_picture': profile_picture_url
    })

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    data = request.data

    username = data.get('username')
    password = data.get('password')
    current_password = data.get('current_password')
    full_name = data.get('full_name')
    email = data.get('email')
    profile_picture = request.FILES.get('profile_picture')

    updated = False

    if username:
        if User.objects.filter(username=username).exclude(id=user.id).exists():
            return Response({'error': 'Username is already taken'}, status=400)
        if user.username != username:
            user.username = username
            updated = True

    if full_name:
        user.full_name = full_name
        updated = True

    if email:
        user.email = email
        updated = True

    if profile_picture:
        user.profile_picture = profile_picture
        updated = True

    if password:
        if not current_password:
            return Response({'error': 'Current password is required to change password'}, status=400)
        if not user.check_password(current_password):
            return Response({'error': 'Current password is incorrect'}, status=400)
        user.set_password(password)
        update_session_auth_hash(request, user)
        updated = True

    if updated:
        user.save()
        return Response({'message': 'Profile updated successfully'}, status=200)
    else:
        return Response({'message': 'No changes were made to your profile.'}, status=200)