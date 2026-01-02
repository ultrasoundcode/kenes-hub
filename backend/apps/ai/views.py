from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import AIConversation, AIMessage, AIKnowledgeBase, AIUsageStats
from .serializers import (
    AIMessageSerializer, AIConversationSerializer,
    AIKnowledgeBaseSerializer, AIUsageStatsSerializer
)
from .services import AIService


class AIChatView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        message = request.data.get('message')
        session_id = request.data.get('session_id')
        application_id = request.data.get('application_id')
        
        if not message:
            return Response(
                {'error': 'Сообщение обязательно'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ai_service = AIService()
        response = ai_service.process_message(
            user=request.user,
            message=message,
            session_id=session_id,
            application_id=application_id
        )
        
        return Response(response)


class AIConversationListView(generics.ListAPIView):
    serializer_class = AIConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AIConversation.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-updated_at')


class AIConversationDetailView(generics.RetrieveAPIView):
    serializer_class = AIConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AIConversation.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def conversation_history(request, session_id):
    """Возвращает историю диалога"""
    
    ai_service = AIService()
    history = ai_service.get_conversation_history(session_id)
    
    return Response({
        'session_id': session_id,
        'messages': history
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def close_conversation(request, session_id):
    """Закрывает диалог"""
    
    ai_service = AIService()
    success = ai_service.close_conversation(session_id)
    
    if success:
        return Response({'message': 'Диалог закрыт'})
    else:
        return Response(
            {'error': 'Диалог не найден'},
            status=status.HTTP_404_NOT_FOUND
        )


class AIKnowledgeBaseListView(generics.ListAPIView):
    serializer_class = AIKnowledgeBaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = AIKnowledgeBase.objects.filter(is_active=True)


class AIUsageStatsView(generics.ListAPIView):
    serializer_class = AIUsageStatsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AIUsageStats.objects.filter(
            user=self.request.user
        ).order_by('-date')[:30]  # Последние 30 дней


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def faq_search(request):
    """Поиск в FAQ"""
    
    query = request.GET.get('q', '')
    if not query:
        return Response(
            {'error': 'Параметр q обязателен'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    ai_service = AIService()
    response = ai_service.get_faq_response(query)
    
    if response:
        return Response({'answer': response})
    else:
        return Response(
            {'message': 'Ответ не найден'},
            status=status.HTTP_404_NOT_FOUND
        )