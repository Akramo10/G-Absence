import json
import hashlib
import psycopg2
import jwt
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .decorators import role_required
import logging

# Configurer le logger
logger = logging.getLogger(__name__)

@csrf_exempt
def login(request):
    """
    Vue pour authentifier un utilisateur et générer un token JWT.
    Accepte uniquement les requêtes POST.
    """
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Seules les requêtes POST sont acceptées'
        }, status=405)
    
    try:
        # Récupérer les données de la requête
        data = json.loads(request.body)
        nom_utilisateur = data.get('nom_utilisateur')
        mot_de_passe = data.get('mot_de_passe')
        
        # Debug - Log des informations de connexion
        logger.error(f"Tentative de connexion pour l'utilisateur: {nom_utilisateur}")
        
        # Vérifier que les champs requis sont présents
        if not nom_utilisateur or not mot_de_passe:
            return JsonResponse({
                'status': 'error',
                'message': 'Nom d\'utilisateur et mot de passe requis'
            }, status=400)
        
        # Hasher le mot de passe avec SHA256
        mot_de_passe_hash = hashlib.sha256(mot_de_passe.encode()).hexdigest()
        
        # Debug - Log du hash généré
        logger.error(f"Hash généré: {mot_de_passe_hash}")
        
        # Établir une connexion à la base de données
        conn = psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )
        
        # Créer un curseur
        cursor = conn.cursor()
        
        # Debug - Requête de vérification du hash en base
        debug_query = """
            SELECT nom_utilisateur, mot_de_passe_hash, type_utilisateur 
            FROM utilisateur 
            WHERE nom_utilisateur = %s
        """
        cursor.execute(debug_query, (nom_utilisateur,))
        debug_user = cursor.fetchone()
        
        if debug_user:
            logger.error(f"Utilisateur trouvé: {debug_user[0]}")
            logger.error(f"Hash en base: {debug_user[1]}")
            logger.error(f"Type utilisateur: {debug_user[2]}")
        else:
            logger.error(f"Aucun utilisateur trouvé avec le nom: {nom_utilisateur}")
        
        # Exécuter la requête SQL pour vérifier l'utilisateur
        query = """
            SELECT id_utilisateur, nom_utilisateur, type_utilisateur 
            FROM utilisateur 
            WHERE nom_utilisateur = %s AND mot_de_passe_hash = %s
        """
        cursor.execute(query, (nom_utilisateur, mot_de_passe_hash))
        
        # Récupérer le résultat
        user = cursor.fetchone()
        
        # Fermer le curseur et la connexion
        cursor.close()
        conn.close()
        
        # Vérifier si l'utilisateur existe
        if not user:
            logger.error(f"Échec d'authentification pour: {nom_utilisateur}")
            return JsonResponse({
                'status': 'error',
                'message': 'Identifiants invalides'
            }, status=401)
        
        # Extraire les informations de l'utilisateur
        id_utilisateur, nom_utilisateur, type_utilisateur = user
        
        # Debug - Log de l'utilisateur authentifié
        logger.error(f"Authentification réussie - ID: {id_utilisateur}, Nom: {nom_utilisateur}, Type: {type_utilisateur}")
        
        # Générer le token JWT
        payload = {
            'id_utilisateur': id_utilisateur,
            'nom_utilisateur': nom_utilisateur,
            'type_utilisateur': type_utilisateur,
            'exp': datetime.utcnow() + timedelta(hours=24)  # Expiration après 24h
        }
        
        # Utiliser la clé secrète de Django pour signer le token
        token = jwt.encode(
            payload, 
            settings.SECRET_KEY, 
            algorithm='HS256'
        )
        
        # Renvoyer le token JWT
        return JsonResponse({
            'status': 'success',
            'token': token,
            'type_utilisateur': type_utilisateur
        })
        
    except json.JSONDecodeError:
        logger.error("Erreur de décodage JSON")
        return JsonResponse({
            'status': 'error',
            'message': 'Format JSON invalide'
        }, status=400)
    
    except psycopg2.Error as e:
        logger.error(f"Erreur de base de données: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Erreur de base de données: {str(e)}'
        }, status=500)
    
    except Exception as e:
        logger.error(f"Erreur serveur: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Erreur serveur: {str(e)}'
        }, status=500)

