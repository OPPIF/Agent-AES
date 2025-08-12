#!/bin/bash

echo "🔄 Mise à jour d'Agent Zero..."
echo "=============================="

# Configuration
A0_PORT=${A0_PORT:-50080}
A0_VOLUME=${A0_VOLUME:-$(pwd)/agent-zero-data}

echo "📋 Configuration actuelle :"
echo "   - Port Web UI: $A0_PORT"
echo "   - Dossier de données: $A0_VOLUME"

# Vérifier si le conteneur existe
if ! docker ps -a --format "table {{.Names}}" | grep -q "^agent-zero$"; then
    echo "❌ Aucun conteneur Agent Zero trouvé. Utilisez start-agent-zero.sh d'abord."
    exit 1
fi

# Créer une sauvegarde avant la mise à jour
echo "💾 Création d'une sauvegarde..."
BACKUP_DIR="$A0_VOLUME/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Copier les fichiers importants
if [ -d "$A0_VOLUME" ]; then
    cp -r "$A0_VOLUME/memory" "$BACKUP_DIR/" 2>/dev/null || true
    cp -r "$A0_VOLUME/knowledge" "$BACKUP_DIR/" 2>/dev/null || true
    cp -r "$A0_VOLUME/tmp" "$BACKUP_DIR/" 2>/dev/null || true
    cp "$A0_VOLUME/.env" "$BACKUP_DIR/" 2>/dev/null || true
    echo "✅ Sauvegarde créée dans : $BACKUP_DIR"
fi

# Arrêter le conteneur actuel
echo "🛑 Arrêt du conteneur actuel..."
docker stop agent-zero
docker rm agent-zero

# Supprimer l'ancienne image
echo "🗑️ Suppression de l'ancienne image..."
docker rmi agent0ai/agent-zero:latest 2>/dev/null || true

# Télécharger la nouvelle image
echo "📥 Téléchargement de la nouvelle image..."
docker pull agent0ai/agent-zero:latest

if [ $? -ne 0 ]; then
    echo "❌ Échec du téléchargement de la nouvelle image"
    echo "🔄 Tentative de restauration..."
    # Redémarrer avec l'ancienne configuration
    docker run -d \
        --name agent-zero \
        -p $A0_PORT:80 \
        -v "$A0_VOLUME:/a0" \
        agent0ai/agent-zero:latest
    exit 1
fi

# Redémarrer avec la nouvelle image
echo "🚀 Redémarrage avec la nouvelle image..."
docker run -d \
    --name agent-zero \
    -p $A0_PORT:80 \
    -v "$A0_VOLUME:/a0" \
    agent0ai/agent-zero:latest

if [ $? -eq 0 ]; then
    echo "✅ Agent Zero mis à jour avec succès !"
    echo ""
    echo "🌐 Interface Web disponible sur :"
    echo "   http://localhost:$A0_PORT"
    echo ""
    echo "💾 Sauvegarde disponible dans :"
    echo "   $BACKUP_DIR"
    echo ""
    echo "⏳ Attendez 30-60 secondes que le système s'initialise"
else
    echo "❌ Échec de la mise à jour"
    exit 1
fi