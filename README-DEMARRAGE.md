# 🚀 Guide de Démarrage Agent Zero

Ce guide vous aidera à démarrer rapidement Agent Zero et à configurer le suivi des mises à jour.

## 📋 Prérequis

1. **Docker Desktop** installé et en cours d'exécution
   - Windows/Mac : [Télécharger Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Linux : [Instructions d'installation](https://docs.docker.com/engine/install/)

## 🚀 Démarrage Rapide

### 1. Démarrer Agent Zero

```bash
# Rendre le script exécutable
chmod +x start-agent-zero.sh

# Démarrer Agent Zero
./start-agent-zero.sh
```

**Variables d'environnement optionnelles :**
```bash
# Personnaliser le port (défaut: 50080)
A0_PORT=8080 ./start-agent-zero.sh

# Personnaliser le dossier de données
A0_VOLUME="/mon/dossier/agent-zero" ./start-agent-zero.sh

# Utiliser une branche spécifique
A0_BRANCH=development ./start-agent-zero.sh
```

### 2. Accéder à l'Interface

1. Attendez 30-60 secondes que le système s'initialise
2. Ouvrez votre navigateur sur : `http://localhost:50080` (ou votre port personnalisé)
3. Configurez vos clés API dans les paramètres

## 🔄 Suivi des Mises à Jour

### Vérifier les mises à jour disponibles

```bash
chmod +x check-updates.sh
./check-updates.sh
```

### Mettre à jour vers la dernière version

```bash
chmod +x update-agent-zero.sh
./update-agent-zero.sh
```

### Monitoring en temps réel

```bash
chmod +x monitor-agent-zero.sh
./monitor-agent-zero.sh
```

## 📁 Structure des Données

Vos données Agent Zero sont stockées dans le dossier configuré (défaut: `./agent-zero-data/`) :

```
agent-zero-data/
├── memory/          # Mémoire de l'agent
├── knowledge/       # Base de connaissances
├── tmp/            # Fichiers temporaires et paramètres
├── work_dir/       # Répertoire de travail
├── instruments/    # Outils personnalisés
├── agents/         # Agents spécialisés
└── .env           # Clés API et configuration
```

## 🛠️ Commandes Utiles

### Gestion du conteneur
```bash
# Voir les logs en temps réel
docker logs -f agent-zero

# Redémarrer
docker restart agent-zero

# Arrêter
docker stop agent-zero

# Supprimer (attention : sauvegardez d'abord !)
docker rm agent-zero
```

### Sauvegarde manuelle
```bash
# Créer une sauvegarde complète
tar -czf "backup-$(date +%Y%m%d_%H%M%S).tar.gz" agent-zero-data/

# Restaurer une sauvegarde
tar -xzf backup-YYYYMMDD_HHMMSS.tar.gz
```

## 🔧 Configuration Initiale

1. **Clés API** : Configurez vos clés API dans Paramètres > API Keys
   - OpenAI, Anthropic, Google, etc.
   
2. **Modèles** : Choisissez vos modèles dans Paramètres > Chat Model
   - Recommandé : OpenRouter avec GPT-4
   
3. **Mémoire** : Configurez la mémoire dans Paramètres > Memory
   - Activez la mémorisation automatique

## 🆘 Dépannage

### Le conteneur ne démarre pas
```bash
# Vérifier Docker
docker --version
docker info

# Vérifier les ports
netstat -tulpn | grep :50080
```

### Interface web inaccessible
```bash
# Vérifier le port mappé
docker port agent-zero

# Vérifier les logs
docker logs agent-zero
```

### Problèmes de permissions
```bash
# Corriger les permissions du dossier de données
sudo chown -R $USER:$USER agent-zero-data/
```

## 📚 Ressources

- [Documentation complète](https://github.com/agent0ai/agent-zero/blob/main/docs/README.md)
- [Guide d'installation détaillé](https://github.com/agent0ai/agent-zero/blob/main/docs/installation.md)
- [Communauté Discord](https://discord.gg/B8KZKNsPpj)
- [Chaîne YouTube](https://www.youtube.com/@AgentZeroFW)

## 🔄 Automatisation des Mises à Jour

Pour automatiser la vérification des mises à jour, ajoutez à votre crontab :

```bash
# Vérifier les mises à jour tous les jours à 9h
0 9 * * * /chemin/vers/check-updates.sh >> /var/log/agent-zero-updates.log 2>&1
```

---

**Prêt à commencer ?** Exécutez `./start-agent-zero.sh` pour démarrer votre aventure avec Agent Zero ! 🎉