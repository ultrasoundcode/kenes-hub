from django.urls import path
from . import views

urlpatterns = [
    path('', views.ApplicationListView.as_view(), name='application-list'),
    path('stats/', views.application_stats, name='application-stats'),
    path('<int:pk>/', views.ApplicationDetailView.as_view(), name='application-detail'),
    path('<int:pk>/status/', views.ApplicationStatusUpdateView.as_view(), name='application-status'),
    path('<int:pk>/assign/', views.assign_application, name='application-assign'),
    path('<int:application_id>/history/', views.ApplicationHistoryListView.as_view(), name='application-history'),
    path('<int:application_id>/comments/', views.ApplicationCommentListView.as_view(), name='application-comments'),
]