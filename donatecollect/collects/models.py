from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Collect(models.Model):
    REASON_CHOICES = [
        ('birthday', 'День рождения'),
        ('wedding', 'Свадьба'),
        ('charity', 'Благотворительность'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collects')
    title = models.CharField(max_length=200)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    description = models.TextField()
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Цель")
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Собранная сумма")
    contributors_count = models.PositiveIntegerField(default=0, verbose_name="Количество жертвователей")
    cover_image = models.ImageField(upload_to='collects/covers/', null=True, blank=True)
    end_datetime = models.DateTimeField()

    def __str__(self):
        return self.title
