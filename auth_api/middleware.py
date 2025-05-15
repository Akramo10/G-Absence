import jwt
import json
import logging
from django.http import JsonResponse
from django.conf import settings

# Configurer le logger
logger = logging.getLogger(__name__)

class JWTAuthMiddleware:
    """
    Middleware pour vérifier la validité des tokens JWT.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log du chemin pour debug
        logger.error(f"JWT Middleware - Path: {request.path}")
        
        # Liste des chemins qui ne nécessitent pas d'authentification
        exempt_paths = [
            # Routes d'authentification
            '/api/auth/login/',
            '/api/auth-sql/login/',
            '/api/auth-sql/create-test-user/',
            # UI Django admin
            '/admin/',
            '/admin/login/',
            # Documentation API Swagger
            '/swagger/',
            '/redoc/',
        ]
        
        # Vérifier si le chemin est exempté
        if any(request.path.startswith(path) for path in exempt_paths):
            logger.error(f"Chemin exempté: {request.path}")
            return self.get_response(request)
        
        # Récupérer le token d'autorisation
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        logger.error(f"Auth Header: {auth_header}")
        
        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'status': 'error', 
                'message': 'Token d\'authentification manquant ou invalide'
            }, status=401)
        
        # Extraire le token JWT
        token = auth_header.split(' ')[1]
        logger.error(f"Token extrait: {token[:10]}...")
        
        try:
            # Vérifier et décoder le token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            logger.error(f"Token décodé avec succès: {payload.get('nom_utilisateur')}")
            
            # Ajouter les informations de l'utilisateur à la requête
            request.user_info = {
                'id_utilisateur': payload.get('id_utilisateur'),
                'nom_utilisateur': payload.get('nom_utilisateur'),
                'type_utilisateur': payload.get('type_utilisateur')
            }
            
            return self.get_response(request)
            
        except jwt.ExpiredSignatureError:
            logger.error("Token expiré")
            return JsonResponse({
                'status': 'error', 
                'message': 'Token expiré'
            }, status=401)
            
        except jwt.InvalidTokenError as e:
            logger.error(f"Token invalide: {str(e)}")
            return JsonResponse({
                'status': 'error', 
                'message': 'Token invalide'
            }, status=401)
            
        except Exception as e:
            logger.error(f"Erreur d'authentification: {str(e)}")
            return JsonResponse({
                'status': 'error', 
                'message': f'Erreur d\'authentification: {str(e)}'
            }, status=500) 