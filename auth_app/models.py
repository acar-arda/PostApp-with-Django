from django.db import models
from django.contrib.auth.models import User
from random import randint

def generate_code():
    return str(randint(100000, 999999))

class BaseVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, default=generate_code, blank=True, null=True)
    old_code = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        abstract = True

class EmailVerification(BaseVerification):
    pass

class ForgotPasswordVerification(BaseVerification):
    pass