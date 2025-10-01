from django.db import models
from django.contrib.auth.models import User

class DeleteLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    object_repr = models.CharField(max_length=1000)
    model_name = models.CharField(max_length=100)
    deleted_at = models.DateTimeField(auto_now_add=True)