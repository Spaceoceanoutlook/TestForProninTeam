from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from collects.models import Collect
from payments.models import Payment
from faker import Faker
from decimal import Decimal
import random
from datetime import timedelta
from django.utils import timezone

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Create mock users, collects, and payments"

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=5, help='Количество пользователей')
        parser.add_argument('--collects', type=int, default=20, help='Количество сборов')
        parser.add_argument('--payments', type=int, default=100, help='Количество платежей')

    def handle(self, *args, **options):
        user_count = options['users']
        collect_count = options['collects']
        payment_count = options['payments']

        # Создание пользователей
        users = []
        for i in range(user_count):
            user = User.objects.create_user(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                password="test5555"
            )
            users.append(user)
        self.stdout.write(self.style.SUCCESS(f'✅ Создано {len(users)} пользователей'))

        # Создание сборов
        reasons = [choice[0] for choice in Collect.REASON_CHOICES]
        collects = []
        for _ in range(collect_count):
            author = random.choice(users)
            collect = Collect.objects.create(
                author=author,
                title=fake.sentence(nb_words=4),
                reason=random.choice(reasons),
                description=fake.text(max_nb_chars=500),
                target_amount=Decimal(random.randint(1000, 100000)),
                end_datetime=timezone.now() + timedelta(days=random.randint(5, 365)),
            )
            collects.append(collect)
        self.stdout.write(self.style.SUCCESS(f'✅ Создано {len(collects)} сборов'))

        # Создание платежей
        payments = []
        for _ in range(payment_count):
            user = random.choice(users)
            collect = random.choice(collects)
            amount = Decimal(random.randint(100, 10000)) / 100
            payment = Payment.objects.create(
                user=user,
                collect=collect,
                amount=amount
            )
            # Обновляем данные сбора
            collect.current_amount += amount
            collect.contributors_count += 1
            collect.save()
            payments.append(payment)
        self.stdout.write(self.style.SUCCESS(f'✅ Создано {len(payments)} платежей'))
