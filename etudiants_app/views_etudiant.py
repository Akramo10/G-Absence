import psycopg2
import psycopg2.extras
import re
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from auth_api.decorators import role_required
from .views import get_db_connection

# ======== API ÉTUDIANTS ========

@api_view(['GET', 'POST'])
@role_required('admin')
def etudiants_list(request):
    """
    Liste tous les étudiants ou crée un nouvel étudiant.
    """
    if request.method == 'GET':
        # Récupérer tous les étudiants avec les informations de filière et département
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        cursor.execute("""
            SELECT e.id, e.code_apogee, e.nom, e.prenom, e.email, e.telephone, e.annee,
                   e.filiere_id, f.nom as filiere_nom, d.nom as departement_nom,
                   e.date_creation, e.date_modification
            FROM etudiants_app_etudiant e
            JOIN etudiants_app_filiere f ON e.filiere_id = f.id
            JOIN etudiants_app_departement d ON f.departement_id = d.id
            ORDER BY e.nom, e.prenom
        """)
        
        etudiants = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Formater les résultats
        result = []
        for e in etudiants:
            result.append({
                'id': e['id'],
                'code_apogee': e['code_apogee'],
                'nom': e['nom'],
                'prenom': e['prenom'],
                'email': e['email'],
                'telephone': e['telephone'],
                'annee': e['annee'],
                'filiere': {
                    'id': e['filiere_id'],
                    'nom': e['filiere_nom']
                },
                'departement_nom': e['departement_nom'],
                'date_creation': e['date_creation'].isoformat() if e['date_creation'] else None,
                'date_modification': e['date_modification'].isoformat() if e['date_modification'] else None
            })
        
        return Response(result)
    
    elif request.method == 'POST':
        # Créer un nouvel étudiant
        data = request.data
        
        # Extraire les données
        code_apogee = data.get('code_apogee')
        nom = data.get('nom')
        prenom = data.get('prenom')
        email = data.get('email')
        telephone = data.get('telephone', '')
        annee = data.get('annee')
        filiere_id = data.get('filiere')
        
        # Validation des données
        if not all([code_apogee, nom, prenom, email, annee, filiere_id]):
            return Response({
                'error': 'Code apogée, nom, prénom, email, année et filière sont requis.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Valider le format du code apogée (8 chiffres)
        if not re.match(r'^\d{8}$', code_apogee):
            return Response({
                'error': 'Le code apogée doit contenir exactement 8 chiffres.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Valider le format de l'email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return Response({
                'error': 'Format d\'email invalide.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Valider l'année d'étude (1 à 5)
        try:
            annee_int = int(annee)
            if annee_int < 1 or annee_int > 5:
                return Response({
                    'error': 'L\'année d\'étude doit être entre 1 et 5.'
                }, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({
                'error': 'L\'année d\'étude doit être un nombre entier.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Valider le format du téléphone si fourni
        if telephone and not re.match(r'^\+?\d{10,15}$', telephone):
            return Response({
                'error': 'Format de téléphone invalide.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Vérifier si le code apogée existe déjà
            cursor.execute("SELECT id FROM etudiants_app_etudiant WHERE code_apogee = %s", (code_apogee,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return Response({
                    'error': 'Un étudiant avec ce code apogée existe déjà.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Vérifier si l'email existe déjà
            cursor.execute("SELECT id FROM etudiants_app_etudiant WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return Response({
                    'error': 'Un étudiant avec cet email existe déjà.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Vérifier si la filière existe
            cursor.execute("SELECT id FROM etudiants_app_filiere WHERE id = %s", (filiere_id,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return Response({
                    'error': 'Filière non trouvée.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Insérer le nouvel étudiant
            cursor.execute("""
                INSERT INTO etudiants_app_etudiant 
                (code_apogee, nom, prenom, email, telephone, annee, filiere_id, date_creation, date_modification)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING id, date_creation, date_modification
            """, (code_apogee, nom, prenom, email, telephone, annee_int, filiere_id))
            
            result = cursor.fetchone()
            conn.commit()
            
            # Récupérer les informations de la filière
            cursor.execute("""
                SELECT f.nom as filiere_nom, d.nom as departement_nom
                FROM etudiants_app_filiere f
                JOIN etudiants_app_departement d ON f.departement_id = d.id
                WHERE f.id = %s
            """, (filiere_id,))
            
            filiere_info = cursor.fetchone()
            
            response_data = {
                'id': result[0],
                'code_apogee': code_apogee,
                'nom': nom,
                'prenom': prenom,
                'email': email,
                'telephone': telephone,
                'annee': annee_int,
                'filiere': {
                    'id': filiere_id,
                    'nom': filiere_info[0]
                },
                'departement_nom': filiere_info[1],
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
def etudiant_detail(request, pk):
    """
    Opérations sur un étudiant spécifique (récupérer, mettre à jour, supprimer).
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Vérifier si l'étudiant existe
        cursor.execute("""
            SELECT e.id, e.code_apogee, e.nom, e.prenom, e.email, e.telephone, e.annee,
                   e.filiere_id, f.nom as filiere_nom, d.id as departement_id, d.nom as departement_nom,
                   e.date_creation, e.date_modification
            FROM etudiants_app_etudiant e
            JOIN etudiants_app_filiere f ON e.filiere_id = f.id
            JOIN etudiants_app_departement d ON f.departement_id = d.id
            WHERE e.id = %s
        """, (pk,))
        
        etudiant = cursor.fetchone()
        
        if not etudiant:
            cursor.close()
            conn.close()
            return Response({'error': 'Étudiant non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
        
        if request.method == 'GET':
            # Formater le résultat
            result = {
                'id': etudiant['id'],
                'code_apogee': etudiant['code_apogee'],
                'nom': etudiant['nom'],
                'prenom': etudiant['prenom'],
                'email': etudiant['email'],
                'telephone': etudiant['telephone'],
                'annee': etudiant['annee'],
                'filiere': {
                    'id': etudiant['filiere_id'],
                    'nom': etudiant['filiere_nom']
                },
                'departement': {
                    'id': etudiant['departement_id'],
                    'nom': etudiant['departement_nom']
                },
                'date_creation': etudiant['date_creation'].isoformat() if etudiant['date_creation'] else None,
                'date_modification': etudiant['date_modification'].isoformat() if etudiant['date_modification'] else None
            }
            
            cursor.close()
            conn.close()
            return Response(result)
        
        elif request.method == 'PUT':
            data = request.data
            
            # Extraire les données
            code_apogee = data.get('code_apogee', etudiant['code_apogee'])
            nom = data.get('nom', etudiant['nom'])
            prenom = data.get('prenom', etudiant['prenom'])
            email = data.get('email', etudiant['email'])
            telephone = data.get('telephone', etudiant['telephone'] or '')
            annee = data.get('annee', etudiant['annee'])
            filiere_id = data.get('filiere', etudiant['filiere_id'])
            
            # Validations similaires à POST
            if not re.match(r'^\d{8}$', code_apogee):
                return Response({
                    'error': 'Le code apogée doit contenir exactement 8 chiffres.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                return Response({
                    'error': 'Format d\'email invalide.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                annee_int = int(annee)
                if annee_int < 1 or annee_int > 5:
                    return Response({
                        'error': 'L\'année d\'étude doit être entre 1 et 5.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({
                    'error': 'L\'année d\'étude doit être un nombre entier.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if telephone and not re.match(r'^\+?\d{10,15}$', telephone):
                return Response({
                    'error': 'Format de téléphone invalide.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Vérifier si le code apogée existe déjà pour un autre étudiant
            cursor.execute("""
                SELECT id FROM etudiants_app_etudiant 
                WHERE code_apogee = %s AND id != %s
            """, (code_apogee, pk))
            
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return Response({
                    'error': 'Un étudiant avec ce code apogée existe déjà.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Vérifier si l'email existe déjà pour un autre étudiant
            cursor.execute("""
                SELECT id FROM etudiants_app_etudiant 
                WHERE email = %s AND id != %s
            """, (email, pk))
            
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return Response({
                    'error': 'Un étudiant avec cet email existe déjà.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Vérifier si la filière existe
            cursor.execute("SELECT id FROM etudiants_app_filiere WHERE id = %s", (filiere_id,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return Response({
                    'error': 'Filière non trouvée.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mettre à jour l'étudiant
            cursor.execute("""
                UPDATE etudiants_app_etudiant 
                SET code_apogee = %s, nom = %s, prenom = %s, email = %s, 
                    telephone = %s, annee = %s, filiere_id = %s, date_modification = NOW()
                WHERE id = %s
                RETURNING date_modification
            """, (code_apogee, nom, prenom, email, telephone, annee_int, filiere_id, pk))
            
            date_modification = cursor.fetchone()[0]
            conn.commit()
            
            # Récupérer les informations de la filière
            cursor.execute("""
                SELECT f.nom as filiere_nom, d.id as departement_id, d.nom as departement_nom
                FROM etudiants_app_filiere f
                JOIN etudiants_app_departement d ON f.departement_id = d.id
                WHERE f.id = %s
            """, (filiere_id,))
            
            filiere_info = cursor.fetchone()
            
            result = {
                'id': pk,
                'code_apogee': code_apogee,
                'nom': nom,
                'prenom': prenom,
                'email': email,
                'telephone': telephone,
                'annee': annee_int,
                'filiere': {
                    'id': filiere_id,
                    'nom': filiere_info[0]
                },
                'departement': {
                    'id': filiere_info[1],
                    'nom': filiere_info[2]
                },
                'date_creation': etudiant['date_creation'].isoformat() if etudiant['date_creation'] else None,
                'date_modification': date_modification.isoformat()
            }
            
            cursor.close()
            conn.close()
            return Response(result)
        
        elif request.method == 'DELETE':
            # Supprimer l'étudiant
            cursor.execute("DELETE FROM etudiants_app_etudiant WHERE id = %s", (pk,))
            conn.commit()
            
            cursor.close()
            conn.close()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
    except psycopg2.Error as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 