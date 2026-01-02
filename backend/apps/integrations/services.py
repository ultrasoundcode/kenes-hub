import requests
import json
import hashlib
import hmac
from django.conf import settings
from django.utils import timezone
from apps.applications.models import Application
from apps.notifications.services import NotificationService
from apps.notifications.models import NotificationType, NotificationChannel
import logging

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Сервис для работы с WhatsApp Business API"""

    @staticmethod
    def send_message(phone_number, message):
        """Отправляет сообщение в WhatsApp"""
        
        if not settings.WHATSAPP_API_TOKEN:
            raise Exception("WhatsApp API token not configured")
        
        url = f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_ID}/messages"
        
        headers = {
            'Authorization': f'Bearer {settings.WHATSAPP_API_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'messaging_product': 'whatsapp',
            'to': phone_number,
            'type': 'text',
            'text': {'body': message}
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return {
                'status': 'success',
                'message_id': response.json().get('messages', [{}])[0].get('id')
            }
        else:
            raise Exception(f"WhatsApp API error: {response.text}")

    @staticmethod
    def process_incoming_message(phone_number, message_text):
        """Обрабатывает входящее сообщение из WhatsApp"""
        
        # Ищем пользователя по телефону
        from apps.accounts.models import User
        
        try:
            user = User.objects.get(phone=phone_number)
        except User.DoesNotExist:
            # Регистрируем нового пользователя
            user = User.objects.create_user(
                username=f"whatsapp_{phone_number}",
                phone=phone_number,
                first_name='WhatsApp',
                last_name='User'
            )
        
        # Создаем заявку или добавляем комментарий
        if any(word in message_text.lower() for word in ['заявка', 'помощь', 'долг']):
            # Создаем заявку
            application = Application.objects.create(
                applicant=user,
                source='whatsapp',
                application_type='consultation',
                subject=f"Заявка из WhatsApp от {phone_number}",
                description=message_text
            )
            
            # Отправляем подтверждение
            confirmation_message = f"Спасибо за обращение! Ваша заявка #{application.number} принята. Мы свяжемся с вами в ближайшее время."
            WhatsAppService.send_message(phone_number, confirmation_message)
            
            # Уведомляем менеджеров
            NotificationService.send_application_created(application)
            
        else:
            # Отвечаем на обычное сообщение
            response = "Спасибо за обращение! Для создания заявки напишите 'заявка' или 'помощь'."
            WhatsAppService.send_message(phone_number, response)


class SMSService:
    """Сервис для отправки SMS"""

    @staticmethod
    def send_message(phone_number, message):
        """Отправляет SMS"""
        
        if not settings.SMS_API_KEY:
            raise Exception("SMS API key not configured")
        
        url = f"{settings.SMS_API_URL}/sms"
        
        headers = {
            'Authorization': f'Bearer {settings.SMS_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'to': phone_number,
            'message': message,
            'sender_id': 'KenesHub'
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            return {
                'status': 'success',
                'sms_id': result.get('message_id')
            }
        else:
            raise Exception(f"SMS API error: {response.text}")


class ExternalAPIService:
    """Сервис для работы с внешними API"""

    @staticmethod
    def validate_iin(iin):
        """Проверяет ИИН через внешний API"""
        
        # Валидация ИИН по алгоритму
        if not ExternalAPIService._is_valid_iin(iin):
            return {'valid': False, 'error': 'Неверный формат ИИН'}
        
        # Здесь должно быть обращение к внешнему API
        # Для демонстрации возвращаем заглушку
        
        return {
            'valid': True,
            'iin': iin,
            'birth_date': ExternalAPIService._get_birth_date_from_iin(iin),
            'gender': ExternalAPIService._get_gender_from_iin(iin)
        }

    @staticmethod
    def get_bank_info(bik):
        """Получает информацию о банке по БИК"""
        
        # Здесь должно быть обращение к API НацБанка РК
        # Для демонстрации возвращаем заглушку
        
        bank_data = {
            '01012': {'name': 'АО "Народный Банк Казахстана"', 'city': 'Алматы'},
            '01013': {'name': 'АО "Казкоммерцбанк"', 'city': 'Алматы'},
            '01014': {'name': 'АО "Банк ЦентрКредит"', 'city': 'Алматы'},
            '01015': {'name': 'АО "Альфа-Банк"', 'city': 'Алматы'},
        }
        
        if bik in bank_data:
            return {
                'bik': bik,
                'name': bank_data[bik]['name'],
                'city': bank_data[bik]['city']
            }
        else:
            return {'error': 'Банк не найден'}

    @staticmethod
    def create_payment_link(amount, description, order_id=None):
        """Создает ссылку на оплату через платежный агрегатор"""
        
        # Здесь должна быть интеграция с платежным агрегатором
        # Например, Kaspi, Freedom Pay, etc.
        
        # Для демонстрации создаем заглушку
        
        if not order_id:
            order_id = f"order_{timezone.now().strftime('%Y%m%d%H%M%S')}"
        
        payment_data = {
            'amount': amount,
            'description': description,
            'order_id': order_id,
            'currency': 'KZT',
            'payment_url': f"https://pay.kenes-hub.kz/pay/{order_id}",
            'status': 'created'
        }
        
        return payment_data

    @staticmethod
    def _is_valid_iin(iin):
        """Проверяет корректность ИИН"""
        
        if len(iin) != 12 or not iin.isdigit():
            return False
        
        # Проверяем контрольную сумму
        weights = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        control_sum = sum(int(iin[i]) * weights[i] for i in range(11))
        control_digit = control_sum % 11
        
        if control_digit == 10:
            control_sum = sum(int(iin[i]) * (weights[i] + 2) for i in range(11))
            control_digit = control_sum % 11
        
        return control_digit == int(iin[11])

    @staticmethod
    def _get_birth_date_from_iin(iin):
        """Извлекает дату рождения из ИИН"""
        
        century = 1900 if iin[6] in '12' else 2000
        year = century + int(iin[0:2])
        month = int(iin[2:4])
        day = int(iin[4:6])
        
        return f"{year:04d}-{month:02d}-{day:02d}"

    @staticmethod
    def _get_gender_from_iin(iin):
        """Определяет пол из ИИН"""
        
        return 'male' if int(iin[6]) % 2 == 1 else 'female'


class CRMIntegrationService:
    """Сервис для интеграции с внешними CRM"""

    @staticmethod
    def sync_application_to_crm(application):
        """Синхронизирует заявку с внешним CRM"""
        
        # Здесь должна быть интеграция с API CRM
        # Для демонстрации просто логируем
        
        logger.info(f"Syncing application {application.id} to CRM")
        
        # Пример структуры данных для CRM
        crm_data = {
            'external_id': application.number,
            'client_name': application.applicant.get_full_name(),
            'client_phone': application.applicant.phone,
            'client_email': application.applicant.email,
            'subject': application.subject,
            'description': application.description,
            'status': application.status,
            'amount': str(application.amount) if application.amount else None,
            'created_at': application.created_at.isoformat(),
            'updated_at': application.updated_at.isoformat()
        }
        
        return crm_data

    @staticmethod
    def receive_lead_from_crm(crm_data):
        """Получает лид из CRM и создает заявку"""
        
        from apps.accounts.models import User
        from apps.applications.models import Application, ApplicationSource, ApplicationType
        
        # Создаем или обновляем пользователя
        user, created = User.objects.get_or_create(
            email=crm_data['email'],
            defaults={
                'first_name': crm_data.get('first_name', ''),
                'last_name': crm_data.get('last_name', ''),
                'phone': crm_data.get('phone', ''),
                'role': 'borrower'
            }
        )
        
        # Создаем заявку
        application = Application.objects.create(
            applicant=user,
            source=ApplicationSource.MANUAL,
            application_type=ApplicationType.CONSULTATION,
            subject=crm_data.get('subject', 'Заявка из CRM'),
            description=crm_data.get('description', ''),
            metadata={'crm_source': crm_data.get('source', 'unknown')}
        )
        
        return application