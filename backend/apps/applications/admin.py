from django.contrib import admin
from .models import Application, ApplicationHistory, ApplicationComment


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'number', 'subject', 'applicant', 'application_type', 
        'status', 'priority', 'assigned_to', 'created_at'
    )
    list_filter = (
        'status', 'application_type', 'source', 'priority', 
        'created_at', 'updated_at'
    )
    search_fields = ('number', 'subject', 'applicant__username', 'creditor_name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_editable = ('status', 'priority', 'assigned_to')

    fieldsets = (
        ('Основная информация', {
            'fields': ('number', 'subject', 'applicant', 'description')
        }),
        ('Тип и источник', {
            'fields': ('application_type', 'source', 'status', 'priority')
        }),
        ('Финансовая информация', {
            'fields': ('amount', 'creditor_name', 'contract_number')
        }),
        ('Назначение', {
            'fields': ('assigned_to', 'deadline')
        }),
        ('Дополнительно', {
            'fields': ('metadata', 'tags', 'parent_application')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ApplicationHistory)
class ApplicationHistoryAdmin(admin.ModelAdmin):
    list_display = ('application', 'user', 'action', 'old_status', 'new_status', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('application__number', 'user__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'


@admin.register(ApplicationComment)
class ApplicationCommentAdmin(admin.ModelAdmin):
    list_display = ('application', 'author', 'is_internal', 'created_at')
    list_filter = ('is_internal', 'created_at')
    search_fields = ('application__number', 'author__username', 'content')
    readonly_fields = ('created_at', 'updated_at')