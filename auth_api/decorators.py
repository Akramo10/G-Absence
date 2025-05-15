from functools import wraps
from django.http import JsonResponse

def role_required(roles):
    """
    Décorateur pour vérifier si l'utilisateur a le rôle requis.
    Utilise les informations d'utilisateur ajoutées par le middleware JWT.
    
    Args:
        roles: Une chaîne de caractères ou une liste de rôles autorisés.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Vérifier si les informations utilisateur sont présentes
            if not hasattr(request, 'user_info'):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Non authentifié'
                }, status=401)
            
            # Convertir roles en liste si c'est une chaîne
            allowed_roles = roles if isinstance(roles, list) else [roles]
            
            # Vérifier si l'utilisateur a le rôle requis
            user_role = request.user_info.get('type_utilisateur')
            if user_role not in allowed_roles:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Accès non autorisé'
                }, status=403)
            
            # Si tout est bon, exécuter la vue
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    
    return decorator 