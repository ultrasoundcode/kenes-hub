from rest_framework import serializers
from .models import (
    DocumentTemplate, GeneratedDocument, 
    DocumentSignature, DocumentVersion
)


class DocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class DocumentTemplateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = ('id', 'name', 'code', 'description', 'document_type', 'is_active')


class GeneratedDocumentSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    signed_by_name = serializers.CharField(source='signed_by.get_full_name', read_only=True)

    class Meta:
        model = GeneratedDocument
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'version')


class GeneratedDocumentListSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    application_number = serializers.CharField(source='application.number', read_only=True)

    class Meta:
        model = GeneratedDocument
        fields = (
            'id', 'template', 'template_name', 'application', 
            'application_number', 'status', 'signature_status',
            'created_at', 'signed_at'
        )


class DocumentGenerationSerializer(serializers.Serializer):
    template_id = serializers.IntegerField()
    application_id = serializers.IntegerField()
    field_values = serializers.JSONField(default=dict)


class DocumentSignatureSerializer(serializers.ModelSerializer):
    signer_name = serializers.CharField(source='signer.get_full_name', read_only=True)

    class Meta:
        model = DocumentSignature
        fields = '__all__'
        read_only_fields = ('created_at', 'signed_at')


class DocumentSignatureCreateSerializer(serializers.Serializer):
    signature_type = serializers.ChoiceField(choices=DocumentSignature.SIGNATURE_TYPES)
    signer_id = serializers.IntegerField()


class SMSVerificationSerializer(serializers.Serializer):
    signature_id = serializers.IntegerField()
    code = serializers.CharField(max_length=6)


class DocumentVersionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = DocumentVersion
        fields = '__all__'
        read_only_fields = ('created_at',)