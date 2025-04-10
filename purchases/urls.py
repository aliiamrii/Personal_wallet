from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PurchaseViewSet, TaskNameViewSet, category_spending_comparison , spending_chart

router = DefaultRouter()
router.register(r'tasks', TaskNameViewSet)
router.register(r'purchases', PurchaseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('spending_chart/', spending_chart, name='spending_chart'),
    path('category-comparison/', category_spending_comparison, name='category-comparison'),
]