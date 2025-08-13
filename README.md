# Epic Events – CRM interne
Description:

Un système de gestion de la relation client (CRM) interne pour Epic Events, développé en Python, 
permettant de gérer les clients, les contrats et les événements de manière sécurisée, 
avec authentification, autorisations, et journalisation via Sentry.

# Fonctionnalités
**Gestion des clients** : création, lecture, modification et suppression.

**Gestion des contrats** : suivi des contrats et des signatures.

**Gestion des événements** : planification et suivi.

**Authentification sécurisée** : stockage haché et salé des mots de passe.

**Système de rôles et permissions** : accès différencié selon le département.

**Journalisation via Sentry** : suivi des erreurs et des opérations critiques.

**Interface CLI**: conviviale avec click et rich.


# Prerequis
* Langage : Python 3.13
* Base de données : PostgreSQL (ou autre moteur compatible)
* ORM : SQLAlchemy
* Authentification : bcrypt / argon2 + JWT (pyjwt)
* Interface : click, rich
* Journalisation : Sentry
* Tests : pytest
* Outils qualité : flake8, black

# Installation
## Etape 1: Cloner le dépôt
    git clone https://github.com/Laureopen/Projet12.git
## Etape 2: Se mettre a la racine du projet
    cd Projet12 puis ensuite cd '.\Epic Events\'
## Etape 3: Pour créer et activer un environnement virtuel
    python -m venv 
    source venv/bin/activate  # Mac/Linux
    venv\Scripts\activate     # Windows
## Etape 4: Installer les dépendances
    pip install -r requirements.txt
## Etape 5: Lancer le programme
    python epicevents.py

