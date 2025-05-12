from django.contrib import admin
from .models import Group,GroupInvitation, Expense

# Register your models here.
admin.site.register(Group)
admin.site.register(GroupInvitation)
admin.site.register(Expense)