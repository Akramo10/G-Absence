from rest_framework import serializers
from .models import Departement, Filiere, Etudiant

class DepartementSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Departement.
    """
    class Meta:
        model = Departement
        fields = '__all__'
        read_only_fields = ['date_creation', 'date_modification']

class FiliereListSerializer(serializers.ModelSerializer):
    """
    Serializer pour lister les filières avec des informations basiques.
    """
    departement_nom = serializers.ReadOnlyField(source='departement.nom')
    
    class Meta:
        model = Filiere
        fields = ['id', 'nom', 'annee_academique', 'departement_nom']

class FiliereDetailSerializer(serializers.ModelSerializer):
    """
    Serializer détaillé pour les filières avec toutes les informations.
    """
    departement_nom = serializers.ReadOnlyField(source='departement.nom')
    nombre_etudiants = serializers.SerializerMethodField()
    
    class Meta:
        model = Filiere
        fields = ['id', 'nom', 'description', 'annee_academique', 'departement', 
                 'departement_nom', 'nombre_etudiants', 'date_creation', 'date_modification']
        read_only_fields = ['date_creation', 'date_modification']
    
    def get_nombre_etudiants(self, obj):
        """Calcule le nombre d'étudiants dans cette filière."""
        return obj.etudiants.count()
    
    def validate_annee_academique(self, value):
        """
        Vérifier que l'année académique est au format correct (AAAA-AAAA)
        """
        import re
        if not re.match(r'^\d{4}-\d{4}$', value):
            raise serializers.ValidationError(
                "Le format doit être AAAA-AAAA (ex: 2023-2024)"
            )
        
        annee_debut, annee_fin = map(int, value.split('-'))
        if annee_fin != annee_debut + 1:
            raise serializers.ValidationError(
                "L'année de fin doit être l'année de début + 1"
            )
        
        return value

class EtudiantListSerializer(serializers.ModelSerializer):
    """
    Serializer pour lister les étudiants avec des informations basiques.
    """
    filiere_nom = serializers.ReadOnlyField(source='filiere.nom')
    
    class Meta:
        model = Etudiant
        fields = ['id', 'code_apogee', 'nom', 'prenom', 'email', 'annee', 'filiere_nom']

class EtudiantDetailSerializer(serializers.ModelSerializer):
    """
    Serializer détaillé pour les étudiants avec toutes les informations.
    """
    filiere_nom = serializers.ReadOnlyField(source='filiere.nom')
    departement_nom = serializers.ReadOnlyField(source='filiere.departement.nom')
    
    class Meta:
        model = Etudiant
        fields = ['id', 'code_apogee', 'nom', 'prenom', 'email', 'telephone', 'annee',
                 'filiere', 'filiere_nom', 'departement_nom', 'date_creation', 'date_modification']
        read_only_fields = ['date_creation', 'date_modification']
    
    def validate_email(self, value):
        """
        Vérifier que l'email est unique (insensible à la casse)
        """
        from django.db.models import Q
        
        # Obtenir l'instance à mettre à jour (si c'est une mise à jour)
        instance = getattr(self, 'instance', None)
        
        # Vérifier si l'email existe déjà (en ignorant l'instance actuelle)
        queryset = Etudiant.objects.filter(email__iexact=value)
        if instance:
            queryset = queryset.exclude(pk=instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        
        return value
    
    def validate_code_apogee(self, value):
        """
        Validation supplémentaire du code apogée pour assurer qu'il est unique
        """
        # Les validateurs de modèle s'appliquent déjà, mais on peut ajouter d'autres vérifications
        return value 