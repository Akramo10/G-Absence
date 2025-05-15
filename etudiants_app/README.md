# Documentation de l'API de Gestion des Étudiants

Cette API permet la gestion complète des départements, filières et étudiants d'un établissement d'enseignement. Elle est sécurisée par authentification JWT et réservée aux administrateurs.

## Authentification

Toutes les routes de cette API nécessitent une authentification JWT.

1. **Obtenir un token JWT**:
   ```
   POST /api/auth-sql/login/
   ```
   Corps de la requête:
   ```json
   {
     "nom_utilisateur": "admin",
     "mot_de_passe": "admin"
   }
   ```
   Réponse:
   ```json
   {
     "status": "success",
     "token": "eyJhbGciOiJIUzI1...",
     "type_utilisateur": "admin"
   }
   ```

2. **Utilisation du token**:
   Pour toutes les requêtes API, ajoutez l'en-tête:
   ```
   Authorization: Bearer <token>
   ```

## Gestion des Départements

### Liste des départements

**Endpoint**: `GET /api/admin/departements/`

**Description**: Récupère tous les départements.

**Exemple de réponse**:
```json
[
  {
    "id": 1,
    "nom": "Informatique",
    "description": "Département d'informatique et systèmes d'information",
    "date_creation": "2023-05-15T10:30:00",
    "date_modification": "2023-05-15T10:30:00"
  }
]
```

### Création d'un département

**Endpoint**: `POST /api/admin/departements/`

**Description**: Crée un nouveau département.

**Corps de la requête**:
```json
{
  "nom": "Mathématiques",
  "description": "Département de mathématiques appliquées"
}
```

**Exemple de réponse**:
```json
{
  "id": 2,
  "nom": "Mathématiques",
  "description": "Département de mathématiques appliquées",
  "date_creation": "2023-05-15T11:00:00",
  "date_modification": "2023-05-15T11:00:00"
}
```

### Détails d'un département

**Endpoint**: `GET /api/admin/departements/<id>/`

**Description**: Récupère les détails d'un département spécifique, y compris ses filières.

**Exemple de réponse**:
```json
{
  "id": 1,
  "nom": "Informatique",
  "description": "Département d'informatique et systèmes d'information",
  "date_creation": "2023-05-15T10:30:00",
  "date_modification": "2023-05-15T10:30:00",
  "filieres": [
    {
      "id": 1,
      "nom": "Génie Logiciel",
      "annee_academique": "2023-2024"
    }
  ]
}
```

### Mise à jour d'un département

**Endpoint**: `PUT /api/admin/departements/<id>/`

**Description**: Met à jour un département existant.

**Corps de la requête**:
```json
{
  "nom": "Informatique et Réseaux",
  "description": "Département d'informatique, réseaux et systèmes d'information"
}
```

**Exemple de réponse**:
```json
{
  "id": 1,
  "nom": "Informatique et Réseaux",
  "description": "Département d'informatique, réseaux et systèmes d'information",
  "date_creation": "2023-05-15T10:30:00",
  "date_modification": "2023-05-15T12:15:00"
}
```

### Suppression d'un département

**Endpoint**: `DELETE /api/admin/departements/<id>/`

**Description**: Supprime un département. Un département ne peut être supprimé que s'il ne contient aucune filière.

**Codes de retour**:
- 204: Suppression réussie
- 400: Impossible de supprimer un département contenant des filières

## Gestion des Filières

### Liste des filières

**Endpoint**: `GET /api/admin/filieres/`

**Description**: Récupère toutes les filières avec leurs départements.

**Exemple de réponse**:
```json
[
  {
    "id": 1,
    "nom": "Génie Logiciel",
    "description": "Formation en ingénierie du logiciel",
    "annee_academique": "2023-2024",
    "departement": {
      "id": 1,
      "nom": "Informatique"
    },
    "date_creation": "2023-05-15T14:00:00",
    "date_modification": "2023-05-15T14:00:00"
  }
]
```

### Création d'une filière

**Endpoint**: `POST /api/admin/filieres/`

**Description**: Crée une nouvelle filière.

**Corps de la requête**:
```json
{
  "nom": "Intelligence Artificielle",
  "description": "Formation en IA et machine learning",
  "annee_academique": "2023-2024",
  "departement": 1
}
```

**Exemple de réponse**:
```json
{
  "id": 2,
  "nom": "Intelligence Artificielle",
  "description": "Formation en IA et machine learning",
  "annee_academique": "2023-2024",
  "departement": {
    "id": 1,
    "nom": "Informatique"
  },
  "date_creation": "2023-05-15T15:30:00",
  "date_modification": "2023-05-15T15:30:00"
}
```

### Détails d'une filière

**Endpoint**: `GET /api/admin/filieres/<id>/`

**Description**: Récupère les détails d'une filière spécifique, y compris ses étudiants.

**Exemple de réponse**:
```json
{
  "id": 1,
  "nom": "Génie Logiciel",
  "description": "Formation en ingénierie du logiciel",
  "annee_academique": "2023-2024",
  "departement": {
    "id": 1,
    "nom": "Informatique"
  },
  "date_creation": "2023-05-15T14:00:00",
  "date_modification": "2023-05-15T14:00:00",
  "nombre_etudiants": 2,
  "etudiants": [
    {
      "id": 1,
      "code_apogee": "12345678",
      "nom": "Dupont",
      "prenom": "Jean"
    },
    {
      "id": 2,
      "code_apogee": "87654321",
      "nom": "Martin",
      "prenom": "Sophie"
    }
  ]
}
```

### Mise à jour d'une filière

**Endpoint**: `PUT /api/admin/filieres/<id>/`

**Description**: Met à jour une filière existante.

