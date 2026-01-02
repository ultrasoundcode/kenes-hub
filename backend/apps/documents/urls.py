from django.urls import path
from . import views

urlpatterns = [
    path('templates/', views.DocumentTemplateListView.as_view(), name='template-list'),
    path('templates/<str:code>/', views.DocumentTemplateDetailView.as_view(), name='template-detail'),
    path('', views.GeneratedDocumentListView.as_view(), name='document-list'),
    path('<int:pk>/', views.GeneratedDocumentDetailView.as_view(), name='document-detail'),
    path('<int:pk>/download/', views.download_document, name='document-download'),
    path('<int:document_id>/signatures/', views.DocumentSignatureListView.as_view(), name='signature-list'),
    path('verify-sms/', views.verify_sms_code, name='verify-sms'),
    path('<int:document_id>/versions/', views.DocumentVersionListView.as_view(), name='version-list'),
]