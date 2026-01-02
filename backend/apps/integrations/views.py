from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .services import WhatsAppService, SMSService, ExternalAPIService


@api_view(['POST'])
def whatsapp_webhook(request):
    """Webhook для получения сообщений из WhatsApp"""
    
    try:
        data = request.data
        
        # Обрабатываем входящее сообщение
        if data.get('object') == 'whatsapp_business_account':
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    
                    if 'messages' in value:
                        for message in value['messages']:
                            phone_number = message['from']
                            message_text = message['text']['body']
                            
                            # Создаем заявку или отвечаем
                            WhatsAppService.process_incoming_message(
                                phone_number, message_text
                            )
        
        return Response({'status': 'success'})
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def send_whatsapp_message(request):
    """Отправка WhatsApp сообщения"""
    
    phone = request.GET.get('phone')
    message = request.GET.get('message')
    
    if not phone or not message:
        return Response(
            {'error': 'Телефон и сообщение обязательны'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = WhatsAppService.send_message(phone, message)
        return Response(result)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_sms(request):
    """Отправка SMS"""
    
    phone = request.data.get('phone')
    message = request.data.get('message')
    
    if not phone or not message:
        return Response(
            {'error': 'Телефон и сообщение обязательны'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = SMSService.send_message(phone, message)
        return Response(result)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def validate_iin(request):
    """Проверка ИИН через внешний API"""
    
    iin = request.GET.get('iin')
    
    if not iin:
        return Response(
            {'error': 'ИИН обязателен'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = ExternalAPIService.validate_iin(iin)
        return Response(result)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_bank_info(request):
    """Получение информации о банке"""
    
    bik = request.GET.get('bik')
    
    if not bik:
        return Response(
            {'error': 'БИК обязателен'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = ExternalAPIService.get_bank_info(bik)
        return Response(result)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_payment_link(request):
    """Создание ссылки на оплату"""
    
    amount = request.data.get('amount')
    description = request.data.get('description')
    order_id = request.data.get('order_id')
    
    if not amount or not description:
        return Response(
            {'error': 'Сумма и описание обязательны'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = ExternalAPIService.create_payment_link(
            amount=amount,
            description=description,
            order_id=order_id
        )
        return Response(result)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )