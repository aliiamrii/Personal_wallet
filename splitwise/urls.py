from django.urls import path
from .views import generate_invite_link, join_group_by_token, list_group_members, list_user_groups, search_users, split_expenses, create_group, add_member_to_group, register_expense

urlpatterns = [
    path('group/create/', create_group, name='create-group'),
    path('group/<int:group_id>/add-member/', add_member_to_group, name='add-member'),
    path('group/list/', list_user_groups, name='list-user-groups'),
    path('group/<int:group_id>/members/', list_group_members, name='list-group-members'),
    path('expense/register/', register_expense, name='register-expense'),
    path('<int:group_id>/split/', split_expenses, name='split-expenses'),
    path('group/<int:group_id>/invite/', generate_invite_link, name='generate-invite'),
    path('group/join/<uuid:token>/', join_group_by_token, name='join-by-token'),
    path('search-user/', search_users, name='search-user'),

]