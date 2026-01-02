from django.contrib import admin
from .models import DocumentTemplate, GeneratedDocument, DocumentSignature, DocumentVersion


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'document_type', 'is_active', 'created_at')
    list_filter = ('document_type', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(GeneratedDocument)
class GeneratedDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'template', 'application', 'created_by', 'status', 
        'signature_status', 'created_at', 'signed_at'
    )
    list_filter = ('status', 'signature_status', 'created_at', 'template')
    search_fields = ('application__number', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DocumentSignature)
class DocumentSignatureAdmin(admin.ModelAdmin):
    list_display = ('document', 'signer', 'signature_type', 'status', 'created_at', 'signed_at')
    list_filter = ('signature_type', 'status', 'created_at')
    search_fields = ('document__template__name', 'signer__username')
    readonly_fields = ('created_at', 'signed_at')


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ('document', 'version_number', 'created_by', 'created_at')
    search_fields = ('document__template__name', 'created_by__username')
    readonly_fields = ('created_at',)