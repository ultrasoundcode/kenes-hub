from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    ADMIN = 'admin', _('Администратор')
    BORROWER = 'borrower', _('Заемщик')
    CREDITOR = 'creditor', _('Кредитор')
    MEDIATOR = 'mediator', _('Медиатор')
    NOTARY = 'notary', _('Нотариус')
    MANAGER = 'manager', _('Менеджер')


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.BORROWER
    )
    phone = models.CharField(_('Телефон'), max_length=20, blank=True)
    iin = models.CharField(_('ИИН'), max_length=12, blank=True, unique=True, null=True)
    organization = models.CharField(_('Организация'), max_length=255, blank=True)
    position = models.CharField(_('Должность'), max_length=255, blank=True)
    is_verified = models.BooleanField(_('Верифицирован'), default=False)
    email_verified = models.BooleanField(_('Email подтвержден'), default=False)
    phone_verified = models.BooleanField(_('Телефон подтвержден'), default=False)
    created_at = models.DateTimeField(_('Создан'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлен'), auto_now=True)

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(_('Аватар'), upload_to='avatars/', blank=True)
    address = models.TextField(_('Адрес'), blank=True)
    city = models.CharField(_('Город'), max_length=100, blank=True)
    region = models.CharField(_('Область'), max_length=100, blank=True)
    postal_code = models.CharField(_('Почтовый индекс'), max_length=10, blank=True)
    additional_info = models.JSONField(_('Дополнительная информация'), default=dict, blank=True)
    created_at = models.DateTimeField(_('Создан'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлен'), auto_now=True)

    class Meta:
        verbose_name = _('Профиль пользователя')
        verbose_name_plural = _('Профили пользователей')

    def __str__(self):
        return f"Профиль {self.user}"


class UserDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(_('Тип документа'), max_length=50)
    file = models.FileField(_('Файл'), upload_to='user_documents/')
    verified = models.BooleanField(_('Проверен'), default=False)
    uploaded_at = models.DateTimeField(_('Загружен'), auto_now_add=True)

    class Meta:
        verbose_name = _('Документ пользователя')
        verbose_name_plural = _('Документы пользователя')

    def __str__(self):
        return f"{self.document_type} - {self.user}"