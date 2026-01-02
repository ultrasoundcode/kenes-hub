import openai
import json
import re
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from .models import (
    AIConversation, AIMessage, AIIntent, 
    AIKnowledgeBase, AIUsageStats
)
from apps.applications.models import Application
from apps.documents.models import DocumentTemplate


class AIService:
    """Сервис для работы с AI"""

    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    def process_message(self, user, message, session_id=None, application_id=None):
        """Обрабатывает сообщение пользователя"""
        
        start_time = timezone.now()
        
        # Получаем или создаем диалог
        if session_id:
            conversation, created = AIConversation.objects.get_or_create(
                session_id=session_id,
                defaults={'user': user}
            )
        else:
            session_id = f"{user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            conversation = AIConversation.objects.create(
                user=user,
                session_id=session_id
            )
            created = True
        
        # Привязываем заявку, если указана
        if application_id:
            try:
                application = Application.objects.get(id=application_id, applicant=user)
                conversation.application = application
                conversation.save()
            except Application.DoesNotExist:
                pass
        
        # Сохраняем сообщение пользователя
        user_message = AIMessage.objects.create(
            conversation=conversation,
            role='user',
            content=message
        )
        
        # Определяем интент
        intent = self._detect_intent(message)
        
        # Генерируем ответ
        response = self._generate_response(message, conversation, intent)
        
        # Сохраняем ответ ассистента
        assistant_message = AIMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=response,
            intent=intent,
            processing_time=(timezone.now() - start_time).total_seconds()
        )
        
        # Обновляем статистику
        self._update_usage_stats(user)
        
        return {
            'session_id': session_id,
            'message': response,
            'intent': intent.code if intent else None,
            'context': conversation.context
        }

    def _detect_intent(self, message):
        """Определяет интент сообщения"""
        
        message_lower = message.lower()
        
        # Проверяем совпадения с примерами интентов
        active_intents = AIIntent.objects.filter(is_active=True)
        
        for intent in active_intents:
            examples = intent.examples
            for example in examples:
                if example.lower() in message_lower:
                    return intent
        
        # Если интент не определен, возвращаем None
        return None

    def _generate_response(self, message, conversation, intent):
        """Генерирует ответ на основе интента и контекста"""
        
        # Если есть интент, используем его ответ
        if intent and intent.response_template:
            return self._fill_template(intent.response_template, conversation)
        
        # Проверяем базу знаний
        kb_response = self._check_knowledge_base(message)
        if kb_response:
            return kb_response
        
        # Используем OpenAI GPT для генерации ответа
        return self._generate_gpt_response(message, conversation)

    def _fill_template(self, template, conversation):
        """Заполняет шаблон данными из контекста"""
        
        context = conversation.context
        
        # Добавляем данные из заявки, если есть
        if conversation.application:
            app = conversation.application
            context.update({
                'application_number': app.number,
                'application_status': app.get_status_display(),
                'application_type': app.get_application_type_display(),
                'application_subject': app.subject,
                'application_amount': str(app.amount) if app.amount else 'Не указана'
            })
        
        # Заменяем плейсхолдеры
        for key, value in context.items():
            template = template.replace(f'{{{key}}}', str(value))
        
        return template

    def _check_knowledge_base(self, message):
        """Проверяет базу знаний"""
        
        message_lower = message.lower()
        
        # Ищем совпадения по ключевым словам
        knowledge_items = AIKnowledgeBase.objects.filter(is_active=True)
        
        for item in knowledge_items:
            keywords = item.keywords
            for keyword in keywords:
                if keyword.lower() in message_lower:
                    return item.answer
        
        return None

    def _generate_gpt_response(self, message, conversation):
        """Генерирует ответ с помощью GPT"""
        
        try:
            # Формируем контекст для GPT
            messages = [
                {"role": "system", "content": self._get_system_prompt()}
            ]
            
            # Добавляем историю сообщений
            for msg in conversation.messages.order_by('created_at')[:10]:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Добавляем текущее сообщение
            messages.append({"role": "user", "content": message})
            
            # Вызываем GPT
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"GPT API error: {str(e)}")
            return "Извините, я временно не могу обработать ваш запрос. Попробуйте позже."

    def _get_system_prompt(self):
        """Возвращает системный промт для GPT"""
        
        return """
        Ты - помощник в системе Kenes Hub для реструктуризации долгов в Казахстане.
        Ты помогаешь пользователям с:
        1. Информацией о процедуре реструктуризации
        2. Подготовкой документов
        3. Ответами на частые вопросы
        4. Напоминаниями о сроках
        
        Отвечай на русском языке, будь вежлив и информативен.
        Если не знаешь ответа, скажи об этом честно.
        """

    def get_faq_response(self, question):
        """Возвращает ответ на частый вопрос"""
        
        faqs = {
            "как подать заявку": "Для подачи заявки на реструктуризацию долга, перейдите в раздел 'Заявки' и нажмите 'Создать заявку'.",
            "какие документы нужны": "Для реструктуризации потребуются: паспорт, договор займа, справка о доходах, документы на имущество.",
            "сколько длится процедура": "Процедура реструктуризации обычно занимает от 2 до 4 недель.",
            "можно ли отменить заявку": "Да, заявку можно отменить до начала рассмотрения в банке.",
            "как подписать документы": "Документы можно подписать с помощью ЭЦП или SMS-кода.",
        }
        
        question_lower = question.lower()
        for key, answer in faqs.items():
            if key in question_lower:
                return answer
        
        return None

    def _update_usage_stats(self, user):
        """Обновляет статистику использования"""
        
        today = timezone.now().date()
        stats, created = AIUsageStats.objects.get_or_create(
            user=user,
            date=today,
            defaults={'requests_count': 0, 'tokens_used': 0, 'conversations_count': 0}
        )
        
        stats.requests_count += 1
        stats.save()

    def process_reminders(self):
        """Обрабатывает напоминания"""
        
        from apps.applications.models import Application
        from apps.notifications.services import NotificationService
        from apps.notifications.models import NotificationType, NotificationChannel
        
        # Напоминания о дедлайнах
        applications = Application.objects.filter(
            deadline__isnull=False,
            status__in=['in_progress', 'pending_documents', 'under_review']
        )
        
        for app in applications:
            time_until_deadline = app.deadline - timezone.now()
            
            # Напоминаем за 24 часа
            if time_until_deadline.total_seconds() <= 24 * 3600:
                NotificationService.send_deadline_reminder(app)

    def get_conversation_history(self, session_id, limit=50):
        """Возвращает историю диалога"""
        
        try:
            conversation = AIConversation.objects.get(session_id=session_id)
            messages = conversation.messages.order_by('-created_at')[:limit]
            
            return [
                {
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.created_at,
                    'intent': msg.intent.name if msg.intent else None
                }
                for msg in reversed(messages)
            ]
        except AIConversation.DoesNotExist:
            return []

    def close_conversation(self, session_id):
        """Закрывает диалог"""
        
        try:
            conversation = AIConversation.objects.get(session_id=session_id)
            conversation.is_active = False
            conversation.save()
            return True
        except AIConversation.DoesNotExist:
            return False