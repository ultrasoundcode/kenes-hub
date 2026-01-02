from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class DocumentTemplate(models.Model):
    name = models.CharField(_('Название'), max_length=255)
    code = models.CharField(_('Код'), max_length=50, unique=True)
    description = models.TextField(_('Описание'), blank=True)
    template_file = models.FileField(_('Файл шаблона'), upload_to='templates/')
    document_type = models.CharField(_('Тип документа'), max_length=50)
    application_types = models.JSONField(_('Типы заявок'), default=list)
    required_fields = models.JSONField(_('Обязательные поля'), default=list)
    is_active = models.BooleanField(_('Активен'), default=True)
    created_at = models.DateTimeField(_('Создан'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлен'), auto_now=True)

    class Meta:
        verbose_name = _('Шаблон документа')
        verbose_name_plural = _('Шаблоны документов')
        ordering = ['name']

    def __str__(self):
        return self.name


class GeneratedDocument(models.Model):
    template = models.ForeignKey(
        DocumentTemplate,
        on_delete=models.CASCADE,
        related_name='generated_documents',
        verbose_name=_('Шаблон')
    )
    application = models.ForeignKey(
        'applications.Application',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('Заявка')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_documents',
        verbose_name=_('Создал')
    )
    
    # Файлы
    original_file = models.FileField(_('Оригинальный файл'), upload_to='documents/original/')
    signed_file = models.FileField(_('Подписанный файл'), upload_to='documents/signed/', blank=True, null=True)
    
    # Данные документа
    document_data = models.JSONField(_('Данные документа'), default=dict)
    field_values = models.JSONField(_('Значения полей'), default=dict)
    
    # Подписание
    signature_type = models.CharField(_('Тип подписи'), max_length=20, blank=True)
    signature_status = models.CharField(_('Статус подписания'), max_length=20, default='pending')
    signed_at = models.DateTimeField(_('Подписан'), null=True, blank=True)
    signed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='signed_documents',
        verbose_name=_('Подписал')
    )
    
    # Статус
    status = models.CharField(_('Статус'), max_length=20, default='draft')
    version = models.IntegerField(_('Версия'), default=1)
    
    # Отправка
    sent_at = models.DateTimeField(_('Отправлен'), null=True, blank=True)
    sent_to = models.JSONField(_('Получатели'), default=list)
    
    created_at = models.DateTimeField(_('Создан'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлен'), auto_now=True)

    class Meta:
        verbose_name = _('Сгенерированный документ')
        verbose_name_plural = _('Сгенерированные документы')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.template.name} - {self.application.number}"


class DocumentSignature(models.Model):
    SIGNATURE_TYPES = [
        ('ecp', 'ЭЦП'),
        ('sms', 'SMS-код'),
        ('handwritten', 'Рукописная'),
    ]
    
    SIGNATURE_STATUS = [
        ('pending', 'Ожидает'),
        ('in_progress', 'В процессе'),
        ('signed', 'Подписан'),
        ('failed', 'Ошибка'),
        ('cancelled', 'Отменен'),
    ]
    
    document = models.ForeignKey(
        GeneratedDocument,
        on_delete=models.CASCADE,
        related_name='signatures',
        verbose_name=_('Документ')
    )
    signer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='document_signatures',
        verbose_name=_('Подписывающий')
    )
    signature_type = models.CharField(
        _('Тип подписи'),
        max_length=20,
        choices=SIGNATURE_TYPES
    )
    status = models.CharField(
        _('Статус'),
        max_length=20,
        choices=SIGNATURE_STATUS,
        default='pending'
    )
    
    # Для SMS
    sms_code = models.CharField(_('SMS код'), max_length=6, blank=True)
    sms_sent_at = models.DateTimeField(_('SMS отправлен'), null=True, blank=True)
    sms_attempts = models.IntegerField(_('Попытки SMS'), default=0)
    
    # Для ЭЦП
    certificate_info = models.JSONField(_('Информация о сертификате'), default=dict)
    
    # Результат
    signature_data = models.JSONField(_('Данные подписи'), default=dict)
    error_message = models.TextField(_('Сообщение об ошибке'), blank=True)
    
    created_at = models.DateTimeField(_('Создан'), auto_now_add=True)
    signed_at = models.DateTimeField(_('Подписан'), null=True, blank=True)

    class Meta:
        verbose_name = _('Подписание документа')
        verbose_name_plural = _('подписания документов')
        ordering = ['-created_at']
        unique_together = ['document', 'signer']

    def __str__(self):
        return f"{self.document} - {self.signer}"


class DocumentVersion(models.Model):
    document = models.ForeignKey(
        GeneratedDocument,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name=_('Документ')
    )
    version_number = models.IntegerField(_('Номер версии'))
    file = models.FileField(_('Файл'), upload_to='documents/versions/')
    changes = models.TextField(_('Изменения'), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='document_versions',
        verbose_name=_('Создал')
    )
    created_at = models.DateTimeField(_('Создана'), auto_now_add=True)

    class Meta:
        verbose_name = _('Версия документа')
        verbose_name_plural = _('Версии документов')
        ordering = ['-version_number']
        unique_together = ['document', 'version_number']

    def __str__(self):
        return f"{self.document} v{self.version_number}"