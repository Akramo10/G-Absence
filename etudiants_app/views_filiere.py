import psycopg2
import psycopg2.extras
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from auth_api.decorators import role_required
from .views import get_db_connection

# ======== API FILIÈRES ========

@api_view(['GET', 'POST'])
@role_required('admin')
def filieres_list(request):
    """
    Liste toutes les filières ou crée une nouvelle filière.
    """
    if request.method == 'GET':
        # Récupérer toutes les filières avec le nom du département
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("""
            SELECT f.id, f.nom, f.description, f.annee_academique, 
                   f.departement_id, d.nom as departement_nom,
                   f.date_creation, f.date_modification
            FROM etudiants_app_filiere f
            JOIN etudiants_app_departement d ON f.departement_id = d.id
            ORDER BY f.nom
        """)
        
        filieres = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Formater les résultats
        result = []
        for f in filieres:
            result.append({
                'id': f['id'],
                'nom': f['nom'],
                'description': f['description'],
                'annee_academique': f['annee_academique'],
                'departement': {
                    'id': f['departement_id'],
                    'nom': f['departement_nom']
                },
                'date_creation': f['date_creation'].isoformat() if f['date_creation'] else None,
                'date_modification': f['date_modification'].isoformat() if f['date_modification'] else None
            })
        
        return Response(result)
    
    elif request.method == 'POST':
        # Créer une nouvelle filière
        data = request.data
        nom = data.get('nom')
        description = data.get('description', '')
        annee_academique = data.get('annee_academique')
        departement_id = data.get('departement')
        
        # Validation des données
        if not all([nom, annee_academique, departement_id]):
            return Response(
                {'error': 'Nom, année académique et département sont requis.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Vérifier si le département existe
            cursor.execute("SELECT id FROM etudiants_app_departement WHERE id = %s", (departement_id,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return Response({'error': 'Département non trouvé.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Vérifier si la filière existe déjà pour ce département
            cursor.execute("""
                SELECT id FROM etudiants_app_filiere 
                WHERE nom = %s AND departement_id = %s
            """, (nom, departement_id))
            
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return Response(
                    {'error': 'Une filière avec ce nom existe déjà dans ce département.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Insérer la nouvelle filière
            cursor.execute("""
                INSERT INTO etudiants_app_filiere 
                (nom, description, annee_academique, departement_id, date_creation, date_modification)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
                RETURNING id, date_creation, date_modification
            """, (nom, description, annee_academique, departement_id))
            
            result = cursor.fetchone()
            conn.commit()
            
            # Récupérer le nom du département
            cursor.execute("SELECT nom FROM etudiants_app_departement WHERE id = %s", (departement_id,))
            departement_nom = cursor.fetchone()[0]
            
            response_data = {
                'id': result[0],
                'nom': nom,
                'description': description,
                'annee_academique': annee_academique,
                'departement': {
                    'id': departement_id,
                    'nom': departement_nom
                },
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
def filiere_detail(request, pk):
    """
    Opérations sur une filière spécifique (récupérer, mettre à jour, supprimer).
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Vérifier si la filière existe
        cursor.execute("""
            SELECT f.id, f.nom, f.description, f.annee_academique, 
                   f.departement_id, d.nom as departement_nom,
                   f.date_creation, f.date_modification
            FROM etudiants_app_filiere f
            JOIN etudiants_app_departement d ON f.departement_id = d.id
            WHERE f.id = %s
        """, (pk,))
        
        filiere = cursor.fetchone()
        
        if not filiere:
            cursor.close()
            conn.close()
            return Response({'error': 'Filière non trouvée.'}, status=status.HTTP_404_NOT_FOUND)
        
        if request.method == 'GET':
            # Formater le résultat
            result = {
                'id': filiere['id'],
                'nom': filiere['nom'],
                'description': filiere['description'],
                'annee_academique': filiere['annee_academique'],
                'departement': {
                    'id': filiere['departement_id'],
                    'nom': filiere['departement_nom']
                },
                'date_creation': filiere['date_creation'].isoformat() if filiere['date_creation'] else None,
                'date_modification': filiere['date_modification'].isoformat() if filiere['date_modification'] else None
            }
            
            # Récupérer le nombre d'étudiants dans cette filière
            cursor.execute("SELECT COUNT(*) FROM etudiants_app_etudiant WHERE filiere_id = %s", (pk,))
            count = cursor.fetchone()[0]
            result['nombre_etudiants'] = count
            
            # Récupérer les étudiants associés (version courte)
            cursor.execute("""
                SELECT id, code_apogee, nom, prenom
                FROM etudiants_app_etudiant
                WHERE filiere_id = %s
                ORDER BY nom, prenom
                LIMIT 10
            """, (pk,))
            
            etudiants = cursor.fetchall()
            result['etudiants'] = [{
                'id': e['id'],
                'code_apogee': e['code_apogee'],
                'nom': e['nom'],
                'prenom': e['prenom']
            } for e in etudiants]
            
            cursor.close()
            conn.close()
            return Response(result)
        
        elif request.method == 'PUT':
            data = request.data
            nom = data.get('nom', filiere['nom'])
            description = data.get('description', filiere['description'])
            annee_academique = data.get('annee_academique', filiere['annee_academique'])
            departement_id = data.get('departement', filiere['departement_id'])
            
            # Vérifier si le département existe
            cursor.execute("SELECT id FROM etudiants_app_departement WHERE id = %s", (departement_id,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return Response({'error': 'Département non trouvé.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Vérifier si le nom existe déjà pour une autre filière dans le même département
            cursor.execute("""
                SELECT id FROM etudiants_app_filiere 
                WHERE nom = %s AND departement_id = %s AND id != %s
            """, (nom, departement_id, pk))
            
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return Response(
                    {'error': 'Une filière avec ce nom existe déjà dans ce département.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mettre à jour la filière
            cursor.execute("""
                UPDATE etudiants_app_filiere 
                SET nom = %s, description = %s, annee_academique = %s, 
                    departement_id = %s, date_modification = NOW()
                WHERE id = %s
                RETURNING date_modification
            """, (nom, description, annee_academique, departement_id, pk))
            
            date_modification = cursor.fetchone()[0]
            conn.commit()
            
            # Récupérer le nom du département
            cursor.execute("SELECT nom FROM etudiants_app_departement WHERE id = %s", (departement_id,))
            departement_nom = cursor.fetchone()[0]
            
            result = {
                'id': pk,
                'nom': nom,
                'description': description,
                'annee_academique': annee_academique,
                'departement': {
                    'id': departement_id,
                    'nom': departement_nom
                },
                'date_creation': filiere['date_creation'].isoformat() if filiere['date_creation'] else None,
                'date_modification': date_modification.isoformat()
            }
            
            cursor.close()
            conn.close()
            return Response(result)
        
        elif request.method == 'DELETE':
            # Vérifier s'il y a des étudiants associés
            cursor.execute("SELECT COUNT(*) FROM etudiants_app_etudiant WHERE filiere_id = %s", (pk,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                cursor.close()
                conn.close()
                return Response(
                    {'error': f'Impossible de supprimer cette filière car elle contient {count} étudiant(s).'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Supprimer la filière
            cursor.execute("DELETE FROM etudiants_app_filiere WHERE id = %s", (pk,))
            conn.commit()
            
            cursor.close()
            conn.close()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
    except psycopg2.Error as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 