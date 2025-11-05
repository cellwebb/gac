# Utilisation en ligne de commande de gac

[English](../en/USAGE.md) | [简体中文](../zh-CN/USAGE.md) | [繁體中文](../zh-TW/USAGE.md) | [日本語](../ja/USAGE.md) | [한국어](../ko/USAGE.md) | [हिन्दी](../hi/USAGE.md) | [Tiếng Việt](../vi/USAGE.md) | **Français** | [Рус../](../ru/USAGE.md) | [Español](../es/USAGE.md) | [Português](../pt/USAGE.md) | [Norsk](../no/USAGE.md) | [Svenska](../sv/USAGE.md) | [Deutsch](../de/USAGE.md) | [Nederlands](../nl/USAGE.md) | [Italiano](../it/USAGE.md)

Ce document décrit tous les drapeaux et options disponibles pour l'outil CLI `gac`.

## Table des matières

- [Utilisation en ligne de commande de gac](#utilisation-en-ligne-de-commande-de-gac)
  - [Table des matières](#table-des-matières)
  - [Utilisation de base](#utilisation-de-base)
  - [Drapeaux de workflow principaux](#drapeaux-de-workflow-principaux)
  - [Personnalisation des messages](#personnalisation-des-messages)
  - [Sortie et verbosité](#sortie-et-verbosité)
  - [Aide et version](#aide-et-version)
  - [Exemples de workflows](#exemples-de-workflows)
  - [Avancé](#avancé)
    - [Sauter les hooks Pre-commit et Lefthook](#sauter-les-hooks-pre-commit-et-lefthook)
  - [Notes de configuration](#notes-de-configuration)
    - [Options de configuration avancées](#options-de-configuration-avancées)
    - [Sous-commandes de configuration](#sous-commandes-de-configuration)
  - [Obtenir de l'aide](#obtenir-de-laide)

## Utilisation de base

```sh
gac init
# Suivez ensuite les invites pour configurer votre fournisseur, modèle et clés API de manière interactive
gac
```

Génère un message de commit alimenté par l'IA pour les changements indexés et demande confirmation. L'invite de confirmation accepte :

- `y` ou `yes` - Procéder au commit
- `n` ou `no` - Annuler le commit
- `r` ou `reroll` - Régénérer le message de commit avec le même contexte
- `e` ou `edit` - Éditer le message de commit sur place avec édition de terminal riche (bindings vi/emacs)
- Tout autre texte - Régénérer avec ce texte comme feedback (ex: "rends-le plus court", "concentre-toi sur les performances")
- Entrée vide (juste Entrée) - Afficher l'invite à nouveau

---

## Drapeaux de workflow principaux

| Drapeau / Option     | Court | Description                                                                |
| -------------------- | ----- | -------------------------------------------------------------------------- |
| `--add-all`          | `-a`  | Indexer tous les changements avant le commit                               |
| `--group`            | `-g`  | Grouper les changements indexés en multiples commits logiques              |
| `--push`             | `-p`  | Pousser les changements vers le distant après le commit                    |
| `--yes`              | `-y`  | Confirmer automatiquement le commit sans demande                           |
| `--dry-run`          |       | Montrer ce qui se passerait sans faire de changements                      |
| `--no-verify`        |       | Sauter les hooks pre-commit et lefthook lors du commit                     |
| `--skip-secret-scan` |       | Sauter l'analyse de sécurité pour les secrets dans les changements indexés |

**Note :** Combinez `-a` et `-g` (c'est-à-dire `-ag`) pour indexer TOUS les changements d'abord, puis les grouper en commits.

**Note :** Lors de l'utilisation de `--group`, la limite de tokens de sortie maximale est automatiquement mise à l'échelle en fonction du nombre de fichiers commités (2x pour 1-9 fichiers, 3x pour 10-19 fichiers, 4x pour 20-29 fichiers, 5x pour 30+ fichiers). Cela assure que l'IA a assez de tokens pour générer tous les commits groupés sans troncation, même pour les ensembles de changements volumineux.

## Personnalisation des messages

| Drapeau / Option    | Court | Description                                                                      |
| ------------------- | ----- | -------------------------------------------------------------------------------- |
| `--one-liner`       | `-o`  | Générer un message de commit sur une seule ligne                                 |
| `--verbose`         | `-v`  | Générer des messages de commit détaillés avec motivation, architecture et impact |
| `--hint <text>`     | `-h`  | Ajouter un indice pour guider l'IA                                               |
| `--model <model>`   | `-m`  | Spécifier le modèle à utiliser pour ce commit                                    |
| `--language <lang>` | `-l`  | Remplacer la langue (nom ou code : 'Spanish', 'es', 'zh-CN', 'ja')               |
| `--scope`           | `-s`  | Inférer une portée appropriée pour le commit                                     |

**Note :** Vous pouvez fournir un feedback de manière interactive en le tapant simplement à l'invite de confirmation - pas besoin de préfixer avec 'r'. Tapez `r` pour une relance simple, `e` pour éditer sur place avec les bindings vi/emacs, ou tapez votre feedback directement comme "rends-le plus court".

## Sortie et verbosité

| Drapeau / Option      | Court | Description                                                                |
| --------------------- | ----- | -------------------------------------------------------------------------- |
| `--quiet`             | `-q`  | Supprimer toute sortie sauf les erreurs                                    |
| `--log-level <level>` |       | Définir le niveau de log (debug, info, warning, error)                     |
| `--show-prompt`       |       | Afficher le prompt de l'IA utilisé pour la génération de message de commit |

## Aide et version

| Drapeau / Option | Court | Description                           |
| ---------------- | ----- | ------------------------------------- |
| `--version`      |       | Afficher la version de gac et quitter |
| `--help`         |       | Afficher le message d'aide et quitter |

---

## Exemples de workflows

- **Indexer tous les changements et commiter :**

  ```sh
  gac -a
  ```

- **Commiter et pousser en une étape :**

  ```sh
  gac -ap
  ```

- **Générer un message de commit sur une seule ligne :**

  ```sh
  gac -o
  ```

- **Générer un message de commit détaillé avec sections structurées :**

  ```sh
  gac -v
  ```

- **Ajouter un indice pour l'IA :**

  ```sh
  gac -h "Refactoriser la logique d'authentification"
  ```

- **Inférer la portée pour le commit :**

  ```sh
  gac -s
  ```

- **Grouper les changements indexés en commits logiques :**

  ```sh
  gac -g
  # Groupe uniquement les fichiers que vous avez déjà indexés
  ```

- **Grouper tous les changements (indexés + non indexés) et confirmer automatiquement :**

  ```sh
  gac -agy
  # Indexe tout, le groupe, et confirme automatiquement
  ```

- **Utiliser un modèle spécifique juste pour ce commit :**

  ```sh
  gac -m anthropic:claude-haiku-4-5
  ```

- **Générer un message de commit dans une langue spécifique :**

  ```sh
  # Utilisant les codes de langue (plus court)
  gac -l zh-CN
  gac -l ja
  gac -l es

  # Utilisant les noms complets
  gac -l "Simplified Chinese"
  gac -l Japanese
  gac -l Spanish
  ```

- **Test à blanc (voir ce qui se passerait) :**

  ```sh
  gac --dry-run
  ```

## Avancé

- Combinez les drapeaux pour des workflows plus puissants (ex: `gac -ayp` pour indexer, confirmer automatiquement et pousser)
- Utilisez `--show-prompt` pour déboguer ou revoir le prompt envoyé à l'IA
- Ajustez la verbosité avec `--log-level` ou `--quiet`

### Sauter les hooks Pre-commit et Lefthook

Le drapeau `--no-verify` vous permet de sauter tous les hooks pre-commit ou lefthook configurés dans votre projet :

```sh
gac --no-verify  # Sauter tous les hooks pre-commit et lefthook
```

**Utilisez `--no-verify` lorsque :**

- Les hooks pre-commit ou lefthook échouent temporairement
- Vous travaillez avec des hooks chronophages
- Vous commitez du code en cours de travail qui ne passe pas encore toutes les vérifications

**Note :** Utilisez avec prudence car ces hooks maintiennent les standards de qualité du code.

### Analyse de sécurité

gac inclut une analyse de sécurité intégrée qui détecte automatiquement les secrets potentiels et clés API dans vos changements indexés avant le commit. Cela aide à prévenir le commit accidentel d'informations sensibles.

**Sauter les analyses de sécurité :**

```sh
gac --skip-secret-scan  # Sauter l'analyse de sécurité pour ce commit
```

**Pour désactiver de manière permanente :** Définissez `GAC_SKIP_SECRET_SCAN=true` dans votre fichier `.gac.env`.

**Quand sauter :**

- Commiter du code d'exemple avec des clés de remplacement
- Travailler avec des fixtures de test qui contiennent des identifiants factices
- Lorsque vous avez vérifié que les changements sont sûrs

**Note :** L'analyseur utilise des motifs pour détecter les formats de secrets courants. Revoyez toujours vos changements indexés avant de commiter.

## Notes de configuration

- La méthode recommandée pour configurer gac est d'exécuter `gac init` et de suivre les invites interactives.
- Vous avez déjà configuré la langue et devez juste changer de fournisseurs ou de modèles ? Exécutez `gac model` pour répéter la configuration sans questions de langue.
- gac charge la configuration dans l'ordre de priorité suivant :
  1. Drapeaux CLI
  2. Variables d'environnement
  3. `.gac.env` au niveau projet
  4. `~/.gac.env` au niveau utilisateur

### Options de configuration avancées

Vous pouvez personnaliser le comportement de gac avec ces variables d'environnement optionnelles :

- `GAC_ALWAYS_INCLUDE_SCOPE=true` - Inférer et inclure automatiquement la portée dans les messages de commit (ex: `feat(auth):` vs `feat:`)
- `GAC_VERBOSE=true` - Générer des messages de commit détaillés avec sections motivation, architecture et impact
- `GAC_TEMPERATURE=0.7` - Contrôler la créativité de l'IA (0.0-1.0, plus bas = plus focus)
- `GAC_MAX_OUTPUT_TOKENS=4096` - Tokens maximum pour les messages générés (automatiquement mis à l'échelle 2-5x lors de l'utilisation de `--group` basé sur le nombre de fichiers ; remplacer pour aller plus haut ou plus bas)
- `GAC_WARNING_LIMIT_TOKENS=4096` - Avertir quand les prompts dépassent ce nombre de tokens
- `GAC_SYSTEM_PROMPT_PATH=/path/to/custom_prompt.txt` - Utiliser un prompt système personnalisé pour la génération de messages de commit
- `GAC_LANGUAGE=Spanish` - Générer des messages de commit dans une langue spécifique (ex: Spanish, French, Japanese, German). Supporte les noms complets ou codes ISO (es, fr, ja, de, zh-CN). Utilisez `gac language` pour sélection interactive
- `GAC_TRANSLATE_PREFIXES=true` - Traduire les préfixes de commits conventionnels (feat, fix, etc.) dans la langue cible (par défaut : false, garde les préfixes en anglais)
- `GAC_SKIP_SECRET_SCAN=true` - Désactiver l'analyse de sécurité automatique pour les secrets dans les changements indexés (utiliser avec prudence)

Voir `.gac.env.example` pour un modèle de configuration complet.

Pour des conseils détaillés sur la création de prompts système personnalisés, voir [docs/CUSTOM_SYSTEM_PROMPTS.fr.md](../CUSTOM_SYSTEM_PROMPTS.fr.md).

### Sous-commandes de configuration

Les sous-commandes suivantes sont disponibles :

- `gac init` — Assistant de configuration interactif pour fournisseur, modèle et configuration de langue
- `gac model` — Configuration fournisseur/modèle/clé API sans invites de langue (idéal pour changements rapides)
- `gac config show` — Afficher la configuration actuelle
- `gac config set KEY VALUE` — Définir une clé de configuration dans `$HOME/.gac.env`
- `gac config get KEY` — Obtenir une valeur de configuration
- `gac config unset KEY` — Supprimer une clé de configuration de `$HOME/.gac.env`
- `gac language` (ou `gac lang`) — Sélecteur de langue interactif pour les messages de commit (définit GAC_LANGUAGE)
- `gac diff` — Afficher le git diff filtré avec options pour les changements indexés/non indexés, couleur et troncation

## Obtenir de l'aide

- Pour les prompts système personnalisés, voir [docs/CUSTOM_SYSTEM_PROMPTS.fr.md](../CUSTOM_SYSTEM_PROMPTS.fr.md)
- Pour le dépannage et conseils avancés, voir [docs/TROUBLESHOOTING.fr.md](../TROUBLESHOOTING.fr.md)
- Pour l'installation et la configuration, voir [README.md#installation-and-configuration](../README.md#installation-and-configuration)
- Pour contribuer, voir [docs/CONTRIBUTING.fr.md](../CONTRIBUTING.fr.md)
- Informations de licence : [LICENSE](../LICENSE)