@csrf_exempt
def create_test_user(request):
    """
    Vue pour créer un utilisateur de test directement depuis l'API.
    Cette vue est uniquement à des fins de débogage.
    """
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Seules les requêtes POST sont acceptées'
        }, status=405)
    
    try:
        # Récupérer les données de la requête
        data = json.loads(request.body)
        nom_utilisateur = data.get('nom_utilisateur', 'prof_test')
        mot_de_passe = data.get('mot_de_passe', 'prof123')
        email = data.get('email', 'prof_test@example.com')
        type_utilisateur = data.get('type_utilisateur', 'enseignant')
        
        # Hasher le mot de passe avec SHA256
        mot_de_passe_hash = hashlib.sha256(mot_de_passe.encode()).hexdigest()
        
        # Log des informations
        logger.error(f"Création d'utilisateur - Nom: {nom_utilisateur}, Hash: {mot_de_passe_hash}, Type: {type_utilisateur}")
        
        # Établir une connexion à la base de données
        conn = psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )
        
        # Créer un curseur
        cursor = conn.cursor()
        
        # Vérifier si l'utilisateur existe déjà
        cursor.execute("SELECT nom_utilisateur FROM utilisateur WHERE nom_utilisateur = %s", (nom_utilisateur,))
        if cursor.fetchone():
            # L'utilisateur existe, on le met à jour
            query = """
                UPDATE utilisateur 
                SET mot_de_passe_hash = %s, email = %s, type_utilisateur = %s
                WHERE nom_utilisateur = %s
                RETURNING id_utilisateur
            """
            cursor.execute(query, (mot_de_passe_hash, email, type_utilisateur, nom_utilisateur))
            id_utilisateur = cursor.fetchone()[0]
            message = f"Utilisateur {nom_utilisateur} mis à jour"
        else:
            # L'utilisateur n'existe pas, on le crée
            query = """
                INSERT INTO utilisateur (nom_utilisateur, mot_de_passe_hash, email, type_utilisateur)
                VALUES (%s, %s, %s, %s)
                RETURNING id_utilisateur
            """
            cursor.execute(query, (nom_utilisateur, mot_de_passe_hash, email, type_utilisateur))
            id_utilisateur = cursor.fetchone()[0]
            message = f"Nouvel utilisateur {nom_utilisateur} créé"
        
        # Valider la transaction
        conn.commit()
        
        # Fermer le curseur et la connexion
        cursor.close()
        conn.close()
        
        return JsonResponse({
            'status': 'success',
            'message': message,
            'user': {
                'id_utilisateur': id_utilisateur,
                'nom_utilisateur': nom_utilisateur,
                'type_utilisateur': type_utilisateur,
                'mot_de_passe': mot_de_passe,
                'mot_de_passe_hash': mot_de_passe_hash
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'utilisateur: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Erreur: {str(e)}'
        }, status=500)

@role_required('admin')
def admin_dashboard(request):
    """
    Vue accessible uniquement aux administrateurs.
    """
    return JsonResponse({
        'status': 'success',
        'message': 'Bienvenue sur le tableau de bord administrateur',
        'user': request.user_info
    })

@role_required('enseignant')
def enseignant_dashboard(request):
    """
    Vue accessible uniquement aux enseignants.
    """
    return JsonResponse({
        'status': 'success',
        'message': 'Bienvenue sur le tableau de bord enseignant',
        'user': request.user_info
    })

@role_required(['admin', 'enseignant'])
def common_dashboard(request):
    """
    Vue accessible aux deux types d'utilisateurs.
    """
    return JsonResponse({
        'status': 'success',
        'message': 'Bienvenue sur le tableau de bord commun',
        'user': request.user_info
    }) 