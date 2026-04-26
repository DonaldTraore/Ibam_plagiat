# Système de Détection de Plagiat - Backend

Backend Django REST Framework pour le système de détection de plagiat de l'IBAM.

## Architecture

Le backend est organisé en plusieurs applications Django:

- **accounts**: Gestion des utilisateurs (étudiants, chefs de département, DA, secrétaires)
- **reports**: Gestion des rapports et détection de plagiat
- **themes**: Gestion des thèmes et vérification de similarité
- **history**: Historique et traçabilité des actions
- **notifications**: Système de notifications
- **documents**: Gestion des documents de référence
- **api**: Endpoints généraux et tableau de bord

## Prérequis

- Python 3.9+
- PostgreSQL 12+
- Redis (pour Celery)

## Installation

1. Créer un environnement virtuel:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. Installer les dépendances:
```bash
pip install -r requirements.txt
```

3. Configurer la base de données dans `.env`:
```
DB_NAME=plagiarism_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

4. Créer la base de données:
```bash
createdb plagiarism_db
```

5. Lancer les migrations:
```bash
python manage.py migrate
```

6. Créer un superutilisateur:
```bash
python manage.py createsuperuser
```

7. Lancer le serveur:
```bash
python manage.py runserver
```

## Développement

### Lancer le worker Celery:
```bash
celery -A plagiarism_detection worker -l info
```

### Lancer le beat Celery (pour les tâches périodiques):
```bash
celery -A plagiarism_detection beat -l info
```

## API Documentation

La documentation de l'API est disponible via Swagger:
- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## Endpoints principaux

### Authentification
- `POST /api/token/` - Obtenir un token JWT
- `POST /api/token/refresh/` - Rafraîchir le token

### Utilisateurs
- `GET /api/auth/users/` - Liste des utilisateurs
- `GET /api/auth/me/` - Profil de l'utilisateur connecté

### Rapports
- `GET /api/reports/` - Liste des rapports
- `POST /api/reports/create/` - Créer un rapport
- `POST /api/reports/{id}/test-plagiarism/` - Tester le plagiat
- `POST /api/reports/{id}/submit/` - Soumettre un rapport
- `POST /api/reports/{id}/validate/` - Valider/Rejeter un rapport

### Thèmes
- `GET /api/themes/` - Liste des thèmes
- `POST /api/themes/create/` - Créer un thème
- `POST /api/themes/{id}/test-similarity/` - Tester la similarité
- `POST /api/themes/{id}/submit/` - Soumettre un thème

### Documents de référence
- `GET /api/documents/` - Liste des documents
- `POST /api/documents/create/` - Ajouter un document

## Fonctionnalités de détection de plagiat

### Détection par chapitre
Le système divise automatiquement les rapports en chapitres et calcule un score de plagiat pour chaque chapitre. Le score global est une moyenne pondérée par le nombre de mots de chaque chapitre.

### Algorithme de détection
- Extraction du contenu textuel (PDF, DOCX, TXT)
- Segmentation en phrases
- Comparaison avec les documents de référence de la base de données
- Calcul de similarité avec TF-IDF et cosine similarity
- Identification des passages plagiés avec leurs sources

### Seuil de plagiat
Par défaut, le seuil est fixé à 25%. Au-delà de ce seuil, le rapport est considéré comme plagiat et nécessite une validation manuelle par le DA.

## Contribution

1. Créer une branche: `git checkout -b feature/nom-feature`
2. Commiter les changements: `git commit -am 'Ajout de la feature'`
3. Pousser vers la branche: `git push origin feature/nom-feature`
4. Créer une Pull Request

## Licence

Propriété de l'IBAM - Tous droits réservés
