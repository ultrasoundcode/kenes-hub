from datetime import datetime, time
from django.utils import timezone
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template import Template, Context
from .models import (
    Notification, NotificationTemplate, NotificationStatus,
    EmailOutbox, SMSOutbox, UserNotificationSettings,
    NotificationChannel, NotificationType
)
import logging
import requests
import random

logger = logging.getLogger(__name__)


class NotificationService:
    """Сервис для отправки уведомлений"""

    @staticmethod
    def send_notification(
        recipient, notification_type, channel, 
        title=None, message=None, data=None,
        template_code=None, related_application=None,
        related_document=None, scheduled_at=None
    ):
        """Отправляет уведомление пользователю"""
        
        # Получаем настройки пользователя
        settings = getattr(recipient, 'notification_settings', None)
        
        # Проверяем, разрешены ли уведомления
        if settings and not NotificationService._is_channel_enabled(settings, channel):
            return None
        
        # Получаем шаблон
        template = None
        if template_code:
            try:
                template = NotificationTemplate.objects.get(code=template_code)
            except NotificationTemplate.DoesNotExist:
                logger.warning(f"Template {template_code} not found")
        
        # Создаем уведомление
        notification = Notification.objects.create(
            recipient=recipient,
            template=template,
            notification_type=notification_type,
            channel=channel,
            title=title,
            message=message,
            data=data or {},
            related_application=related_application,
            related_document=related_document,
            scheduled_at=scheduled_at
        )
        
        # Отправляем немедленно, если не запланировано
        if not scheduled_at:
            NotificationService._send_immediately(notification)
        
        return notification

    @staticmethod
    def _is_channel_enabled(settings, channel):
        """Проверяет, разрешен ли канал"""
        
        if channel == NotificationChannel.EMAIL:
            return settings.email_enabled
        elif channel == NotificationChannel.SMS:
            return settings.sms_enabled
        elif channel == NotificationChannel.PUSH:
            return settings.push_enabled
        elif channel == NotificationChannel.WHATSAPP:
            return settings.whatsapp_enabled
        
        return True

    @staticmethod
    def _send_immediately(notification):
        """Немедленная отправка уведомления"""
        
        try:
            if notification.channel == NotificationChannel.EMAIL:
                NotificationService._send_email(notification)
            elif notification.channel == NotificationChannel.SMS:
                NotificationService._send_sms(notification)
            elif notification.channel == NotificationChannel.PUSH:
                NotificationService._send_push(notification)
            elif notification.channel == NotificationChannel.WHATSAPP:
                NotificationService._send_whatsapp(notification)
            
            notification.status = NotificationStatus.SENT
            notification.sent_at = timezone.now()
            notification.save()
            
        except Exception as e:
            logger.error(f"Failed to send notification {notification.id}: {str(e)}")
            notification.attempts += 1
            notification.error_message = str(e)
            
            if notification.attempts >= notification.max_attempts:
                notification.status = NotificationStatus.FAILED
            
            notification.save()

    @staticmethod
    def _send_email(notification):
        """Отправка email"""
        
        subject = notification.title or 'Уведомление от Kenes Hub'
        message = notification.message
        
        # Используем шаблон, если доступен
        if notification.template and notification.template.email_body:
            template = notification.template.email_body
            context = Context(notification.data)
            message = Template(template).render(context)
            
            if notification.template.email_subject:
                subject = Template(notification.template.email_subject).render(context)
        
        # Создаем email
        email = EmailOutbox.objects.create(
            notification=notification,
            recipient_email=notification.recipient.email,
            subject=subject,
            body=message,
            html_body=notification.template.email_html if notification.template else '',
            headers={'X-Notification-ID': str(notification.id)}
        )
        
        # Отправляем
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.recipient.email],
                fail_silently=False,
            )
            email.status = NotificationStatus.SENT
            email.sent_at = timezone.now()
            email.save()
            
        except Exception as e:
            email.status = NotificationStatus.FAILED
            email.error_message = str(e)
            email.save()
            raise

    @staticmethod
    def _send_sms(notification):
        """Отправка SMS"""
        
        message = notification.message
        
        # Используем шаблон, если доступен
        if notification.template and notification.template.sms_template:
            template = notification.template.sms_template
            context = Context(notification.data)
            message = Template(template).render(context)
        
        # Создаем SMS
        sms = SMSOutbox.objects.create(
            notification=notification,
            recipient_phone=notification.recipient.phone,
            message=message
        )
        
        # Здесь должна быть интеграция с SMS провайдером
        # Пример с SMS.to:
        try:
            response = requests.post(
                f"{settings.SMS_API_URL}/sms",
                headers={
                    'Authorization': f'Bearer {settings.SMS_API_KEY}',
                    'Content-Type': 'application/json'
                },
                json={
                    'to': notification.recipient.phone,
                    'message': message,
                    'sender_id': 'KenesHub'
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                sms.sms_id = result.get('message_id')
                sms.status = NotificationStatus.SENT
                sms.sent_at = timezone.now()
                sms.save()
            else:
                raise Exception(f"SMS API error: {response.text}")
                
        except Exception as e:
            sms.status = NotificationStatus.FAILED
            sms.error_message = str(e)
            sms.save()
            raise

    @staticmethod
    def _send_push(notification):
        """Отправка push-уведомлений"""
        
        # Здесь должна быть интеграция с FCM/APNS
        # Для демонстрации просто логируем
        
        logger.info(f"Push notification to {notification.recipient}: {notification.title}")
        
        # Пример с FCM:
        # from firebase_admin import messaging
        # message = messaging.Message(
        #     notification=messaging.Notification(
        #         title=notification.title,
        #         body=notification.message
        #     ),
        #     token=device_token
        # )
        # messaging.send(message)

    @staticmethod
    def _send_whatsapp(notification):
        """Отправка WhatsApp сообщений"""
        
        # Здесь должна быть интеграция с WhatsApp Business API
        # Для демонстрации просто логируем
        
        logger.info(f"WhatsApp message to {notification.recipient}: {notification.message}")
        
        # Пример с WhatsApp Business API:
        # response = requests.post(
        #     f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_ID}/messages",
        #     headers={
        #         'Authorization': f'Bearer {settings.WHATSAPP_API_TOKEN}',
        #         'Content-Type': 'application/json'
        #     },
        #     json={
        #         'messaging_product': 'whatsapp',
        #         'to': notification.recipient.phone,
        #         'type': 'text',
        #         'text': {'body': notification.message}
        #     }
        # )

    @staticmethod
    def send_application_created(application):
        """Отправка уведомления о создании заявки"""
        
        # Уведомление заявителю
        NotificationService.send_notification(
            recipient=application.applicant,
            notification_type=NotificationType.APPLICATION_CREATED,
            channel=NotificationChannel.EMAIL,
            title=f"Заявка {application.number} создана",
            message=f"Ваша заявка '{application.subject}' успешно создана и находится на рассмотрении.",
            related_application=application,
            template_code='application_created'
        )
        
        # Уведомление ответственному
        if application.assigned_to:
            NotificationService.send_notification(
                recipient=application.assigned_to,
                notification_type=NotificationType.APPLICATION_CREATED,
                channel=NotificationChannel.EMAIL,
                title=f"Новая заявка {application.number}",
                message=f"Получена новая заявка от {application.applicant.get_full_name()}: {application.subject}",
                related_application=application
            )

    @staticmethod
    def send_status_changed(application, old_status, new_status):
        """Отправка уведомления об изменении статуса"""
        
        NotificationService.send_notification(
            recipient=application.applicant,
            notification_type=NotificationType.APPLICATION_STATUS_CHANGED,
            channel=NotificationChannel.EMAIL,
            title=f"Статус заявки {application.number} изменен",
            message=f"Статус вашей заявки '{application.subject}' изменен с '{old_status}' на '{new_status}'",
            related_application=application,
            data={'old_status': old_status, 'new_status': new_status}
        )

    @staticmethod
    def send_deadline_reminder(application):
        """Отправка напоминания о дедлайне"""
        
        if application.deadline:
            NotificationService.send_notification(
                recipient=application.assigned_to or application.applicant,
                notification_type=NotificationType.DEADLINE_APPROACHING,
                channel=NotificationChannel.EMAIL,
                title=f"Напоминание: дедлайн по заявке {application.number}",
                message=f"До дедлайна по заявке '{application.subject}' осталось менее 24 часов",
                related_application=application
            )

    @staticmethod
    def process_scheduled_notifications():
        """Обработка запланированных уведомлений"""
        
        now = timezone.now()
        pending_notifications = Notification.objects.filter(
            status=NotificationStatus.PENDING,
            scheduled_at__lte=now
        )
        
        for notification in pending_notifications:
            NotificationService._send_immediately(notification)

    @staticmethod
    def mark_as_read(user, notification_id):
        """Отмечает уведомление как прочитанное"""
        
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=user
            )
            notification.status = NotificationStatus.READ
            notification.read_at = timezone.now()
            notification.save()
            
            return True
        except Notification.DoesNotExist:
            return False

    @staticmethod
    def get_unread_count(user):
        """Возвращает количество непрочитанных уведомлений"""
        
        return Notification.objects.filter(
            recipient=user,
            status__in=[NotificationStatus.PENDING, NotificationStatus.SENT, NotificationStatus.DELIVERED]
        ).count()