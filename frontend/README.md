# Frontend Angular - Système de Détection de Plagiat

Ce projet est le frontend Angular du système de détection de plagiat de l'IBAM.

## Prérequis

- Node.js 16+
- npm 8+

## Installation

```bash
# Installation des dépendances
npm install

# Démarrage du serveur de développement
ng serve
```

L'application sera accessible à l'adresse `http://localhost:4200`.

## Structure du projet

```
src/
├── app/
│   ├── components/          # Composants réutilisables
│   │   ├── layout/         # Navbar, Sidebar, Footer
│   │   ├── shared/         # Composants partagés
│   │   └── reports/        # Composants spécifiques aux rapports
│   ├── pages/              # Pages de l'application
│   │   ├── auth/           # Login
│   │   ├── dashboard/      # Tableau de bord
│   │   ├── reports/        # Gestion des rapports
│   │   ├── themes/         # Gestion des thèmes
│   │   ├── documents/      # Documents de référence
│   │   ├── notifications/  # Notifications
│   │   └── history/        # Historique
│   ├── services/           # Services (API, Auth, etc.)
│   ├── guards/             # Guards de routage
│   ├── interceptors/       # Interceptors HTTP
│   └── models/             # Interfaces TypeScript
├── assets/                 # Ressources statiques
└── environments/           # Configurations d'environnement
```

## Fonctionnalités

- 🔐 Authentification JWT
- 📊 Tableau de bord avec statistiques
- 📝 Gestion des rapports (création, soumission, validation)
- 🎯 Gestion des thèmes
- 🔍 Détection de plagiat par chapitre
- 🔔 Système de notifications
- 📜 Historique des actions

## Technologies utilisées

- Angular 16
- Angular Material
- RxJS
- Chart.js (pour les graphiques)

## Rôles utilisateurs

- **Étudiant**: Soumet des rapports et thèmes, tests privés
- **Chef de Département**: Valide les rapports et thèmes de son département
- **DA (Directeur Académique)**: Validation finale, rejet avec motifs
- **Secrétaire**: Gestion des documents de référence

## Développement

### Génération d'un composant
```bash
ng generate component nom-du-composant
```

### Build pour production
```bash
ng build --configuration production
```

## Licence

Propriété de l'IBAM - Tous droits réservés
