<!-- markdownlint-disable MD013 -->
<!-- markdownlint-disable MD033 MD036 -->

<div align="center">

# 🚀 Git Auto Commit (`gac`)

[![PyPI version](https://img.shields.io/pypi/v/gac.svg)](https://pypi.org/project/gac/)
[![Python](https://img.shields.io/badge/python-3.10--3.14-blue.svg)](https://www.python.org/downloads/)
[![Build Status](https://github.com/cellwebb/gac/actions/workflows/ci.yml/badge.svg)](https://github.com/cellwebb/gac/actions)
[![codecov](https://codecov.io/gh/cellwebb/gac/branch/main/graph/badge.svg)](https://app.codecov.io/gh/cellwebb/gac)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://mypy-lang.org/)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](docs/fr/CONTRIBUTING.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](../../README.md) | [简体中文](../zh-CN/README.md) | [繁體中文](../zh-TW/README.md) | [日本語](../ja/README.md) | [한국어](../ko/README.md) | [हिन्दी](../hi/README.md) | [Tiếng Việt](../vi/README.md) | **Français** | [Русский](../ru/README.md) | [Español](../es/README.md) | [Português](../pt/README.md) | [Norsk](../no/README.md) | [Svenska](../sv/README.md) | [Deutsch](../de/README.md) | [Nederlands](../nl/README.md) | [Italiano](../it/README.md)

**Messages de commit alimentés par l'IA qui comprennent votre code !**

**Automatisez vos commits !** Remplacez `git commit -m "..."` par `gac` pour obtenir des messages de commit contextuels et bien formatés générés par des grands modèles de langage !

---

## Ce que vous obtenez

Des messages intelligents et contextuels qui expliquent le **pourquoi** derrière vos changements :

![GAC générant un message de commit contextuel](../../assets/gac-simple-usage.fr.png)

---

</div>

<!-- markdownlint-enable MD033 MD036 -->

## Démarrage rapide

### Utiliser gac sans l'installer

```bash
uvx gac init   # Configurez votre fournisseur, votre modèle et votre langue
uvx gac  # Générez et commitez avec l'IA
```

C'est tout ! Vérifiez le message généré et confirmez avec `y`.

### Installer et utiliser gac

```bash
uv tool install gac
gac init
gac
```

### Mettre à niveau gac installé

```bash
uv tool upgrade gac
```

---

## Fonctionnalités principales

### 🌐 **Plus de 25 Fournisseurs pris en charge**

- **Anthropic** • **Azure OpenAI** • **Cerebras** • **ChatGPT (OAuth)** • **Chutes.ai**
- **Claude Code (OAuth)** • **DeepSeek** • **Fireworks** • **Gemini** • **GitHub Copilot**
- **Groq** • **Kimi for Coding** • **LM Studio** • **MiniMax.io** • **Mistral AI** • **Moonshot AI**
- **Ollama** • **OpenAI** • **OpenRouter** • **Qwen Cloud (CN & INTL)** • **Replicate**
- **Streamlake/Vanchin** • **Synthetic.new** • **Together AI** • **Wafer.ai**
- **Z.AI** • **Z.AI Coding** • **Custom Endpoints (Anthropic/OpenAI)**

### 🧠 **Analyse intelligente par l'IA**

- **Comprend l'intention** : Analyse la structure, la logique et les motifs du code pour comprendre le "pourquoi" derrière vos changements, pas seulement ce qui a changé
- **Conscience sémantique** : Reconnaît les refactorisations, corrections de bugs, fonctionnalités et changements cassants pour générer des messages contextuellement appropriés
- **Filtrage intelligent** : Donne la priorité aux changements significatifs tout en ignorant les fichiers générés, dépendances et artefacts
- **Regroupement intelligent des commits** - Regroupe automatiquement les changements connexes en plusieurs commits logiques avec `--group`

### 📝 **Formats de messages multiples**

- **Une ligne** (-o) : Message de commit sur une seule ligne suivant le format de commit conventionnel
- **Standard** (par défaut) : Résumé avec points expliquant les détails d'implémentation
- **Détaillé** (-v) : Explications complètes incluant motivation, approche technique et analyse d'impact
- **Règle 50/72** (drapeau --50-72) : Applique le format classique de message de commit pour une lisibilité optimale dans git log et l'interface GitHub
- **DCO/Signoff** (drapeau --signoff) : Ajoute la ligne Signed-off-by pour la conformité au Developer Certificate of Origin (requis par Cherry Studio, le noyau Linux et autres projets)

### 🌍 **Support multilingue**

- **25+ langues** : Générez des messages de commit en anglais, chinois, japonais, coréen, espagnol, français, allemand et 20+ autres langues
- **Traduction flexible** : Choisissez de conserver les préfixes de commits conventionnels en anglais pour la compatibilité des outils, ou traduisez-les entièrement
- **Workflows multiples** : Définissez une langue par défaut avec `gac language`, ou utilisez le drapeau `-l <langue>` pour des remplacements ponctuels
- **Support des scripts natifs** : Support complet des scripts non latins incluant CJK, cyrillique, thaï et plus

### 💻 **Expérience développeur**

- **Feedback interactif** : Tapez `r` pour relancer, `e` pour éditer (TUI intégrée par défaut, ou `$GAC_EDITOR` si défini), ou tapez directement votre feedback comme "rends-le plus court" ou "concentre-toi sur la correction du bug"
- **Interrogation interactive** : Utilisez `--interactive` (`-i`) pour répondre à des questions ciblées sur vos changements pour des messages de commit plus contextuels
- **Workflows en une commande** : Workflows complets avec des drapeaux comme `gac -ayp` (indexer tout, confirmer automatiquement, pousser)
- **Intégration Git** : Respecte les hooks pre-commit et lefthook, en les exécutant avant les opérations coûteuses de l'IA
- **Serveur MCP** : Exécutez `gac serve` pour exposer les outils de commit aux agents IA via le [Model Context Protocol](https://modelcontextprotocol.io/)

### 📊 **Statistiques d'utilisation**

- **Suivez vos gacs** : Voyez combien de commits vous avez faits avec gac, votre série actuelle, pics d'activité quotidienne/hebdomadaire et projets principaux
- **Suivi des tokens** : Total des tokens de prompt et de completion par jour, semaine, projet et modèle — avec des trophées de record pour l'utilisation des tokens aussi
- **Modèles principaux** : Voyez quels modèles vous utilisez le plus et combien de tokens chacun consomme
- **Statistiques par projet** : Consultez les statistiques du dépôt actuel avec `gac stats project`
- **Célébrations de records** : 🏆 trophées quand vous établissez de nouveaux records quotidiens, hebdomadaires, de tokens ou de série ; 🥈 pour les égaler
- **Opt-in lors de la configuration** : `gac init` vous demande si vous souhaitez activer les statistiques et explique exactement ce qui est stocké
- **Opt-out à tout moment** : Définissez `GAC_DISABLE_STATS=true` (ou `1`/`yes`/`on`) pour désactiver. Le définir à `false`/`0`/`no` (ou le laisser non défini) garde les statistiques activées
- **Confidentialité d'abord** : Stocké localement dans `~/.gac_stats.json`. Seulement les compteurs, dates, noms de projets et noms de modèles — pas de messages de commit, de code ni de données personnelles. Pas de télémétrie

### 🛡️ **Sécurité intégrée**

- **Détection automatique de secrets** : Analyse les clés API, mots de passe et jetons avant le commit
- **Protection interactive** : Demande confirmation avant de commiter des données potentiellement sensibles avec des options de remédiation claires
- **Filtrage intelligent** : Ignore les fichiers d'exemple, fichiers de modèle et texte de remplacement pour réduire les faux positifs

---

## Exemples d'utilisation

### Workflow de base

```bash
# Indexez vos changements
git add .

# Générez et commitez avec l'IA
gac

# Vérifiez → y (commit) | n (annuler) | r (relancer) | e (éditer) | ou tapez votre feedback
```

### Commandes courantes

| Commande          | Description                                                             |
| ----------------- | ----------------------------------------------------------------------- |
| `gac`             | Générer un message de commit                                            |
| `gac -y`          | Confirmer automatiquement (pas de vérification nécessaire)              |
| `gac -a`          | Indexer tout avant de générer le message de commit                      |
| `gac -o`          | Message sur une ligne pour les changements triviaux                     |
| `gac -v`          | Format détaillé avec Motivation, Approche technique et Analyse d'impact |
| `gac -h "indice"` | Ajouter du contexte pour l'IA (ex: `gac -h "correction de bug"`)        |
| `gac -s`          | Inclure une portée (ex: feat(auth):)                                    |
| `gac -i`          | Poser des questions sur les changements pour un meilleur contexte       |
| `gac -g`          | Grouper les changements en plusieurs commits logiques                   |
| `gac -p`          | Commiter et pousser                                                     |
| `gac stats`       | Consultez vos statistiques d'utilisation de gac                         |

### Exemples pour utilisateurs avancés

```bash
# Workflow complet en une commande
# Consultez vos statistiques de commits
gac stats

# Statistiques du projet actuel uniquement
gac stats project

gac -ayp -h "préparation de release"

# Explication détaillée avec portée
gac -v -s

# Message rapide sur une ligne pour petits changements
gac -o

# Grouper les changements en commits logiquement liés
gac -ag

# Mode interactif avec sortie détaillée pour des explications détaillées
gac -iv

# Déboguer ce que voit l'IA
gac --show-prompt

# Ignorer l'analyse de sécurité (utiliser avec prudence)
gac --skip-secret-scan

# Ajouter signoff pour conformité DCO (Cherry Studio, noyau Linux, etc.)
gac --signoff
```

### Système de feedback interactif

Pas satisfait du résultat ? Vous avez plusieurs options :

```bash
# Relancer simple (pas de feedback)
r

# Éditer le message de commit
e
# Par défaut : TUI intégrée avec bindings vi/emacs
# Appuyez sur Esc+Entrée ou Ctrl+S pour soumettre, Ctrl+C pour annuler

# Définissez GAC_EDITOR pour ouvrir votre éditeur préféré à la place :
# GAC_EDITOR=code gac → ouvre VS Code (--wait appliqué automatiquement)
# GAC_EDITOR=vim gac → ouvre vim
# GAC_EDITOR=nano gac → ouvre nano

# Ou tapez simplement votre feedback directement !
rends-le plus court et concentre-toi sur l'amélioration des performances
utilise le format de commit conventionnel avec portée
explique les implications de sécurité

# Appuyez sur Entrée sur une entrée vide pour voir l'invite à nouveau
```

La fonction d'édition (`e`) vous permet d'affiner le message de commit :

- **Par défaut (TUI intégrée)** : Édition multi-lignes avec bindings vi/emacs — corriger les fautes de frappe, ajuster la formulation, restructurer
- **Avec `GAC_EDITOR`** : Ouvre votre éditeur préféré (`code`, `vim`, `nano`, etc.) — toute la puissance de l'éditeur, y compris rechercher/remplacer, macros, etc.

Les éditeurs GUI comme VS Code sont gérés automatiquement : gac insère `--wait` pour que le processus se bloque jusqu'à la fermeture de l'onglet de l'éditeur. Aucune configuration supplémentaire nécessaire.

---

## Configuration

Exécutez `gac init` pour configurer votre fournisseur de manière interactive, ou définissez les variables d'environnement :

Besoin de changer de fournisseurs ou de modèles plus tard sans toucher aux paramètres de langue ? Utilisez `gac model` pour un flux simplifié qui saute les questions de langue.

```bash
# Exemple de configuration
GAC_MODEL=anthropic:your-model-name
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

Voir `.gac.env.example` pour toutes les options disponibles.

**Vous voulez des messages de commit dans une autre langue ?** Exécutez `gac language` pour sélectionner parmi 25+ langues incluant Español, Français, 日本語 et plus.

**Vous voulez personnaliser le style des messages de commit ?** Voir [docs/CUSTOM_SYSTEM_PROMPTS.md](docs/fr/CUSTOM_SYSTEM_PROMPTS.md) pour des conseils sur la récitation de prompts système personnalisés.

---

## Obtenir de l'aide

- **Documentation complète** : [USAGE.md](docs/fr/USAGE.md) - Référence CLI complète
- **Serveur MCP** : [docs/MCP.md](MCP.md) - Utiliser GAC comme serveur MCP pour les agents IA
- **Claude Code OAuth** : [docs/CLAUDE_CODE.md](docs/fr/CLAUDE_CODE.md) - Configuration et authentification de Claude Code
- **ChatGPT OAuth** : [docs/CHATGPT_OAUTH.md](docs/fr/CHATGPT_OAUTH.md) - Configuration et authentification de ChatGPT OAuth
- **Prompts personnalisés** : [CUSTOM_SYSTEM_PROMPTS.md](docs/fr/CUSTOM_SYSTEM_PROMPTS.md) - Personnaliser le style des messages de commit
- **Statistiques d'utilisation** : Voir `gac stats --help` ou la [documentation complète](docs/fr/USAGE.md#statistiques-dutilisation)
- **Dépannage** : [TROUBLESHOOTING.md](docs/fr/TROUBLESHOOTING.md) - Problèmes courants et solutions
- **Contribuer** : [CONTRIBUTING.md](docs/fr/CONTRIBUTING.md) - Configuration de développement et lignes directrices

---

<!-- markdownlint-disable MD033 MD036 -->

<div align="center">

[⭐ Mettez-nous une étoile sur GitHub](https://github.com/cellwebb/gac) • [🐛 Signaler des problèmes](https://github.com/cellwebb/gac/issues) • [📖 Documentation complète](docs/fr/USAGE.md)

</div>

<!-- markdownlint-enable MD033 MD036 -->
