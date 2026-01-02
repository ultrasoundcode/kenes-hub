from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class AIIntent(models.Model):
    name = models.CharField(_('Название'), max_length=100)
    code = models.CharField(_('Код'), max_length=50, unique=True)
    description = models.TextField(_('Описание'), blank=True)
    examples = models.JSONField(_('Примеры фраз'), default=list)
    parameters = models.JSONField(_('Параметры'), default=dict)
    response_template = models.TextField(_('Шаблон ответа'), blank=True)
    is_active = models.BooleanField(_('Активен'), default=True)
    created_at = models.DateTimeField(_('Создан'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлен'), auto_now=True)

    class Meta:
        verbose_name = _('AI Интент')
        verbose_name_plural = _('AI Интенты')
        ordering = ['name']

    def __str__(self):
        return self.name


class AIConversation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_conversations',
        verbose_name=_('Пользователь')
    )
    application = models.ForeignKey(
        'applications.Application',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ai_conversations',
        verbose_name=_('Заявка')
    )
    session_id = models.CharField(_('ID сессии'), max_length=100, unique=True)
    context = models.JSONField(_('Контекст'), default=dict)
    is_active = models.BooleanField(_('Активна'), default=True)
    created_at = models.DateTimeField(_('Создана'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлена'), auto_now=True)

    class Meta:
        verbose_name = _('AI Диалог')
        verbose_name_plural = _('AI Диалоги')
        ordering = ['-updated_at']

    def __str__(self):
        return f"Диалог {self.user} - {self.session_id[:8]}"


class AIMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('assistant', 'Ассистент'),
        ('system', 'Система'),
    ]
    
    conversation = models.ForeignKey(
        AIConversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('Диалог')
    )
    role = models.CharField(_('Роль'), max_length=20, choices=ROLE_CHOICES)
    content = models.TextField(_('Содержание'))
    intent = models.ForeignKey(
        AIIntent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='messages',
        verbose_name=_('Интент')
    )
    parameters = models.JSONField(_('Параметры'), default=dict)
    tokens_used = models.IntegerField(_('Использовано токенов'), null=True, blank=True)
    processing_time = models.FloatField(_('Время обработки'), null=True, blank=True)
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)

    class Meta:
        verbose_name = _('AI Сообщение')
        verbose_name_plural = _('AI Сообщения')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class AIKnowledgeBase(models.Model):
    category = models.CharField(_('Категория'), max_length=100)
    question = models.TextField(_('Вопрос'))
    answer = models.TextField(_('Ответ'))
    keywords = models.JSONField(_('Ключевые слова'), default=list)
    is_active = models.BooleanField(_('Активен'), default=True)
    created_at = models.DateTimeField(_('Создан'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлен'), auto_now=True)

    class Meta:
        verbose_name = _('База знаний AI')
        verbose_name_plural = _('База знаний AI')
        ordering = ['category', 'question']

    def __str__(self):
        return f"{self.category}: {self.question[:50]}"


class AIUsageStats(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_usage_stats',
        verbose_name=_('Пользователь')
    )
    date = models.DateField(_('Дата'))
    requests_count = models.IntegerField(_('Количество запросов'), default=0)
    tokens_used = models.IntegerField(_('Использовано токенов'), default=0)
    conversations_count = models.IntegerField(_('Количество диалогов'), default=0)
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)

    class Meta:
        verbose_name = _('Статистика использования AI')
        verbose_name_plural = _('Статистика использования AI')
        ordering = ['-date']
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user} - {self.date}"