from django.urls import path
from . import views

urlpatterns = [
    path('create-shareholder', views.create_shareholder, name='create_shareholder'),
    path('', views.shareholder_listing, name='shareholder_listing'),
    path('shareholders/<int:shareholder_id>/create-share-amount/', views.create_share_amount, name='create_share_amount'),
    path('generate_payment_schedule/',views.generate_payment_schedule, name='generate_payment_schedule'),
    path('save-payment-data/', views.save_payment_data, name='save_payment_data'),
    path('share-amount-summary', views.share_amount_summary, name='share_amount_summary'),
    path('payment-summary', views.payment_summary, name='payment_summary'),
    path('update-payment/<int:payment_instalment_id>', views.update_shareholder_payment, name='update_payment'),

]
