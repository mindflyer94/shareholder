from django import forms
from .models import Shareholder,SharePayment
from django_countries.fields import CountryField

class ShareholderForm(forms.ModelForm):
    country = CountryField().formfield()

    class Meta:
        model = Shareholder
        fields = ['name', 'email', 'mobile_number', 'country']


class SharePaymentForm(forms.ModelForm):
    class Meta:
        model = SharePayment
        fields = ['duration', 'annual_amount', 'instalment_type', 'start_date','payment_mode','staff_name']
