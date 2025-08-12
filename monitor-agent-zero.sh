#!/bin/bash

echo "📊 Monitoring Agent Zero..."
echo "=========================="

# Fonction pour afficher le statut
show_status() {
    echo "🔍 Statut du conteneur :"
    if docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep agent-zero; then
        echo "✅ Agent Zero est en cours d'exécution"
    else
        echo "❌ Agent Zero n'est pas en cours d'exécution"
        if docker ps -a --format "table {{.Names}}\t{{.Status}}" | grep agent-zero; then
            echo "💡 Le conteneur existe mais est arrêté. Redémarrez avec :"
            echo "   docker start agent-zero"
        else
            echo "💡 Aucun conteneur trouvé. Démarrez avec :"
            echo "   ./start-agent-zero.sh"
        fi
        return 1
    fi
}

# Fonction pour afficher les logs
show_logs() {
    echo ""
    echo "📋 Derniers logs (10 lignes) :"
    echo "------------------------------"
    docker logs --tail 10 agent-zero 2>/dev/null || echo "❌ Impossible de récupérer les logs"
}

# Fonction pour afficher les statistiques
show_stats() {
    echo ""
    echo "📈 Statistiques du conteneur :"
    echo "------------------------------"
    docker stats agent-zero --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" 2>/dev/null || echo "❌ Conteneur non trouvé"
}

# Fonction pour vérifier l'accès web
check_web_access() {
    echo ""
    echo "🌐 Vérification de l'accès web :"
    echo "--------------------------------"
    
    # Obtenir le port mappé
    PORT=$(docker port agent-zero 80 2>/dev/null | cut -d: -f2)
    
    if [ -n "$PORT" ]; then
        echo "🔗 URL : http://localhost:$PORT"
        
        # Tester la connectivité
        if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT" | grep -q "200\|302\|401"; then
            echo "✅ Interface web accessible"
        else
            echo "⚠️ Interface web non accessible (le système démarre peut-être encore)"
        fi
    else
        echo "❌ Port non trouvé"
    fi
}

# Menu interactif
while true; do
    clear
    echo "📊 Agent Zero - Monitoring"
    echo "=========================="
    echo ""
    
    show_status
    
    echo ""
    echo "Options disponibles :"
    echo "1) Afficher les logs en temps réel"
    echo "2) Afficher les statistiques"
    echo "3) Vérifier l'accès web"
    echo "4) Redémarrer Agent Zero"
    echo "5) Arrêter Agent Zero"
    echo "6) Vérifier les mises à jour"
    echo "7) Quitter"
    echo ""
    read -p "Choisissez une option (1-7) : " choice
    
    case $choice in
        1)
            echo "📋 Logs en temps réel (Ctrl+C pour arrêter) :"
            docker logs -f agent-zero
            ;;
        2)
            show_stats
            read -p "Appuyez sur Entrée pour continuer..."
            ;;
        3)
            check_web_access
            read -p "Appuyez sur Entrée pour continuer..."
            ;;
        4)
            echo "🔄 Redémarrage d'Agent Zero..."
            docker restart agent-zero
            echo "✅ Redémarrage effectué"
            sleep 2
            ;;
        5)
            echo "🛑 Arrêt d'Agent Zero..."
            docker stop agent-zero
            echo "✅ Agent Zero arrêté"
            read -p "Appuyez sur Entrée pour continuer..."
            ;;
        6)
            ./check-updates.sh
            read -p "Appuyez sur Entrée pour continuer..."
            ;;
        7)
            echo "👋 Au revoir !"
            exit 0
            ;;
        *)
            echo "❌ Option invalide"
            sleep 1
            ;;
    esac
done