# Quiz FAQ 20 · Achzod

Nouveau parcours : `/faq`. Le quiz historique à `/` reste inchangé.

- 20 situations avancées : 5 métabolisme, 5 biomécanique, 5 nutrition, 5 compléments.
- Quatre propositions, ordre des réponses mélangé par session, corrigé réservé au serveur jusqu’à validation.
- Email capturé, score et réponses persistants dans `faq_sessions` ; file de livraison dans `faq_outbox`.
- Corrigé HTML complet envoyé via SendPulse ; reçu SMTP relu par identifiant avant statut `sent`.
- Newsletter facultative, double opt-in : seule une confirmation personnelle reçue par mail ajoute l’adresse à **My emails / 128647**. Aucun compte QA n’est ajouté.
- CTA coaching : **BLOOD99**, **99 € de réduction**.
- Conservation des données FAQ : 30 jours, nettoyage horaire. Un arrêt ambigu d’envoi est soumis à vérification, jamais renvoyé aveuglément.

## Production FAQ

Commande : `uvicorn app.faq_main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips='*'` (proxy Render, un processus).

Variables :
- `FAQ_DATABASE_URL` : SQLite sur disque Render persistant `/var/data/faq.sqlite`, ou URL PostgreSQL.
- `FAQ_SENDPULSE_API_KEY` : clé API native, transmise directement en Bearer ; pas en secret OAuth.
- `FAQ_SECRET`, `FAQ_ADMIN_TOKEN` : secrets aléatoires distincts.
- `FAQ_PUBLIC_URL` : origine publique, utilisée dans les liens du corrigé.
- `FAQ_SENDER_EMAIL`, `FAQ_SENDER_NAME` : expéditeur vérifié.

Contrôle : `/api/faq/health`. Statut opérateur : `/api/faq/admin/status` avec l’en-tête `X-FAQ-Admin` ; aucune adresse ni réponse personnelle dans ce statut.

Tests : `python -m pytest tests/ -q`. QA navigateur et reçus opérateur conservés hors dépôt dans `tasks/faq_quiz_20261013` du workspace.

---

# Quiz Mitochondries - Achzod Coaching

Quiz interactif de 35 questions basé sur la vidéo YouTube d'Achzod sur les mitochondries, la récupération et l'optimisation de la performance.

## Fonctionnalités

✅ **35 questions QCM** couvrant tous les concepts clés :
- HRV et récupération
- Magnésium et stress (cycle vicieux)
- COMT et neurotransmetteurs
- Sommeil au niveau moléculaire
- Hormone de croissance et sécrétogènes
- Peptides mitochondriaux (MOTS-c, SLU-PP-332)
- Bleu de méthylène
- Antioxydants et stress oxydatif
- Agonistes GLP

✅ **Système de scoring automatique** avec calcul du pourcentage

✅ **Email automatique** avec :
- Score final
- Corrections détaillées pour chaque erreur
- Explications pédagogiques

✅ **Code promo QUIZZ25** (-25% sur tous les coachings)

✅ **Design Achzod Styleguide** :
- Couleurs : #101010, #9990EA, #8DFFE0, #FFFFFF
- Fonts : Black Ops One (titres), Inter (body)
- Bordures épaisses, gradients, pas de border-radius

## Installation

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## Configuration

Les variables d'environnement pour l'envoi d'emails :
- `MAIL_USER` : coaching@achzodcoaching.com
- `MAIL_PASS` : (mot de passe app Gmail)

## Lancement

```bash
# En développement
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001

# En production
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Le quiz sera accessible sur : http://localhost:8001

## Structure du projet

```
achzod_quiz_mitochondries/
├── app/
│   ├── __init__.py
│   ├── main.py              # Serveur FastAPI
│   ├── questions.py         # 35 questions QCM
│   └── email_sender.py      # Envoi emails avec corrections
├── static/
│   └── style.css            # Styles Achzod
├── templates/
│   └── index.html           # Interface quiz
├── requirements.txt
└── README.md
```

## Déploiement sur Render

1. Push le code sur GitHub
2. Créer un nouveau Web Service sur Render
3. Connecter le repository
4. Configuration :
   - Build Command : `pip install -r requirements.txt`
   - Start Command : `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables : `MAIL_USER` et `MAIL_PASS`

## Technologies

- **FastAPI** : Framework web Python moderne et rapide
- **Jinja2** : Moteur de templates
- **SMTP Gmail** : Envoi d'emails
- **JavaScript Vanilla** : Interface interactive
- **CSS3** : Design Achzod styleguide

## Auteur

Achzod - Expert en Performance Humaine et Pharmacologie Avancée
https://www.achzodcoaching.com
