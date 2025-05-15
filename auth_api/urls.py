from django.urls import path
from . import views

app_name = 'auth_api'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('create-test-user/', views.create_test_user, name='create_test_user'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('enseignant-dashboard/', views.enseignant_dashboard, name='enseignant_dashboard'),
    path('common-dashboard/', views.common_dashboard, name='common_dashboard'),
] 