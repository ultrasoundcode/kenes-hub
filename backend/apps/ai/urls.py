from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.AIChatView.as_view(), name='ai-chat'),
    path('conversations/', views.AIConversationListView.as_view(), name='conversation-list'),
    path('conversations/<str:pk>/', views.AIConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<str:session_id>/history/', views.conversation_history, name='conversation-history'),
    path('conversations/<str:session_id>/close/', views.close_conversation, name='close-conversation'),
    path('knowledge/', views.AIKnowledgeBaseListView.as_view(), name='knowledge-list'),
    path('stats/', views.AIUsageStatsView.as_view(), name='usage-stats'),
    path('faq/', views.faq_search, name='faq-search'),
]