from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class TaskName(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_name = models.ForeignKey(TaskName, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.task_name} - {self.cost}"