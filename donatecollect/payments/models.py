from django.db import models
from django.contrib.auth import get_user_model
from collects.models import Collect

User = get_user_model()

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    collect = models.ForeignKey(Collect, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"
