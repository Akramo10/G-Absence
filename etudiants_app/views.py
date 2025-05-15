import json
import psycopg2
import psycopg2.extras
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from auth_api.decorators import role_required

# Fonction utilitaire pour établir la connexion à la base de données
def get_db_connection():
    """
    Établit et retourne une connexion à la base de données PostgreSQL.
    """
    return psycopg2.connect(
        dbname=settings.DATABASES['default']['NAME'],
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        host=settings.DATABASES['default']['HOST'],
        port=settings.DATABASES['default']['PORT']
    )

# ======== API DÉPARTEMENTS ========

@api_view(['GET', 'POST'])
@role_required('admin')
def departements_list(request):
    """
    Liste tous les départements ou crée un nouveau département.
    """
    if request.method == 'GET':
        # Récupérer tous les départements
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("""
            SELECT id, nom, description, date_creation, date_modification 
            FROM etudiants_app_departement
            ORDER BY nom
        """)
        
        departements = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Formater les résultats
        result = []
        for dept in departements:
            result.append({
                'id': dept['id'],
                'nom': dept['nom'],
                'description': dept['description'],
                'date_creation': dept['date_creation'].isoformat() if dept['date_creation'] else None,
                'date_modification': dept['date_modification'].isoformat() if dept['date_modification'] else None
            })
        
        return Response(result)
    
    elif request.method == 'POST':
        # Créer un nouveau département
        data = request.data
        nom = data.get('nom')
        description = data.get('description', '')
        
        if not nom:
            return Response({'error': 'Le nom du département est requis.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Vérifier si le département existe déjà
            cursor.execute("SELECT id FROM etudiants_app_departement WHERE nom = %s", (nom,))
            if cursor.fetchone():
                return Response({'error': 'Un département avec ce nom existe déjà.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Insérer le nouveau département
            cursor.execute("""
                INSERT INTO etudiants_app_departement (nom, description, date_creation, date_modification)
                VALUES (%s, %s, NOW(), NOW())
                RETURNING id, date_creation, date_modification
            """, (nom, description))
            
            result = cursor.fetchone()
            conn.commit()
            
            response_data = {
                'id': result[0],
                'nom': nom,
                'description': description,
                'date_creation': result[1].isoformat(),
                'date_modification': result[2].isoformat()
            }
            
            cursor.close()
            conn.close()
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except psycopg2.Error as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'PUT', 'DELETE'])
@role_required('admin')
def departement_detail(request, pk):
    """
    Opérations sur un département spécifique (récupérer, mettre à jour, supprimer).
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Vérifier si le département existe
        cursor.execute("""
            SELECT id, nom, description, date_creation, date_modification 
            FROM etudiants_app_departement
            WHERE id = %s
        """, (pk,))
        
        departement = cursor.fetchone()
        
        if not departement:
            cursor.close()
            conn.close()
            return Response({'error': 'Département non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
        
        if request.method == 'GET':
            # Formater le résultat
            result = {
                'id': departement['id'],
                'nom': departement['nom'],
                'description': departement['description'],
                'date_creation': departement['date_creation'].isoformat() if departement['date_creation'] else None,
                'date_modification': departement['date_modification'].isoformat() if departement['date_modification'] else None
            }
            
            # Récupérer les filières associées
            cursor.execute("""
                SELECT id, nom, annee_academique
                FROM etudiants_app_filiere
                WHERE departement_id = %s
                ORDER BY nom
            """, (pk,))
            
            filieres = cursor.fetchall()
            result['filieres'] = [{
                'id': f['id'],
                'nom': f['nom'],
                'annee_academique': f['annee_academique']
            } for f in filieres]
            
            cursor.close()
            conn.close()
            return Response(result)
        
        elif request.method == 'PUT':
            data = request.data
            nom = data.get('nom')
            description = data.get('description', departement['description'])
            
            if not nom:
                return Response({'error': 'Le nom du département est requis.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Vérifier si le nom existe déjà pour un autre département
            cursor.execute("""
                SELECT id FROM etudiants_app_departement 
                WHERE nom = %s AND id != %s
            """, (nom, pk))
            
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return Response({'error': 'Un département avec ce nom existe déjà.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Mettre à jour le département
            cursor.execute("""
                UPDATE etudiants_app_departement 
                SET nom = %s, description = %s, date_modification = NOW()
                WHERE id = %s
                RETURNING date_modification
            """, (nom, description, pk))
            
            date_modification = cursor.fetchone()[0]
            conn.commit()
            
            result = {
                'id': pk,
                'nom': nom,
                'description': description,
                'date_creation': departement['date_creation'].isoformat() if departement['date_creation'] else None,
                'date_modification': date_modification.isoformat()
            }
            
            cursor.close()
            conn.close()
            return Response(result)
        
        elif request.method == 'DELETE':
            # Vérifier s'il y a des filières associées
            cursor.execute("SELECT COUNT(*) FROM etudiants_app_filiere WHERE departement_id = %s", (pk,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                cursor.close()
                conn.close()
                return Response(
                    {'error': f'Impossible de supprimer ce département car il contient {count} filière(s).'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Supprimer le département
            cursor.execute("DELETE FROM etudiants_app_departement WHERE id = %s", (pk,))
            conn.commit()
            
            cursor.close()
            conn.close()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
    except psycopg2.Error as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 