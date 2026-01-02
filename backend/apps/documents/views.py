from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import DocumentTemplate, GeneratedDocument, DocumentSignature, DocumentVersion
from .serializers import (
    DocumentTemplateSerializer, DocumentTemplateListSerializer,
    GeneratedDocumentSerializer, GeneratedDocumentListSerializer,
    DocumentGenerationSerializer, DocumentSignatureSerializer,
    DocumentSignatureCreateSerializer, SMSVerificationSerializer,
    DocumentVersionSerializer
)
from .services import DocumentService
from .tasks import generate_document_task, send_sms_code_task


class DocumentTemplateListView(generics.ListAPIView):
    serializer_class = DocumentTemplateListSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DocumentTemplate.objects.filter(is_active=True)


class DocumentTemplateDetailView(generics.RetrieveAPIView):
    serializer_class = DocumentTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = DocumentTemplate.objects.filter(is_active=True)
    lookup_field = 'code'


class GeneratedDocumentListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DocumentGenerationSerializer
        return GeneratedDocumentListSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'manager']:
            return GeneratedDocument.objects.select_related('template', 'application', 'created_by').all()
        return GeneratedDocument.objects.filter(
            created_by=user
        ).select_related('template', 'application', 'created_by')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        template_id = serializer.validated_data['template_id']
        application_id = serializer.validated_data['application_id']
        field_values = serializer.validated_data.get('field_values', {})
        
        # Асинхронная генерация документа
        task = generate_document_task.delay(
            template_id, application_id, request.user.id, field_values
        )
        
        return Response({
            'task_id': task.id,
            'message': 'Документ отправлен на генерацию'
        }, status=status.HTTP_202_ACCEPTED)


class GeneratedDocumentDetailView(generics.RetrieveAPIView):
    serializer_class = GeneratedDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'manager']:
            return GeneratedDocument.objects.all()
        return GeneratedDocument.objects.filter(created_by=user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_document(request, pk):
    document = get_object_or_404(GeneratedDocument, pk=pk)
    
    # Проверка прав доступа
    user = request.user
    if user.role not in ['admin', 'manager'] and document.created_by != user:
        return Response(
            {'error': 'Нет доступа к документу'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    file_field = document.signed_file if document.signed_file else document.original_file
    
    response = HttpResponse(file_field, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{document.template.name}.pdf"'
    return response


class DocumentSignatureListView(generics.ListCreateAPIView):
    serializer_class = DocumentSignatureSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        document_id = self.kwargs.get('document_id')
        return DocumentSignature.objects.filter(document_id=document_id)

    def create(self, request, *args, **kwargs):
        document_id = self.kwargs.get('document_id')
        document = get_object_or_404(GeneratedDocument, pk=document_id)
        
        serializer = DocumentSignatureCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        signature_type = serializer.validated_data['signature_type']
        signer_id = serializer.validated_data['signer_id']
        
        # Создаем запись о подписании
        signature, created = DocumentSignature.objects.get_or_create(
            document=document,
            signer_id=signer_id,
            defaults={'signature_type': signature_type}
        )
        
        if signature_type == 'sms':
            # Отправляем SMS код
            send_sms_code_task.delay(signature.id)
            return Response({
                'message': 'SMS код отправлен',
                'signature_id': signature.id
            })
        
        serializer = DocumentSignatureSerializer(signature)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_sms_code(request):
    serializer = SMSVerificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    signature_id = serializer.validated_data['signature_id']
    code = serializer.validated_data['code']
    
    signature = get_object_or_404(DocumentSignature, pk=signature_id)
    
    if signature.signature_type != 'sms':
        return Response(
            {'error': 'Неверный тип подписи'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if signature.sms_code == code:
        signature.status = 'signed'
        signature.signed_at = timezone.now()
        signature.save()
        
        # Обновляем статус документа
        signature.document.signature_status = 'signed'
        signature.document.signed_file = signature.document.original_file
        signature.document.signed_by = signature.signer
        signature.document.signed_at = signature.signed_at
        signature.document.save()
        
        return Response({'message': 'Документ успешно подписан'})
    else:
        signature.sms_attempts += 1
        signature.save()
        
        if signature.sms_attempts >= 3:
            signature.status = 'failed'
            signature.save()
            return Response(
                {'error': 'Превышено количество попыток'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {'error': 'Неверный код'},
            status=status.HTTP_400_BAD_REQUEST
        )


class DocumentVersionListView(generics.ListCreateAPIView):
    serializer_class = DocumentVersionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        document_id = self.kwargs.get('document_id')
        return DocumentVersion.objects.filter(document_id=document_id)

    def perform_create(self, serializer):
        document_id = self.kwargs.get('document_id')
        document = get_object_or_404(GeneratedDocument, pk=document_id)
        
        # Проверяем права
        if self.request.user.role not in ['admin', 'manager'] and document.created_by != self.request.user:
            raise PermissionDenied('Нет прав на создание версии')
        
        # Определяем номер версии
        last_version = document.versions.first()
        version_number = (last_version.version_number + 1) if last_version else 2
        
        serializer.save(
            document=document,
            version_number=version_number,
            created_by=self.request.user
        )