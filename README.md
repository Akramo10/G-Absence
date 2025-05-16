# Système de Gestion d'Absences

Plateforme de gestion des absences pour établissements d'enseignement, développée avec Django et PostgreSQL.

## Fonctionnalités

- Authentification sécurisée avec JWT (JSON Web Tokens)
- Gestion des utilisateurs avec différents rôles (admin, enseignant)
- Connexion directe à une base de données PostgreSQL avec psycopg2 (sans ORM)
- Contrôle d'accès basé sur les rôles
- API REST pour l'intégration avec des applications frontend

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/Akramo10/G-Absence.git
cd G-Absence
```

2. Créer un environnement virtuel et l'activer :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer la base de données PostgreSQL dans `settings.py`

5. Lancer le serveur de développement :
```bash
python manage.py runserver
```

## API d'Authentification

Le système utilise une API d'authentification par JWT pour sécuriser l'accès :

- POST `/api/auth-sql/login/` : Authentification et génération de token
- GET `/api/auth-sql/admin-dashboard/` : Dashboard administrateur
- GET `/api/auth-sql/enseignant-dashboard/` : Dashboard enseignant
- GET `/api/auth-sql/common-dashboard/` : Dashboard commun

## Structure de la base de données

Table `utilisateur` :
- `id_utilisateur` (PK)
- `nom_utilisateur`
- `mot_de_passe_hash` (SHA256)
- `email`
- `type_utilisateur` (ENUM: 'admin' ou 'enseignant')

## Technologies utilisées

- Django
- PostgreSQL
- psycopg2
- PyJWT
- REST Framework

## Développeurs

- Akram 