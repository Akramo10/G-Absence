# API d'Authentification avec JWT

Cette API permet l'authentification des utilisateurs avec JWT et la gestion des rôles (admin/enseignant).

## Fonctionnalités principales

- Authentification via JWT avec PostgreSQL et psycopg2 (sans ORM)
- Vérification des mots de passe hashés en SHA256
- Gestion des rôles utilisateur (admin/enseignant)
- Middleware d'authentification automatique
- Décorateurs pour protéger les routes par rôle

## Endpoints

### `/api/auth/login/` (POST)

Authentifie un utilisateur et génère un token JWT.

**Requête**:

```json
{
  "nom_utilisateur": "utilisateur",
  "mot_de_passe": "motdepasse"
}
```

**Réponse** (Succès):

```json
{
  "status": "success",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "type_utilisateur": "admin"
}
```

### Routes protégées

- `/api/auth/admin-dashboard/`: Accessible uniquement aux administrateurs
- `/api/auth/enseignant-dashboard/`: Accessible uniquement aux enseignants
- `/api/auth/common-dashboard/`: Accessible aux deux types d'utilisateurs

## Exemples de Tokens JWT

### Exemple pour un administrateur

```
{
  "id_utilisateur": 1,
  "nom_utilisateur": "admin_user",
  "type_utilisateur": "admin",
  "exp": 1620000000
}
```

Encodé (exemple): `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZF91dGlsaXNhdGV1ciI6MSwibm9tX3V0aWxpc2F0ZXVyIjoiYWRtaW5fdXNlciIsInR5cGVfdXRpbGlzYXRldXIiOiJhZG1pbiIsImV4cCI6MTYyMDAwMDAwMH0.8kKrOKq6RFzHEQC5-I6PUHoCz6WuQzsZJnAH3Nb8rkE`

### Exemple pour un enseignant

```
{
  "id_utilisateur": 2,
  "nom_utilisateur": "prof_user",
  "type_utilisateur": "enseignant",
  "exp": 1620000000
}
```

Encodé (exemple): `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZF91dGlsaXNhdGV1ciI6Miwibm9tX3V0aWxpc2F0ZXVyIjoicHJvZl91c2VyIiwidHlwZV91dGlsaXNhdGV1ciI6ImVuc2VpZ25hbnQiLCJleHAiOjE2MjAwMDAwMDB9.7GMJAakAhvU0-YGoC0H1NnSkyP4LIe-X0Ej5TQqNb7Q`

## Utilisation dans le Frontend

### Redirection basée sur le rôle

Après authentification, le frontend peut rediriger l'utilisateur vers la bonne interface en fonction de `type_utilisateur` dans le token décodé:

```javascript
// Exemple de code frontend (React/Vue.js)
function handleLogin(token) {
  // Décoder le token
  const decodedToken = jwt_decode(token);
  
  // Rediriger en fonction du rôle
  if (decodedToken.type_utilisateur === 'admin') {
    router.push('/admin-dashboard');
  } else if (decodedToken.type_utilisateur === 'enseignant') {
    router.push('/enseignant-dashboard');
  }
}
```

## Tests avec Postman

Pour tester avec Postman, envoyez une requête POST à `/api/auth/login/` avec les identifiants. Puis utilisez le token obtenu dans les en-têtes d'authentification des autres requêtes:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Structure de la base de données

Table `utilisateur`:
- `id_utilisateur`: int (PK)
- `nom_utilisateur`: varchar
- `mot_de_passe_hash`: varchar (SHA256)
- `email`: varchar
- `type_utilisateur`: varchar (enum: 'admin' ou 'enseignant') 