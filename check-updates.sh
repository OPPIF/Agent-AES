#!/bin/bash

echo "🔍 Vérification des mises à jour Agent Zero..."
echo "============================================="

# Fonction pour obtenir la version locale
get_local_version() {
    if docker images --format "table {{.Repository}}:{{.Tag}}\t{{.CreatedAt}}" | grep "agent0ai/agent-zero:latest" | head -1; then
        return 0
    else
        echo "Aucune image locale trouvée"
        return 1
    fi
}

# Fonction pour vérifier les mises à jour GitHub
check_github_updates() {
    echo "📡 Vérification des dernières versions sur GitHub..."
    
    # Obtenir la dernière release
    LATEST_RELEASE=$(curl -s https://api.github.com/repos/agent0ai/agent-zero/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
    
    if [ -n "$LATEST_RELEASE" ]; then
        echo "🏷️ Dernière version disponible : $LATEST_RELEASE"
        
        # Obtenir les notes de version
        RELEASE_NOTES=$(curl -s https://api.github.com/repos/agent0ai/agent-zero/releases/latest | grep '"body":' | sed -E 's/.*"body":"([^"]+)".*/\1/' | sed 's/\\n/\n/g')
        
        echo ""
        echo "📝 Notes de version :"
        echo "$RELEASE_NOTES" | head -10
        echo ""
    else
        echo "❌ Impossible de récupérer les informations de version"
    fi
}

# Fonction pour vérifier les mises à jour Docker Hub
check_docker_updates() {
    echo "🐳 Vérification des mises à jour sur Docker Hub..."
    
    # Obtenir les informations de l'image locale
    LOCAL_IMAGE_ID=$(docker images agent0ai/agent-zero:latest --format "{{.ID}}" 2>/dev/null)
    
    if [ -n "$LOCAL_IMAGE_ID" ]; then
        echo "🏠 Image locale : $LOCAL_IMAGE_ID"
        
        # Vérifier s'il y a une nouvelle image disponible
        docker pull agent0ai/agent-zero:latest --quiet
        NEW_IMAGE_ID=$(docker images agent0ai/agent-zero:latest --format "{{.ID}}" 2>/dev/null)
        
        if [ "$LOCAL_IMAGE_ID" != "$NEW_IMAGE_ID" ]; then
            echo "🆕 Nouvelle image disponible !"
            echo "   Ancienne : $LOCAL_IMAGE_ID"
            echo "   Nouvelle : $NEW_IMAGE_ID"
            echo ""
            echo "💡 Pour mettre à jour, exécutez : ./update-agent-zero.sh"
        else
            echo "✅ Votre image Docker est à jour"
        fi
    else
        echo "❌ Aucune image locale trouvée"
    fi
}

# Afficher la version locale actuelle
echo "📦 Version locale actuelle :"
get_local_version

echo ""

# Vérifier les mises à jour
check_github_updates
echo ""
check_docker_updates

echo ""
echo "🔗 Liens utiles :"
echo "   - Releases GitHub : https://github.com/agent0ai/agent-zero/releases"
echo "   - Documentation : https://github.com/agent0ai/agent-zero/blob/main/docs/README.md"
echo "   - Discord : https://discord.gg/B8KZKNsPpj"