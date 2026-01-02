from celery import shared_task
from django.utils import timezone
from .services import DocumentService
from .models import DocumentSignature
import random
import logging

logger = logging.getLogger(__name__)


@shared_task
def generate_document_task(template_id, application_id, user_id, field_values=None):
    """Асинхронная генерация документа"""
    
    try:
        document = DocumentService.generate_document(
            template_id, application_id, user_id, field_values
        )
        
        logger.info(f"Document {document.id} generated successfully")
        return {
            'status': 'success',
            'document_id': document.id,
            'message': 'Документ успешно сгенерирован'
        }
        
    except Exception as e:
        logger.error(f"Document generation failed: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def send_sms_code_task(signature_id):
    """Отправка SMS кода для подписания"""
    
    try:
        signature = DocumentSignature.objects.get(id=signature_id)
        
        # Генерируем 6-значный код
        code = str(random.randint(100000, 999999))
        signature.sms_code = code
        signature.sms_sent_at = timezone.now()
        signature.status = 'in_progress'
        signature.save()
        
        # Здесь должна быть интеграция с SMS провайдером
        # Например, через SMS.to, Twilio и т.д.
        
        # Заглушка для демонстрации
        logger.info(f"SMS code {code} sent to user {signature.signer.id}")
        
        return {
            'status': 'success',
            'signature_id': signature_id,
            'message': 'SMS код отправлен'
        }
        
    except Exception as e:
        logger.error(f"SMS sending failed: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def send_document_email_task(document_id, recipients):
    """Отправка документа по email"""
    
    try:
        from .models import GeneratedDocument
        from django.core.mail import EmailMessage
        
        document = GeneratedDocument.objects.get(id=document_id)
        
        subject = f"Документ {document.template.name}"
        body = f"Вам отправлен документ {document.template.name} по заявке {document.application.number}"
        
        email = EmailMessage(
            subject=subject,
            body=body,
            to=recipients
        )
        
        # Прикрепляем файл
        if document.signed_file:
            email.attach_file(document.signed_file.path)
        else:
            email.attach_file(document.original_file.path)
        
        email.send()
        
        # Обновляем статус отправки
        document.sent_at = timezone.now()
        document.sent_to = recipients
        document.save()
        
        logger.info(f"Document {document_id} sent to {recipients}")
        
        return {
            'status': 'success',
            'recipients': recipients
        }
        
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def cleanup_old_documents_task():
    """Очистка старых документов"""
    
    from django.utils import timezone
    from datetime import timedelta
    from .models import GeneratedDocument
    
    try:
        # Удаляем черновики старше 30 дней
        cutoff_date = timezone.now() - timedelta(days=30)
        
        old_documents = GeneratedDocument.objects.filter(
            status='draft',
            created_at__lt=cutoff_date
        )
        
        count = old_documents.count()
        old_documents.delete()
        
        logger.info(f"Deleted {count} old draft documents")
        
        return {
            'status': 'success',
            'deleted_count': count
        }
        
    except Exception as e:
        logger.error(f"Document cleanup failed: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }