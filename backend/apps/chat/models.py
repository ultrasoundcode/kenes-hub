from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ChatRoom(models.Model):
    name = models.CharField(_('Название'), max_length=255)
    application = models.ForeignKey(
        'applications.Application',
        on_delete=models.CASCADE,
        related_name='chat_rooms',
        verbose_name=_('Заявка')
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='chat_rooms',
        verbose_name=_('Участники')
    )
    is_active = models.BooleanField(_('Активна'), default=True)
    created_at = models.DateTimeField(_('Создана'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлена'), auto_now=True)

    class Meta:
        verbose_name = _('Чат комната')
        verbose_name_plural = _('Чат комнаты')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} - {self.application.number}"


class ChatMessage(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Текст'),
        ('file', 'Файл'),
        ('system', 'Системное'),
    ]
    
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('Комната')
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        verbose_name=_('Автор')
    )
    content = models.TextField(_('Содержание'))
    message_type = models.CharField(
        _('Тип сообщения'),
        max_length=20,
        choices=MESSAGE_TYPES,
        default='text'
    )
    file = models.FileField(
        _('Файл'),
        upload_to='chat_files/',
        blank=True,
        null=True
    )
    is_read = models.BooleanField(_('Прочитано'), default=False)
    read_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='read_messages',
        blank=True,
        verbose_name=_('Прочитали')
    )
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлено'), auto_now=True)

    class Meta:
        verbose_name = _('Сообщение чата')
        verbose_name_plural = _('Сообщения чата')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author}: {self.content[:50]}"


class ChatAttachment(models.Model):
    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('Сообщение')
    )
    file = models.FileField(_('Файл'), upload_to='chat_attachments/')
    filename = models.CharField(_('Имя файла'), max_length=255)
    file_size = models.IntegerField(_('Размер файла'))
    mime_type = models.CharField(_('MIME тип'), max_length=100)
    created_at = models.DateTimeField(_('Создан'), auto_now_add=True)

    class Meta:
        verbose_name = _('Вложение чата')
        verbose_name_plural = _('Вложения чата')

    def __str__(self):
        return self.filename