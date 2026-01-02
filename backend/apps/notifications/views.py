from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Notification, NotificationTemplate, UserNotificationSettings
from .serializers import (
    NotificationSerializer, NotificationTemplateSerializer,
    UserNotificationSettingsSerializer
)
from .services import NotificationService


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('template', 'related_application', 'related_document')


class NotificationDetailView(generics.RetrieveAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unread_count(request):
    """Возвращает количество непрочитанных уведомлений"""
    
    count = NotificationService.get_unread_count(request.user)
    return Response({'unread_count': count})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_as_read(request, pk):
    """Отмечает уведомление как прочитанное"""
    
    success = NotificationService.mark_as_read(request.user, pk)
    if success:
        return Response({'message': 'Уведомление отмечено как прочитанное'})
    else:
        return Response(
            {'error': 'Уведомление не найдено'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_as_read(request):
    """Отмечает все уведомления как прочитанные"""
    
    Notification.objects.filter(
        recipient=request.user,
        status__in=['pending', 'sent', 'delivered']
    ).update(
        status='read',
        read_at=timezone.now()
    )
    
    return Response({'message': 'Все уведомления отмечены как прочитанные'})


class NotificationTemplateListView(generics.ListAPIView):
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = NotificationTemplate.objects.filter(is_active=True)


class UserNotificationSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = UserNotificationSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        settings, created = UserNotificationSettings.objects.get_or_create(
            user=self.request.user
        )
        return settings