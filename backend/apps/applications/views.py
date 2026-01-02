from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from .models import Application, ApplicationHistory, ApplicationComment
from .serializers import (
    ApplicationSerializer, ApplicationListSerializer,
    ApplicationHistorySerializer, ApplicationCommentSerializer,
    ApplicationStatusUpdateSerializer, ApplicationStatsSerializer
)
from .filters import ApplicationFilter

User = get_user_model()


class ApplicationListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ApplicationFilter

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ApplicationSerializer
        return ApplicationListSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'manager']:
            return Application.objects.select_related('applicant', 'assigned_to').all()
        elif user.role in ['mediator', 'notary', 'creditor']:
            return Application.objects.filter(
                Q(applicant=user) | Q(assigned_to=user)
            ).select_related('applicant', 'assigned_to').distinct()
        else:
            return Application.objects.filter(applicant=user).select_related('applicant', 'assigned_to')

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)


class ApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'manager']:
            return Application.objects.all()
        return Application.objects.filter(applicant=user)


class ApplicationStatusUpdateView(generics.UpdateAPIView):
    serializer_class = ApplicationStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'manager']:
            return Application.objects.all()
        return Application.objects.filter(assigned_to=user)


class ApplicationHistoryListView(generics.ListAPIView):
    serializer_class = ApplicationHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        application_id = self.kwargs.get('application_id')
        user = self.request.user
        
        if user.role in ['admin', 'manager']:
            return ApplicationHistory.objects.filter(application_id=application_id)
        
        # Проверяем доступ пользователя к заявке
        if Application.objects.filter(
            Q(id=application_id) & 
            (Q(applicant=user) | Q(assigned_to=user))
        ).exists():
            return ApplicationHistory.objects.filter(application_id=application_id)
        
        return ApplicationHistory.objects.none()


class ApplicationCommentListView(generics.ListCreateAPIView):
    serializer_class = ApplicationCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        application_id = self.kwargs.get('application_id')
        user = self.request.user
        
        base_query = ApplicationComment.objects.filter(application_id=application_id)
        
        if user.role in ['admin', 'manager']:
            return base_query
        
        # Фильтруем внутренние комментарии для обычных пользователей
        return base_query.filter(is_internal=False)

    def perform_create(self, serializer):
        application_id = self.kwargs.get('application_id')
        serializer.save(
            application_id=application_id,
            author=self.request.user
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def application_stats(request):
    user = request.user
    
    # Базовый queryset с учетом роли
    if user.role in ['admin', 'manager']:
        base_query = Application.objects.all()
    else:
        base_query = Application.objects.filter(
            Q(applicant=user) | Q(assigned_to=user)
        )
    
    # Статистика
    total = base_query.count()
    by_status = dict(base_query.values_list('status').annotate(count=Count('id')))
    by_type = dict(base_query.values_list('application_type').annotate(count=Count('id')))
    by_source = dict(base_query.values_list('source').annotate(count=Count('id')))
    
    # Заявки за текущий месяц
    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    this_month = base_query.filter(created_at__gte=start_of_month).count()
    
    # Завершенные за месяц
    completed_this_month = base_query.filter(
        status='completed',
        completed_at__gte=start_of_month
    ).count()
    
    data = {
        'total': total,
        'by_status': by_status,
        'by_type': by_type,
        'by_source': by_source,
        'this_month': this_month,
        'completed_this_month': completed_this_month
    }
    
    serializer = ApplicationStatsSerializer(data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def assign_application(request, pk):
    try:
        application = Application.objects.get(pk=pk)
        user = request.user
        
        # Проверка прав
        if user.role not in ['admin', 'manager']:
            return Response(
                {'error': 'Недостаточно прав'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        assigned_to_id = request.data.get('assigned_to')
        if assigned_to_id:
            assigned_to = User.objects.get(pk=assigned_to_id)
            application.assigned_to = assigned_to
            application.save()
            
            ApplicationHistory.objects.create(
                application=application,
                user=user,
                action='Назначение ответственного',
                comment=f'Назначен: {assigned_to.get_full_name()}'
            )
            
            return Response({'message': 'Ответственный назначен'})
        
        return Response(
            {'error': 'Не указан ответственный'},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    except Application.DoesNotExist:
        return Response(
            {'error': 'Заявка не найдена'},
            status=status.HTTP_404_NOT_FOUND
        )
    except User.DoesNotExist:
        return Response(
            {'error': 'Пользователь не найден'},
            status=status.HTTP_404_NOT_FOUND
        )