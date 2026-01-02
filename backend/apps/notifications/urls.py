from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('unread-count/', views.unread_count, name='unread-count'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('<int:pk>/read/', views.mark_as_read, name='mark-as-read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark-all-read'),
    path('templates/', views.NotificationTemplateListView.as_view(), name='template-list'),
    path('settings/', views.UserNotificationSettingsView.as_view(), name='settings'),
]