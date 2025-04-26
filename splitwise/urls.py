from django.urls import path
from .views import list_user_groups, split_expenses, create_group, add_member_to_group, register_expense

urlpatterns = [
    path('group/create/', create_group, name='create-group'),
    path('group/<int:group_id>/add-member/', add_member_to_group, name='add-member'),
    path('group/list/', list_user_groups, name='list-user-groups'),
    path('expense/register/', register_expense, name='register-expense'),
    path('<int:group_id>/split/', split_expenses, name='split-expenses'),
]