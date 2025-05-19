from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('profile/update/', views.update_profile, name='update-profile'),
    path('profile/', views.get_profile, name='get-profile'),
]