#!/bin/bash

echo "🚀 Démarrage d'Agent Zero..."
echo "=================================="

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez l'installer d'abord :"
    echo "   - Windows/Mac: https://www.docker.com/products/docker-desktop/"
    echo "   - Linux: https://docs.docker.com/engine/install/"
    exit 1
fi

# Vérifier si Docker fonctionne
if ! docker info &> /dev/null; then
    echo "❌ Docker n'est pas démarré. Veuillez démarrer Docker Desktop."
    exit 1
fi

echo "✅ Docker détecté et fonctionnel"

# Configuration par défaut
A0_PORT=${A0_PORT:-50080}
A0_VOLUME=${A0_VOLUME:-$(pwd)/agent-zero-data}
A0_BRANCH=${A0_BRANCH:-main}

echo "📋 Configuration :"
echo "   - Port Web UI: $A0_PORT"
echo "   - Dossier de données: $A0_VOLUME"
echo "   - Branche Git: $A0_BRANCH"

# Créer le dossier de données s'il n'existe pas
mkdir -p "$A0_VOLUME"
echo "✅ Dossier de données créé : $A0_VOLUME"

# Télécharger l'image Docker
echo "📥 Téléchargement de l'image Agent Zero..."
docker pull agent0ai/agent-zero:latest

if [ $? -ne 0 ]; then
    echo "❌ Échec du téléchargement de l'image Docker"
    exit 1
fi

echo "✅ Image Docker téléchargée"

# Arrêter le conteneur existant s'il existe
if docker ps -a --format "table {{.Names}}" | grep -q "^agent-zero$"; then
    echo "🛑 Arrêt du conteneur existant..."
    docker stop agent-zero 2>/dev/null
    docker rm agent-zero 2>/dev/null
fi

# Démarrer le conteneur
echo "🚀 Démarrage du conteneur Agent Zero..."
docker run -d \
    --name agent-zero \
    -p $A0_PORT:80 \
    -v "$A0_VOLUME:/a0" \
    agent0ai/agent-zero:latest

if [ $? -eq 0 ]; then
    echo "✅ Agent Zero démarré avec succès !"
    echo ""
    echo "🌐 Interface Web disponible sur :"
    echo "   http://localhost:$A0_PORT"
    echo ""
    echo "📁 Données persistantes dans :"
    echo "   $A0_VOLUME"
    echo ""
    echo "⏳ Attendez 30-60 secondes que le système s'initialise complètement"
    echo ""
    echo "📖 Pour suivre les logs :"
    echo "   docker logs -f agent-zero"
else
    echo "❌ Échec du démarrage du conteneur"
    exit 1
fi