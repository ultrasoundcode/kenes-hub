from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ApplicationSource(models.TextChoices):
    WHATSAPP = 'whatsapp', _('WhatsApp')
    WEB_FORM = 'web_form', _('Веб-форма')
    EMAIL = 'email', _('Email')
    PHONE = 'phone', _('Телефон')
    MANUAL = 'manual', _('Ручной ввод')


class ApplicationType(models.TextChoices):
    RESTRUCTURING = 'restructuring', _('Реструктуризация')
    MEDIATION = 'mediation', _('Медиация')
    NOTARY = 'notary', _('Нотариус')
    CONSULTATION = 'consultation', _('Консультация')
    COLLECTION = 'collection', _('Взыскание')


class ApplicationStatus(models.TextChoices):
    NEW = 'new', _('Новая')
    IN_PROGRESS = 'in_progress', _('В работе')
    PENDING_DOCUMENTS = 'pending_documents', _('Ожидание документов')
    UNDER_REVIEW = 'under_review', _('На рассмотрении')
    APPROVED = 'approved', _('Одобрено')
    REJECTED = 'rejected', _('Отклонено')
    COMPLETED = 'completed', _('Завершено')
    CANCELLED = 'cancelled', _('Отменено')


class Application(models.Model):
    # Основная информация
    number = models.CharField(_('Номер заявки'), max_length=50, unique=True)
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name=_('Заявитель')
    )
    
    # Источник и тип
    source = models.CharField(
        max_length=20,
        choices=ApplicationSource.choices,
        default=ApplicationSource.WEB_FORM,
        verbose_name=_('Источник')
    )
    application_type = models.CharField(
        max_length=20,
        choices=ApplicationType.choices,
        verbose_name=_('Тип заявки')
    )
    
    # Статус и назначение
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.NEW,
        verbose_name=_('Статус')
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_applications',
        verbose_name=_('Ответственный')
    )
    
    # Данные заявки
    subject = models.CharField(_('Тема'), max_length=255)
    description = models.TextField(_('Описание'), blank=True)
    amount = models.DecimalField(
        _('Сумма долга'),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    creditor_name = models.CharField(_('Кредитор'), max_length=255, blank=True)
    contract_number = models.CharField(_('Номер договора'), max_length=100, blank=True)
    
    # Даты
    created_at = models.DateTimeField(_('Создана'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлена'), auto_now=True)
    deadline = models.DateTimeField(_('Крайний срок'), null=True, blank=True)
    completed_at = models.DateTimeField(_('Завершена'), null=True, blank=True)
    
    # Дополнительные данные
    metadata = models.JSONField(_('Дополнительные данные'), default=dict, blank=True)
    tags = models.CharField(_('Теги'), max_length=500, blank=True)
    priority = models.IntegerField(_('Приоритет'), default=0)
    
    # Связанные данные
    parent_application = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='child_applications',
        verbose_name=_('Родительская заявка')
    )

    class Meta:
        verbose_name = _('Заявка')
        verbose_name_plural = _('Заявки')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.number} - {self.subject}"

    def save(self, *args, **kwargs):
        if not self.number:
            from django.utils import timezone
            self.number = f"APP{timezone.now().strftime('%Y%m%d')}{Application.objects.count() + 1:04d}"
        super().save(*args, **kwargs)


class ApplicationHistory(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_('Заявка')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Пользователь')
    )
    action = models.CharField(_('Действие'), max_length=100)
    old_status = models.CharField(_('Старый статус'), max_length=20, blank=True)
    new_status = models.CharField(_('Новый статус'), max_length=20, blank=True)
    comment = models.TextField(_('Комментарий'), blank=True)
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)

    class Meta:
        verbose_name = _('История заявки')
        verbose_name_plural = _('История заявок')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.application} - {self.action}"


class ApplicationComment(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Заявка')
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('Автор')
    )
    content = models.TextField(_('Содержание'))
    is_internal = models.BooleanField(_('Внутренний'), default=False)
    created_at = models.DateTimeField(_('Создан'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлен'), auto_now=True)

    class Meta:
        verbose_name = _('Комментарий')
        verbose_name_plural = _('Комментарии')
        ordering = ['-created_at']

    def __str__(self):
        return f"Комментарий к {self.application}"