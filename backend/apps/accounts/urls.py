from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('current/', views.current_user, name='current-user'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('documents/', views.UserDocumentListView.as_view(), name='document-list'),
    path('documents/<int:pk>/', views.UserDocumentDetailView.as_view(), name='document-detail'),
    path('verify/phone/', views.verify_phone, name='verify-phone'),
    path('verify/email/', views.verify_email, name='verify-email'),
]
