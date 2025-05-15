from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Permission personnalisée pour n'autoriser que les utilisateurs avec le rôle 'admin'.
    """
    
    def has_permission(self, request, view):
        """
        Vérifie si l'utilisateur courant possède le rôle 'admin'.
        """
        # Vérifier si l'attribut user_info (ajouté par le middleware JWTAuthMiddleware) existe
        if hasattr(request, 'user_info'):
            # Vérifier le type_utilisateur (admin ou enseignant)
            return request.user_info.get('type_utilisateur') == 'admin'
        
        # Par défaut, refuser l'accès si l'attribut user_info n'existe pas
        return False 