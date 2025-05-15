from django.urls import path
from . import views
from . import views_filiere
from . import views_etudiant

app_name = 'etudiants_app'

urlpatterns = [
    # Départements
    path('departements/', views.departements_list, name='departements-list'),
    path('departements/<int:pk>/', views.departement_detail, name='departement-detail'),
    
    # Filières
    path('filieres/', views_filiere.filieres_list, name='filieres-list'),
    path('filieres/<int:pk>/', views_filiere.filiere_detail, name='filiere-detail'),
    
    # Étudiants
    path('etudiants/', views_etudiant.etudiants_list, name='etudiants-list'),
    path('etudiants/<int:pk>/', views_etudiant.etudiant_detail, name='etudiant-detail'),
] 