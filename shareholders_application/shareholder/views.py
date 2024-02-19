from django.shortcuts import render, redirect
from .forms import ShareholderForm, SharePaymentForm
from .models import Shareholder, SharePayment,PaymentInstalment
from .constants import *
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, F, Case, When, Value, IntegerField, DecimalField
from datetime import date, datetime, timedelta
import calendar
from django_countries.data import COUNTRIES
from django.db.models import Q
from .serializers import PaymentInstalmentSerializer, SharePaymentSerializer
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponseRedirect

def create_shareholder(request):
    if request.method == 'POST':
        form = ShareholderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('shareholder_listing')
    else:
        form = ShareholderForm()
    return render(request, 'create_shareholder.html', {'form': form})

def shareholder_listing(request):
    shareholders = Shareholder.objects.all()
    return render(request, 'shareholder_listing.html', {'shareholders': shareholders})

def create_share_amount(request,shareholder_id):
    check_share_exists = SharePayment.objects.filter(shareholder_id=shareholder_id).exists()
    if check_share_exists:
     shareholders = Shareholder.objects.all()
     return render(request, 'shareholder_listing.html', {'check_share_exists': check_share_exists,'shareholders': shareholders})
    else:
        INSTALMENT_TYPE = [
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('annual', 'Annual'),
            ('custom', 'Custom'),
        ]
        form = SharePaymentForm()
        return render(request, 'add_share_amount.html',{'form': form, 'shareholder_id': shareholder_id,'instalment_type':INSTALMENT_TYPE})
    

def generate_payment_schedule(request):
    if request.method == 'POST':
        duration = int(request.POST.get('duration'))
        annual_amount = float(request.POST.get('annual_amount'))
        instalment_type = request.POST.get('instalment_type')
        start_date_str = request.POST.get('start_date')
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
  

        payment_schedule = []

        total_months = duration * 12 if instalment_type != 'annual' else duration

        if instalment_type == 'monthly':
            instalment_count = total_months
        elif instalment_type == 'quarterly':
            instalment_count = total_months // 3
        elif instalment_type == 'annual':
            instalment_count = duration
        
        instalment_amount = round(annual_amount / instalment_count, 2)
        current_date = start_date

        for _ in range(instalment_count):
            payment_schedule.append({
                'due_date': current_date.strftime('%Y-%m-%d'),
                'instalment_amount': instalment_amount
            })
            if instalment_type == 'monthly':
                current_date += relativedelta(months=1)
            elif instalment_type == 'quarterly':
                current_date += relativedelta(months=3)
            elif instalment_type == 'annual':
                current_date += relativedelta(years=1)
        return JsonResponse({'payment_schedule': payment_schedule})
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def save_payment_data(request):
    if request.method == 'POST':
        shareholder_id = request.POST.get('user_id')
        duration = request.POST.get('duration')
        total_amount = request.POST.get('totalAmount')
        instalment_type = request.POST.get('instalmentType')
        start_date = request.POST.get('startDate')
        payment_mode = request.POST.get('payment_mode')
        staff_name = request.POST.get('Staff_name')
        due_dates = request.POST.getlist('due_date[]')
        instalment_amounts = request.POST.getlist('instalment_amount[]')

        share_payment = SharePayment.objects.create(
            shareholder_id=shareholder_id,
            duration=duration,
            annual_amount=total_amount,
            instalment_type=instalment_type,
            start_date=start_date,
            payment_mode=payment_mode,
            staff_name=staff_name
        )

        for due_date, instalment_amount in zip(due_dates, instalment_amounts):
            PaymentInstalment.objects.create(
                shareholder_id=shareholder_id,
                share_payment=share_payment,
                payment_date=due_date,
                amount=instalment_amount
            )
        return JsonResponse({'message': 'Payment data saved successfully.'})
    else:
        return JsonResponse({'error': 'Invalid request.'}, status=400)
    
def share_amount_summary(request):

    current_month = date.today().month
    month_name = calendar.month_name[current_month]
    current_year = date.today().year

    results = PaymentInstalment.objects.filter(
        payment_date__month=current_month,
        payment_date__year=current_year
    ).aggregate(
        total_collected_amount=Sum(
            Case(
                When(status=1, then=F('amount')),
                default=Value(0),
                output_field=DecimalField()
            )
        ),
        total_expected_amount=Sum('amount')
    )

    total_collected_amount = results['total_collected_amount'] or 0
    total_expected_amount = results['total_expected_amount'] or 0
    due_amount = total_expected_amount - total_collected_amount
    
    monthly_summary = PaymentInstalment.objects.filter(
        status=0,
        payment_date__month=current_month,
        payment_date__year=current_year
        ).select_related('share_payment__shareholder').annotate(
            total_amount=Sum(
                Case(
                    When(status=0, then=F('amount')),
                    default=Value(0),
                    output_field=DecimalField()
                )
            )
        ).values(
            'share_payment_id',
            'share_payment__shareholder__name',
            'payment_date',
            'amount',
            'paid_at',
            'status',
            'id',
            'total_amount'
        )
    return render(request, 'share_monthly_summary.html', 
                  {'monthly_summary': monthly_summary,
                   'total_collected_amount':total_collected_amount,
                   'total_expected_amount':total_expected_amount,
                   'due_amount':due_amount,
                   'month_name':month_name
                })


def payment_summary(request):
    shareholders = Shareholder.objects.all().values('id', 'name')
    months = [{'id': str(month).zfill(2), 'name': calendar.month_name[month]} for month in range(1, 13)]
    if request.method == 'GET':
        return render(request, 'payment_summary.html', {'shareholders': shareholders, 'months': months, 'STATUS_CHOICES': STATUS_CHOICES})

    elif request.method == 'POST':
        selected_month = request.POST.get('month')
        selected_status = request.POST.get('status') 
        shareholder_id = request.POST.get('shareholder_id') 
        shareholder_details = None

        if shareholder_id:
            try:
                shareholder = int(shareholder_id)
            except ValueError:
                return JsonResponse({'error': 'Invalid shareholder ID'}, status=400)
            
            try:
                shareholder_details = SharePayment.objects.get(shareholder=shareholder_id)
            except SharePayment.DoesNotExist:
                return JsonResponse({'error': 'Shareholder details not found'}, status=400)
            
            shareholder_serializer = SharePaymentSerializer(shareholder_details, many=False)
            shareholder_deta = shareholder_serializer.data

        custom_filter = Q() 
        if selected_month:
            custom_filter &= Q(payment_date__month=selected_month)
        
        if selected_status:
            custom_filter &=Q(status=selected_status)
       
        payment_instalments = PaymentInstalment.objects.filter(
            Q(custom_filter),
            Q(shareholder=shareholder)
        ).order_by('payment_date')

        serializer = PaymentInstalmentSerializer(payment_instalments, many=True)
        serialized_data = serializer.data

        return JsonResponse({'payment_instalments': serialized_data, 'shareholder_details':shareholder_deta})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


def update_shareholder_payment(request,payment_instalment_id):
    if request.method == 'PUT':
        try:
            payment_instalment = PaymentInstalment.objects.get(id=payment_instalment_id)
            payment_instalment.status = 1
            payment_instalment.paid_at = timezone.now().date()
            payment_instalment.save()
            return JsonResponse({'message': 'Payment updated successfully'})
        except PaymentInstalment.DoesNotExist:
            return JsonResponse({'error': 'PaymentInstalment not found'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=405)