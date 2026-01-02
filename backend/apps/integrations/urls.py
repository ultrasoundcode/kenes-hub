from django.urls import path
from . import views

urlpatterns = [
    path('whatsapp/webhook/', views.whatsapp_webhook, name='whatsapp-webhook'),
    path('whatsapp/send/', views.send_whatsapp_message, name='whatsapp-send'),
    path('sms/send/', views.send_sms, name='sms-send'),
    path('validate/iin/', views.validate_iin, name='validate-iin'),
    path('bank/info/', views.get_bank_info, name='bank-info'),
    path('payment/create/', views.create_payment_link, name='create-payment'),
]