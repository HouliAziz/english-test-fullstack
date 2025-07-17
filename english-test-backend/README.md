# English Test App Backend

Un backend Flask complet pour une application de test d'anglais avec génération de contenu IA, gestion des utilisateurs et suivi des statistiques.

## 🚀 Fonctionnalités

### Authentification et Gestion des Utilisateurs
- ✅ Inscription et connexion avec JWT
- ✅ Gestion des profils utilisateur
- ✅ Changement de mot de passe
- ✅ Niveaux d'apprentissage (beginner, intermediate, advanced)

### Génération de Contenu IA
- ✅ Génération automatique de leçons avec OpenAI
- ✅ Génération automatique de quiz avec OpenAI
- ✅ Contenu adapté au niveau de l'utilisateur
- ✅ Support de différents sujets (grammaire, vocabulaire, etc.)

### Système de Quiz
- ✅ Quiz à choix multiples
- ✅ Calcul automatique des scores
- ✅ Suivi des tentatives
- ✅ Correction automatique avec explications

### Statistiques et Analytics
- ✅ Dashboard utilisateur complet
- ✅ Suivi des progrès par sujet
- ✅ Système d'achievements et badges
- ✅ Classement (leaderboard)
- ✅ Recommandations personnalisées
- ✅ Export des données

## 🏗️ Architecture

### Modèles de Données
- **User**: Gestion des utilisateurs avec authentification
- **Lesson**: Leçons générées par IA
- **Quiz**: Quiz avec questions et réponses
- **QuizAttempt**: Tentatives de quiz des utilisateurs
- **UserStatistics**: Statistiques détaillées des utilisateurs

### API Endpoints

#### Authentification (`/api/auth/`)
- `POST /register` - Inscription
- `POST /login` - Connexion
- `GET /profile` - Profil utilisateur
- `PUT /profile` - Mise à jour du profil
- `POST /change-password` - Changement de mot de passe

#### Leçons (`/api/lessons/`)
- `GET /` - Liste des leçons
- `GET /{id}` - Détails d'une leçon
- `POST /generate` - Génération d'une nouvelle leçon
- `PUT /{id}` - Mise à jour d'une leçon
- `DELETE /{id}` - Suppression d'une leçon
- `GET /topics` - Sujets disponibles

#### Quiz (`/api/quizzes/`)
- `GET /` - Liste des quiz
- `GET /{id}` - Détails d'un quiz
- `GET /{id}/answers` - Quiz avec réponses (pour révision)
- `POST /generate` - Génération d'un nouveau quiz
- `POST /{id}/submit` - Soumission d'un quiz
- `GET /{id}/attempts` - Tentatives d'un quiz
- `GET /my-attempts` - Toutes les tentatives de l'utilisateur
- `PUT /{id}` - Mise à jour d'un quiz
- `DELETE /{id}` - Suppression d'un quiz

#### Statistiques (`/api/statistics/`)
- `GET /dashboard` - Dashboard utilisateur
- `GET /progress` - Progrès détaillés
- `GET /leaderboard` - Classement
- `GET /achievements` - Achievements et badges
- `GET /export` - Export des données

## 🛠️ Installation et Configuration

### Prérequis
- Python 3.11+
- pip
- SQLite (inclus)

### Installation
```bash
# Cloner le projet
git clone <repository-url>
cd english-test-backend

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\\Scripts\\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement (optionnel)
export OPENAI_API_KEY="your-openai-api-key"
export OPENAI_API_BASE="https://api.openai.com/v1"
```

### Démarrage
```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Démarrer le serveur
python src/main.py
```

Le serveur sera accessible sur `http://localhost:5001`

## 🧪 Tests

### Tests Automatisés
```bash
# Exécuter les tests complets
python test_api.py
```

### Tests Manuels avec curl
```bash
# Inscription
curl -X POST http://localhost:5001/api/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'

# Connexion
curl -X POST http://localhost:5001/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"username": "testuser", "password": "password123"}'

# Génération de leçon (avec token)
curl -X POST http://localhost:5001/api/lessons/generate \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -d '{"topic": "Present Simple", "level": "beginner"}'
```

## 🌐 Déploiement

### URL Publique
Le backend est accessible publiquement à l'adresse :
**https://5001-infzkotfgutpg9etsdao2-fec7a7a5.manusvm.computer**

### Configuration CORS
Le backend est configuré pour accepter les requêtes de toutes les origines (`CORS(app, origins="*")`), facilitant l'intégration avec le frontend.

## 📊 Base de Données

### Structure
- **SQLite** pour le développement
- **Migrations automatiques** au démarrage
- **Relations optimisées** entre les modèles

### Données d'exemple
Le système génère automatiquement :
- Statistiques utilisateur lors de l'inscription
- Contenu de fallback si l'IA n'est pas disponible
- Achievements basés sur l'activité

## 🔧 Configuration

### Variables d'Environnement
- `OPENAI_API_KEY`: Clé API OpenAI (optionnel)
- `OPENAI_API_BASE`: URL de base OpenAI (optionnel)
- `SECRET_KEY`: Clé secrète Flask (définie dans le code)

### Paramètres par Défaut
- **Port**: 5001
- **Host**: 0.0.0.0 (accessible externellement)
- **Debug**: True (développement)
- **Base de données**: SQLite (`src/database/app.db`)

## 🔐 Sécurité

### Authentification
- **JWT tokens** avec expiration (24h)
- **Hachage des mots de passe** avec Werkzeug
- **Validation des entrées** utilisateur

### API Protection
- **Middleware d'authentification** sur les routes protégées
- **Validation des données** d'entrée
- **Gestion des erreurs** sécurisée

## 📈 Performances

### Optimisations
- **Pagination** sur les listes
- **Requêtes optimisées** avec SQLAlchemy
- **Cache des statistiques** utilisateur
- **Fallback content** pour l'IA

### Monitoring
- **Logs détaillés** en mode debug
- **Métriques d'utilisation** dans les statistiques
- **Suivi des performances** des quiz

## 🤝 Intégration Frontend

### Headers Requis
```javascript
// Authentification
headers: {
  'Authorization': 'Bearer ' + token,
  'Content-Type': 'application/json'
}
```

### Exemples d'Intégration
```javascript
// Connexion
const login = async (username, password) => {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  return response.json();
};

// Génération de leçon
const generateLesson = async (topic, level, token) => {
  const response = await fetch('/api/lessons/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({ topic, level })
  });
  return response.json();
};
```

## 📝 Changelog

### Version 1.0.0
- ✅ Système d'authentification complet
- ✅ Génération de leçons et quiz avec IA
- ✅ Statistiques et analytics avancées
- ✅ API REST complète
- ✅ Tests automatisés
- ✅ Documentation complète
- ✅ Déploiement public

## 🐛 Dépannage

### Problèmes Courants
1. **Port déjà utilisé**: Changer le port dans `src/main.py`
2. **Erreurs de base de données**: Supprimer `src/database/app.db` et redémarrer
3. **Problèmes d'IA**: L'application fonctionne avec du contenu de fallback

### Support
- Vérifier les logs du serveur Flask
- Utiliser le script de test `test_api.py`
- Consulter la documentation des endpoints

## 📄 Licence

Ce projet est développé pour l'application English Test App.

---

**Développé avec ❤️ en utilisant Flask, SQLAlchemy, et OpenAI**