**Corps de la requête**:
```json
{
  "nom": "Génie Logiciel Avancé",
  "description": "Formation en ingénierie du logiciel et méthodes agiles",
  "annee_academique": "2023-2024",
  "departement": 1
}
```

**Exemple de réponse**:
```json
{
  "id": 1,
  "nom": "Génie Logiciel Avancé",
  "description": "Formation en ingénierie du logiciel et méthodes agiles",
  "annee_academique": "2023-2024",
  "departement": {
    "id": 1,
    "nom": "Informatique"
  },
  "date_creation": "2023-05-15T14:00:00",
  "date_modification": "2023-05-15T16:45:00"
}
```

### Suppression d'une filière

**Endpoint**: `DELETE /api/admin/filieres/<id>/`

**Description**: Supprime une filière. Une filière ne peut être supprimée que si elle ne contient aucun étudiant.

**Codes de retour**:
- 204: Suppression réussie
- 400: Impossible de supprimer une filière contenant des étudiants

## Gestion des Étudiants

### Liste des étudiants

**Endpoint**: `GET /api/admin/etudiants/`

**Description**: Récupère tous les étudiants avec leurs filières et départements.

**Exemple de réponse**:
```json
[
  {
    "id": 1,
    "code_apogee": "12345678",
    "nom": "Dupont",
    "prenom": "Jean",
    "email": "jean.dupont@example.com",
    "telephone": "+33612345678",
    "annee": 3,
    "filiere": {
      "id": 1,
      "nom": "Génie Logiciel"
    },
    "departement_nom": "Informatique",
    "date_creation": "2023-05-16T09:00:00",
    "date_modification": "2023-05-16T09:00:00"
  }
]
```

### Création d'un étudiant

**Endpoint**: `POST /api/admin/etudiants/`

**Description**: Crée un nouvel étudiant.

**Validation**:
- Code apogée: 8 chiffres exactement
- Email: format valide
- Téléphone: format valide (+XXXXXXXXXXXX ou XXXXXXXXXX)
- Année: entre 1 et 5

**Corps de la requête**:
```json
{
  "code_apogee": "87654321",
  "nom": "Martin",
  "prenom": "Sophie",
  "email": "sophie.martin@example.com",
  "telephone": "+33687654321",
  "annee": 2,
  "filiere": 1
}
```

**Exemple de réponse**:
```json
{
  "id": 2,
  "code_apogee": "87654321",
  "nom": "Martin",
  "prenom": "Sophie",
  "email": "sophie.martin@example.com",
  "telephone": "+33687654321",
  "annee": 2,
  "filiere": {
    "id": 1,
    "nom": "Génie Logiciel"
  },
  "departement_nom": "Informatique",
  "date_creation": "2023-05-16T10:15:00",
  "date_modification": "2023-05-16T10:15:00"
}
```

### Détails d'un étudiant

**Endpoint**: `GET /api/admin/etudiants/<id>/`

**Description**: Récupère les détails d'un étudiant spécifique.

**Exemple de réponse**:
```json
{
  "id": 1,
  "code_apogee": "12345678",
  "nom": "Dupont",
  "prenom": "Jean",
  "email": "jean.dupont@example.com",
  "telephone": "+33612345678",
  "annee": 3,
  "filiere": {
    "id": 1,
    "nom": "Génie Logiciel"
  },
  "departement": {
    "id": 1,
    "nom": "Informatique"
  },
  "date_creation": "2023-05-16T09:00:00",
  "date_modification": "2023-05-16T09:00:00"
}
```

### Mise à jour d'un étudiant

**Endpoint**: `PUT /api/admin/etudiants/<id>/`

**Description**: Met à jour un étudiant existant.

**Corps de la requête**:
```json
{
  "code_apogee": "12345678",
  "nom": "Dupont",
  "prenom": "Jean-Michel",
  "email": "jean.dupont@example.com",
  "telephone": "+33612345678",
  "annee": 4,
  "filiere": 1
}
```

**Exemple de réponse**:
```json
{
  "id": 1,
  "code_apogee": "12345678",
  "nom": "Dupont",
  "prenom": "Jean-Michel",
  "email": "jean.dupont@example.com",
  "telephone": "+33612345678",
  "annee": 4,
  "filiere": {
    "id": 1,
    "nom": "Génie Logiciel"
  },
  "departement": {
    "id": 1,
    "nom": "Informatique"
  },
  "date_creation": "2023-05-16T09:00:00",
  "date_modification": "2023-05-16T11:30:00"
}
```

### Suppression d'un étudiant

**Endpoint**: `DELETE /api/admin/etudiants/<id>/`

**Description**: Supprime un étudiant.

**Codes de retour**:
- 204: Suppression réussie

## Codes d'état HTTP

- 200: Requête réussie (GET, PUT)
- 201: Ressource créée avec succès (POST)
- 204: Ressource supprimée avec succès (DELETE)
- 400: Erreur de validation des données
- 401: Non authentifié ou token JWT invalide
- 403: Non autorisé (permissions insuffisantes)
- 404: Ressource non trouvée
- 500: Erreur serveur

## Exemples de requêtes avec cURL

### Connexion et récupération du token
```bash
curl -X POST http://127.0.0.1:8000/api/auth-sql/login/ \
  -H "Content-Type: application/json" \
  -d '{"nom_utilisateur": "admin", "mot_de_passe": "admin"}'
```

### Création d'un département
```bash
curl -X POST http://127.0.0.1:8000/api/admin/departements/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"nom": "Informatique", "description": "Département informatique"}'
```

### Liste des filières
```bash
curl -X GET http://127.0.0.1:8000/api/admin/filieres/ \
  -H "Authorization: Bearer <token>"
``` 