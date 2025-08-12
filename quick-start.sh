#!/bin/bash

echo "⚡ Agent Zero - Démarrage Ultra-Rapide"
echo "====================================="

# Vérifications rapides
if ! command -v docker &> /dev/null; then
    echo "❌ Docker requis. Installez-le depuis : https://docker.com"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Démarrez Docker Desktop d'abord"
    exit 1
fi

# Configuration express
export A0_PORT=${A0_PORT:-50080}
export A0_VOLUME=${A0_VOLUME:-$(pwd)/agent-zero-data}

echo "🚀 Démarrage avec Docker Compose..."

# Créer le dossier de données
mkdir -p "$A0_VOLUME"

# Démarrer avec Docker Compose
docker-compose up -d

echo ""
echo "✅ Agent Zero démarré !"
echo "🌐 Interface : http://localhost:$A0_PORT"
echo "📁 Données : $A0_VOLUME"
echo ""
echo "⏳ Attendez 1-2 minutes pour l'initialisation complète"
echo ""
echo "📋 Commandes utiles :"
echo "   docker-compose logs -f     # Voir les logs"
echo "   docker-compose restart     # Redémarrer"
echo "   docker-compose down        # Arrêter"
echo "   ./check-updates.sh         # Vérifier les mises à jour"