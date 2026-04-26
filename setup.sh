#!/bin/bash

echo "=========================================="
echo "Setup - Système de Détection de Plagiat"
echo "=========================================="
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

echo "✅ Python 3 détecté"

# Vérifier pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 n'est pas installé"
    exit 1
fi

echo "✅ pip3 détecté"

# Vérifier Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js n'est pas installé"
    exit 1
fi

echo "✅ Node.js détecté"

# Backend Setup
echo ""
echo "📦 Installation du Backend..."
echo "================================"
cd backend

# Créer l'environnement virtuel
if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances
echo "Installation des dépendances Python..."
pip install -r requirements.txt

# Créer les migrations
echo "Création des migrations..."
python manage.py makemigrations

# Appliquer les migrations
echo "Application des migrations..."
python manage.py migrate

# Créer le superutilisateur (optionnel)
read -p "Voulez-vous créer un superutilisateur maintenant? (y/n): " create_superuser
if [ "$create_superuser" = "y" ]; then
    python manage.py createsuperuser
fi

cd ..

# Frontend Setup
echo ""
echo "📦 Installation du Frontend..."
echo "================================"
cd frontend

# Vérifier si node_modules existe
if [ ! -d "node_modules" ]; then
    echo "Installation des dépendances npm..."
    npm install
else
    echo "Les dépendances npm sont déjà installées"
fi

cd ..

echo ""
echo "=========================================="
echo "✅ Installation terminée!"
echo "=========================================="
echo ""
echo "Pour démarrer le backend:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Pour démarrer le frontend (dans un autre terminal):"
echo "  cd frontend"
echo "  ng serve"
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:4200"
echo "Admin: http://localhost:8000/admin"
echo ""
