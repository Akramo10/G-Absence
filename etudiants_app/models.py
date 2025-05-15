from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator

class Departement(models.Model):
    """
    Modèle représentant un département d'enseignement.
    """
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom du département")
    description = models.TextField(verbose_name="Description", blank=True)
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom

class Filiere(models.Model):
    """
    Modèle représentant une filière d'étude, rattachée à un département.
    """
    nom = models.CharField(max_length=100, verbose_name="Nom de la filière")
    description = models.TextField(verbose_name="Description", blank=True)
    annee_academique = models.CharField(
        max_length=9, 
        verbose_name="Année académique",
        help_text="Format: AAAA-AAAA (ex: 2023-2024)"
    )
    departement = models.ForeignKey(
        Departement, 
        on_delete=models.CASCADE, 
        related_name='filieres',
        verbose_name="Département"
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Filière"
        verbose_name_plural = "Filières"
        ordering = ['nom']
        # Garantir qu'une filière est unique par nom et département
        unique_together = [['nom', 'departement']]
    
    def __str__(self):
        return f"{self.nom} ({self.departement.nom})"

class Etudiant(models.Model):
    """
    Modèle représentant un étudiant inscrit dans une filière.
    """
    # Validator pour le format du code apogée
    code_apogee_validator = RegexValidator(
        regex=r'^\d{8}$',
        message="Le code apogée doit contenir exactement 8 chiffres"
    )
    
    # Validator pour le format du téléphone
    telephone_validator = RegexValidator(
        regex=r'^\+?\d{10,15}$',
        message="Le numéro de téléphone doit être au format valide: +XXXXXXXXXXXX ou XXXXXXXXXX"
    )
    
    code_apogee = models.CharField(
        max_length=8, 
        unique=True, 
        validators=[code_apogee_validator],
        verbose_name="Code Apogée"
    )
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    email = models.EmailField(unique=True, verbose_name="Email")
    telephone = models.CharField(
        max_length=15, 
        validators=[telephone_validator],
        verbose_name="Téléphone",
        blank=True
    )
    annee = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Année d'étude",
        help_text="De 1 à 5"
    )
    filiere = models.ForeignKey(
        Filiere, 
        on_delete=models.CASCADE, 
        related_name='etudiants',
        verbose_name="Filière"
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Étudiant"
        verbose_name_plural = "Étudiants"
        ordering = ['nom', 'prenom']
    
    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.code_apogee})"
