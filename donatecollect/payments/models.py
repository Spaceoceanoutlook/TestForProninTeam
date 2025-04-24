from django.db import models
from django.contrib.auth import get_user_model
from collects.models import Collect
from django.core.validators import validate_email

User = get_user_model()

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    collect = models.ForeignKey(Collect, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"
    
    def save(self, *args, **kwargs):
        validate_email(self.user.email)
        validate_email(self.collect.author.email)
        super().save(*args, **kwargs)
