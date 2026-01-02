from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class NotificationChannel(models.TextChoices):
    EMAIL = 'email', _('Email')
    SMS = 'sms', _('SMS')
    PUSH = 'push', _('Push-уведомление')
    WHATSAPP = 'whatsapp', _('WhatsApp')
    TELEGRAM = 'telegram', _('Telegram')


class NotificationType(models.TextChoices):
    APPLICATION_CREATED = 'application_created', _('Создана заявка')
    APPLICATION_STATUS_CHANGED = 'application_status_changed', _('Изменен статус заявки')
    DOCUMENT_GENERATED = 'document_generated', _('Сгенерирован документ')
    DOCUMENT_SIGNED = 'document_signed', _('Документ подписан')
    DEADLINE_APPROACHING = 'deadline_approaching', _('Приближается дедлайн')
    REMINDER = 'reminder', _('Напоминание')
    SYSTEM = 'system', _('Системное уведомление')
    NEWS = 'news', _('Новости')


class NotificationStatus(models.TextChoices):
    PENDING = 'pending', _('Ожидает отправки')
    SENT = 'sent', _('Отправлено')
    DELIVERED = 'delivered', _('Доставлено')
    FAILED = 'failed', _('Ошибка отправки')
    READ = 'read', _('Прочитано')


class NotificationTemplate(models.Model):
    name = models.CharField(_('Название'), max_length=255)
    code = models.CharField(_('Код'), max_length=50, unique=True)
    description = models.TextField(_('Описание'), blank=True)
    
    # Шаблоны для разных каналов
    email_subject = models.CharField(_('Тема email'), max_length=500, blank=True)
    email_body = models.TextField(_('Тело email'), blank=True)
    email_html = models.TextField(_('HTML email'), blank=True)
    sms_template = models.CharField(_('SMS шаблон'), max_length=500, blank=True)
    push_title = models.CharField(_('Заголовок push'), max_length=100, blank=True)
    push_body = models.CharField(_('Тело push'), max_length=500, blank=True)
    
    # Настройки
    channels = models.JSONField(_('Каналы'), default=list)
    is_active = models.BooleanField(_('Активен'), default=True)
    created_at = models.DateTimeField(_('Создан'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлен'), auto_now=True)

    class Meta:
        verbose_name = _('Шаблон уведомления')
        verbose_name_plural = _('Шаблоны уведомлений')
        ordering = ['name']

    def __str__(self):
        return self.name


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Получатель')
    )
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Шаблон')
    )
    
    # Тип и канал
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        verbose_name=_('Тип уведомления')
    )
    channel = models.CharField(
        max_length=20,
        choices=NotificationChannel.choices,
        verbose_name=_('Канал')
    )
    
    # Содержимое
    title = models.CharField(_('Заголовок'), max_length=500, blank=True)
    message = models.TextField(_('Сообщение'))
    data = models.JSONField(_('Данные'), default=dict)
    
    # Статус
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
        verbose_name=_('Статус')
    )
    
    # Попытки отправки
    attempts = models.IntegerField(_('Попытки отправки'), default=0)
    max_attempts = models.IntegerField(_('Максимум попыток'), default=3)
    
    # Отправка
    scheduled_at = models.DateTimeField(_('Запланировано на'), null=True, blank=True)
    sent_at = models.DateTimeField(_('Отправлено'), null=True, blank=True)
    delivered_at = models.DateTimeField(_('Доставлено'), null=True, blank=True)
    read_at = models.DateTimeField(_('Прочитано'), null=True, blank=True)
    
    # Ошибки
    error_message = models.TextField(_('Сообщение об ошибке'), blank=True)
    
    # Связанные объекты
    related_application = models.ForeignKey(
        'applications.Application',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name=_('Связанная заявка')
    )
    related_document = models.ForeignKey(
        'documents.GeneratedDocument',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name=_('Связанный документ')
    )
    
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлено'), auto_now=True)

    class Meta:
        verbose_name = _('Уведомление')
        verbose_name_plural = _('Уведомления')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient}"


class EmailOutbox(models.Model):
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='email_outbox',
        verbose_name=_('Уведомление')
    )
    recipient_email = models.EmailField(_('Email получателя'))
    subject = models.CharField(_('Тема'), max_length=500)
    body = models.TextField(_('Тело письма'))
    html_body = models.TextField(_('HTML тело'), blank=True)
    headers = models.JSONField(_('Заголовки'), default=dict)
    attachments = models.JSONField(_('Вложения'), default=list)
    
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
        verbose_name=_('Статус')
    )
    
    sent_at = models.DateTimeField(_('Отправлено'), null=True, blank=True)
    error_message = models.TextField(_('Сообщение об ошибке'), blank=True)
    
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)

    class Meta:
        verbose_name = _('Исходящее письмо')
        verbose_name_plural = _('Исходящие письма')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.recipient_email}"


class SMSOutbox(models.Model):
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='sms_outbox',
        verbose_name=_('Уведомление')
    )
    recipient_phone = models.CharField(_('Телефон получателя'), max_length=20)
    message = models.CharField(_('Сообщение'), max_length=500)
    
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
        verbose_name=_('Статус')
    )
    
    sms_id = models.CharField(_('ID SMS в провайдере'), max_length=100, blank=True)
    sent_at = models.DateTimeField(_('Отправлено'), null=True, blank=True)
    delivered_at = models.DateTimeField(_('Доставлено'), null=True, blank=True)
    error_message = models.TextField(_('Сообщение об ошибке'), blank=True)
    
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)

    class Meta:
        verbose_name = _('Исходящее SMS')
        verbose_name_plural = _('Исходящие SMS')
        ordering = ['-created_at']

    def __str__(self):
        return f"SMS to {self.recipient_phone}"


class UserNotificationSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_settings',
        verbose_name=_('Пользователь')
    )
    
    # Настройки каналов
    email_enabled = models.BooleanField(_('Email уведомления'), default=True)
    sms_enabled = models.BooleanField(_('SMS уведомления'), default=True)
    push_enabled = models.BooleanField(_('Push уведомления'), default=True)
    whatsapp_enabled = models.BooleanField(_('WhatsApp уведомления'), default=False)
    
    # Настройки типов уведомлений
    application_notifications = models.BooleanField(_('Уведомления о заявках'), default=True)
    document_notifications = models.BooleanField(_('Уведомления о документах'), default=True)
    deadline_notifications = models.BooleanField(_('Напоминания о сроках'), default=True)
    system_notifications = models.BooleanField(_('Системные уведомления'), default=True)
    news_notifications = models.BooleanField(_('Новости'), default=False)
    
    # Рабочее время
    work_hours_only = models.BooleanField(_('Только в рабочее время'), default=False)
    work_start = models.TimeField(_('Начало рабочего дня'), default='09:00')
    work_end = models.TimeField(_('Конец рабочего дня'), default='18:00')
    
    # Тихий режим
    quiet_hours_start = models.TimeField(_('Начало тихого режима'), null=True, blank=True)
    quiet_hours_end = models.TimeField(_('Конец тихого режима'), null=True, blank=True)
    
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлено'), auto_now=True)

    class Meta:
        verbose_name = _('Настройки уведомлений')
        verbose_name_plural = _('Настройки уведомлений')

    def __str__(self):
        return f"Настройки {self.user}"