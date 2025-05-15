from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg, Sum
from django.db.models.functions import TruncDate
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Purchase, TaskName
from .serializers import PurchaseSerializer, TaskNameSerializer


class TaskNameViewSet(viewsets.ModelViewSet):
    queryset = TaskName.objects.all()
    serializer_class = TaskNameSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.select_related('user').all()
    serializer_class = PurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Purchase.objects.filter(user=self.request.user).select_related('user')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


def get_date_range(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if not start_date_str:
        start_date = timezone.now() - timedelta(days=30)
    else:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        if timezone.is_naive(start_date):
            start_date = timezone.make_aware(start_date)

    if not end_date_str:
        end_date = timezone.now()
    else:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        if timezone.is_naive(end_date):
            end_date = timezone.make_aware(end_date)

    return start_date, end_date


def get_average_spending(user=None, start_date=None, end_date=None, category=None):
    queryset = Purchase.objects.annotate(day=TruncDate('purchase_date')).filter(
        purchase_date__gte=start_date,
        purchase_date__lte=end_date
    )

    if user:
        queryset = queryset.filter(user=user)
    if category:
        queryset = queryset.filter(task_name__name=category)

    return queryset.values('day').annotate(avg_cost=Avg('cost')).order_by('day')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def spending_chart(request):
    user = request.user
    start_date, end_date = get_date_range(request)
    category = request.GET.get('category')

    overall_purchases = get_average_spending(start_date=start_date, end_date=end_date, category=category)
    overall_series = [{"value": round(entry["avg_cost"], 2), "name": entry["day"].isoformat()} for entry in overall_purchases]

    user_purchases = get_average_spending(user=user, start_date=start_date, end_date=end_date, category=category)
    user_series = [{"value": round(entry["avg_cost"], 2), "name": entry["day"].isoformat()} for entry in user_purchases]

    response_data = [
        {"name": "Overall Average", "series": overall_series},
        {"name": user.username, "series": user_series}
    ]

    return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def category_spending_comparison(request):
    user = request.user
    category = request.GET.get('category')

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            if timezone.is_naive(start_date):
                start_date = timezone.make_aware(start_date)
        else:
            start_date = timezone.now() - timedelta(days=30)

        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            if timezone.is_naive(end_date):
                end_date = timezone.make_aware(end_date)
        else:
            end_date = timezone.now()
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

    if not category:
        return Response({'error': 'Category is required'}, status=400)

    #calc the usege of the user and all users
    user_spending = Purchase.objects.filter(
        user=user,
        task_name__name=category,
        purchase_date__range=[start_date, end_date]
    ).aggregate(total=Sum('cost'))['total'] or 0

    overall_queryset = Purchase.objects.filter(
        task_name__name=category,
        purchase_date__range=[start_date, end_date]
    )

    overall_spending = overall_queryset.aggregate(total=Sum('cost'))['total'] or 0
    user_percentage = 0

    if overall_spending > 0:
        distinct_user_count = overall_queryset.values('user').distinct().count()
        avg_per_user = overall_spending / distinct_user_count if distinct_user_count > 0 else 0

        if avg_per_user > 0:
            user_percentage = ((user_spending - avg_per_user) / avg_per_user) * 100

    response_data = {
        'category': category,
        'user_spending': round(user_spending, 2),
        'overall_avg_spending': round(avg_per_user, 2) if overall_spending > 0 else 0,
        'percentage_difference': round(user_percentage, 2),
        'comparison': "more" if user_percentage > 0 else "less"
    }

    return Response(response_data)