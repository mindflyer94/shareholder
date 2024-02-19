from django.db import models
from django_countries.fields import CountryField
from django.core.validators import RegexValidator

# Create your models here.
STATUS_CHOICES = (
    (0, 'In progress'),
    (1, 'Completed'),
    (2, 'Due'),
)

class Shareholder(models.Model):
    name = models.CharField(max_length=255, null=False)
    mobile_number = models.CharField(max_length=15, null=False, validators=[RegexValidator(r'^[0-9]+$')])
    email = models.EmailField(null=False, unique=True)
    country = CountryField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def __str__(self):
        return self.name


class SharePayment(models.Model):
    shareholder = models.ForeignKey(Shareholder, on_delete=models.CASCADE)
    duration = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    annual_amount = models.DecimalField(max_digits=10, decimal_places=2)
    INSTALMENT_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
        ('custom', 'Custom'),
    ]
    instalment_type = models.CharField(max_length=20, choices=INSTALMENT_CHOICES)
    start_date = models.DateField()

    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    payment_mode = models.CharField(max_length=20)
    staff_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class PaymentInstalment(models.Model):
    shareholder = models.ForeignKey(Shareholder, on_delete=models.CASCADE, blank=True, null=True)
    share_payment = models.ForeignKey(SharePayment, on_delete=models.CASCADE)
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    paid_at = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    