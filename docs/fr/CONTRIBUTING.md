# Contribuer à gac

[English](../en/CONTRIBUTING.md) | [简体中文](../zh-CN/CONTRIBUTING.md) | [繁體中文](../zh-TW/CONTRIBUTING.md) | [日本語](../ja/CONTRIBUTING.md) | [한국어](../ko/CONTRIBUTING.md) | [हिन्दी](../hi/CONTRIBUTING.md) | [Tiếng Việt](../vi/CONTRIBUTING.md) | **Français** | [Русский](../ru/CONTRIBUTING.md) | [Español](../es/CONTRIBUTING.md) | [Português](../pt/CONTRIBUTING.md) | [Norsk](../no/CONTRIBUTING.md) | [Svenska](../sv/CONTRIBUTING.md) | [Deutsch](../de/CONTRIBUTING.md) | [Nederlands](../nl/CONTRIBUTING.md) | [Italiano](../it/CONTRIBUTING.md)

Merci de votre intérêt à contribuer à ce projet ! Votre aide est appréciée. Veuillez suivre ces directives pour faciliter le processus pour tout le monde.

## Table des matières

- [Contribuer à gac](#contribuer-à-gac)
  - [Table des matières](#table-des-matières)
  - [Configuration de l'environnement de développement](#configuration-de-lenvironnement-de-développement)
    - [Configuration rapide](#configuration-rapide)
    - [Configuration alternative (si vous préférez étape par étape)](#configuration-alternative-si-vous-préférez-étape-par-étape)
    - [Commandes disponibles](#commandes-disponibles)
  - [Augmentation de version](#augmentation-de-version)
    - [Comment augmenter la version](#comment-augmenter-la-version)
    - [Processus de release](#processus-de-release)
    - [Utilisation de bump-my-version (optionnel)](#utilisation-de-bump-my-version-optionnel)
  - [Ajouter un nouveau fournisseur d'IA](#ajouter-un-nouveau-fournisseur-dia)
    - [Checklist pour ajouter un nouveau fournisseur](#checklist-pour-ajouter-un-nouveau-fournisseur)
    - [Exemple d'implémentation](#exemple-dimplémentation)
    - [Points clés](#points-clés)
  - [Standards de codage](#standards-de-codage)
  - [Hooks Git (Lefthook)](#hooks-git-lefthook)
    - [Configuration](#configuration)
    - [Sauter les hooks Git](#sauter-les-hooks-git)
  - [Directives de test](#directives-de-test)
    - [Exécution des tests](#exécution-des-tests)
      - [Tests d'intégration de fournisseurs](#tests-dintégration-de-fournisseurs)
  - [Code de conduite](#code-de-conduite)
  - [Licence](#licence)
  - [Où obtenir de l'aide](#où-obtenir-de-laide)

## Configuration de l'environnement de développement

Ce projet utilise `uv` pour la gestion des dépendances et fournit un Makefile pour les tâches de développement courantes :

### Configuration rapide

```bash
# Une commande pour tout configurer incluant les hooks Lefthook
make dev
```

Cette commande va :

- Installer les dépendances de développement
- Installer les hooks git
- Exécuter les hooks Lefthook sur tous les fichiers pour corriger les problèmes existants

### Configuration alternative (si vous préférez étape par étape)

```bash
# Créer un environnement virtuel et installer les dépendances
make setup

# Installer les dépendances de développement
make dev

# Installer les hooks Lefthook
brew install lefthook  # ou voir la documentation ci-dessous pour alternatives
lefthook install
lefthook run pre-commit --all
```

### Commandes disponibles

- `make setup` - Créer un environnement virtuel et installer toutes les dépendances
- `make dev` - **Configuration de développement complète** - inclut les hooks Lefthook
- `make test` - Exécuter les tests standards (exclut les tests d'intégration)
- `make test-integration` - Exécuter uniquement les tests d'intégration (nécessite des clés API)
- `make test-all` - Exécuter tous les tests
- `make test-cov` - Exécuter les tests avec rapport de couverture
- `make lint` - Vérifier la qualité du code (ruff, prettier, markdownlint)
- `make format` - Corriger automatiquement les problèmes de formatage de code

## Augmentation de version

**Important** : Les PRs doivent inclure une augmentation de version dans `src/gac/__version__.py` lorsqu'elles contiennent des changements qui devraient être publiés.

### Comment augmenter la version

1. Éditez `src/gac/__version__.py` et incrémentez le numéro de version
2. Suivez le [Versionnement Sémantique](https://semver.org/) :
   - **Patch** (1.6.X) : Corrections de bugs, petites améliorations
   - **Mineur** (1.X.0) : Nouvelles fonctionnalités, changements rétrocompatibles (ex: ajouter un nouveau fournisseur)
   - **Majeur** (X.0.0) : Changements cassants

### Processus de release

Les releases sont déclenchées par le push de tags de version :

1. Fusionnez les PR(s) avec augmentations de version vers main
2. Créez un tag : `git tag v1.6.1`
3. Poussez le tag : `git push origin v1.6.1`
4. GitHub Actions publie automatiquement sur PyPI

Exemple :

```python
# src/gac/__version__.py
__version__ = "1.6.1"  # Augmenté de 1.6.0
```

### Utilisation de bump-my-version (optionnel)

Si vous avez `bump-my-version` installé, vous pouvez l'utiliser localement :

```bash
# Pour les corrections de bugs :
bump-my-version bump patch

# Pour les nouvelles fonctionnalités :
bump-my-version bump minor

# Pour les changements cassants :
bump-my-version bump major
```

## Ajouter un nouveau fournisseur d'IA

Lors de l'ajout d'un nouveau fournisseur d'IA, vous devez mettre à jour plusieurs fichiers dans la base de code. Suivez cette checklist complète :

### Checklist pour ajouter un nouveau fournisseur

- [ ] **1. Créer l'implémentation du fournisseur** (`src/gac/providers/<provider_name>.py`)

  - Créez un nouveau fichier nommé d'après le fournisseur (ex: `minimax.py`)
  - Implémentez `call_<provider>_api(model: str, messages: list[dict], temperature: float, max_tokens: int) -> str`
  - Utilisez le format compatible OpenAI si le fournisseur le supporte
  - Gérez la clé API à partir de la variable d'environnement `<PROVIDER>_API_KEY`
  - Incluez un gestionnaire d'erreurs approprié avec les types `AIError` :
    - `AIError.authentication_error()` pour les problèmes d'auth
    - `AIError.rate_limit_error()` pour les limites de taux (HTTP 429)
    - `AIError.timeout_error()` pour les timeouts
    - `AIError.model_error()` pour les erreurs de modèle et contenu vide/null
  - Définissez l'URL du point de terminaison API
  - Utilisez un timeout de 120 secondes pour les requêtes HTTP

- [ ] **2. Enregistrer le fournisseur dans le paquet** (`src/gac/providers/__init__.py`)

  - Ajoutez l'import : `from .<provider> import call_<provider>_api`
  - Ajoutez au dictionnaire `PROVIDER_REGISTRY` : `"provider-name": call_<provider>_api`
  - Ajoutez à la liste `__all__` : `"call_<provider>_api"`

- [ ] **3. Mettre à jour la configuration d'exemple** (`.gac.env.example`)

  - Ajoutez une configuration de modèle d'exemple au format : `# GAC_MODEL=provider:model-name`
  - Ajoutez une entrée de clé API : `# <PROVIDER>_API_KEY=your_key_here`
  - Gardez les entrées triées alphabétiquement
  - Ajoutez des commentaires pour les clés optionnelles si applicable

- [ ] **4. Mettre à jour la documentation** (`README.md` et toutes les traductions de `README.md` dans `docs/`)

  - Ajoutez le nom du fournisseur à la section "Supported Providers" dans toutes les traductions de README
  - Gardez la liste triée alphabétiquement dans ses puces

- [ ] **5. Ajouter à la configuration interactive** (`src/gac/init_cli.py`)

  - Ajoutez un tuple à la liste `providers` : `("Provider Name", "default-model-name")`
  - Gardez la liste triée alphabétiquement
  - **Important** : Si votre fournisseur utilise un nom de clé API non standard (pas le `{PROVIDER_UPPERCASE}_API_KEY` généré automatiquement), ajoutez un traitement spécial :

    ```python
    elif provider_key == "your-provider-key":
        api_key_name = "YOUR_CUSTOM_API_KEY_NAME"
    ```

    Exemples : `kimi-for-coding` utilise `KIMI_CODING_API_KEY`, `moonshot-ai` utilise `MOONSHOT_API_KEY`

- [ ] **6. Créer des tests complets** (`tests/providers/test_<provider>.py`)

  - Créez un fichier de test suivant la convention de nommage
  - Incluez ces classes de test :
    - `Test<Provider>Imports` - Tester les imports de module et fonction
    - `Test<Provider>APIKeyValidation` - Tester l'erreur de clé API manquante
    - `Test<Provider>ProviderMocked(BaseProviderTest)` - Hériter de `BaseProviderTest` pour 9 tests standards
    - `Test<Provider>EdgeCases` - Tester le contenu null et autres cas limites
    - `Test<Provider>Integration` - Tests d'appels API réels (marqués avec `@pytest.mark.integration`)
  - Implémentez les propriétés requises dans la classe de test mockée :
    - `provider_name` - Nom du fournisseur (minuscule)
    - `provider_module` - Chemin complet du module
    - `api_function` - La référence de fonction API
    - `api_key_env_var` - Nom de variable d'environnement pour la clé API (ou None pour les fournisseurs locaux)
    - `model_name` - Nom de modèle par défaut pour les tests
    - `success_response` - Réponse API réussie mockée
    - `empty_content_response` - Réponse de contenu vide mockée

- [ ] **7. Augmenter la version** (`src/gac/__version__.py`)
  - Incrémentez la version **mineure** (ex: 1.10.2 → 1.11.0)
  - Ajouter un fournisseur est une nouvelle fonctionnalité et nécessite une augmentation de version mineure

### Exemple d'implémentation

Voyez l'implémentation du fournisseur MiniMax comme référence :

- Fournisseur : `src/gac/providers/minimax.py`
- Tests : `tests/providers/test_minimax.py`

### Points clés

1. **Gestion des erreurs** : Utilisez toujours le type `AIError` approprié pour différents scénarios d'erreur
2. **Contenu null/vide** : Vérifiez toujours pour le contenu `None` et chaîne vide dans les réponses
3. **Tests** : La classe `BaseProviderTest` fournit 9 tests standards que chaque fournisseur devrait hériter
4. **Ordre alphabétique** : Gardez les listes de fournisseurs triées alphabétiquement pour la maintenabilité
5. **Nom des clés API** : Utilisez le format `<PROVIDER>_API_KEY` (tout majuscule, underscores pour les espaces)
6. **Enregistrement du fournisseur** : Ne modifier que `src/gac/providers/__init__.py` et `src/gac/init_cli.py` – `ai.py` et `ai_utils.py` lisent automatiquement à partir du registre
7. **Format de nom de fournisseur** : Utilisez minuscules avec traits d'union pour les noms multi-mots (ex: "lm-studio")
8. **Augmentation de version** : Ajouter un fournisseur nécessite une augmentation de version **mineure** (nouvelle fonctionnalité)

## Standards de codage

- Cible Python 3.10+ (3.10, 3.11, 3.12, 3.13, 3.14)
- Utilisez des annotations de type pour tous les paramètres de fonction et valeurs de retour
- Gardez le code propre, compact et lisible
- Évitez la complexité inutile
- Utilisez le logging au lieu des instructions print
- Le formatage est géré par `ruff` (linting, formatage et tri d'imports en un seul outil ; longueur de ligne max : 120)
- Écrivez des tests minimaux et efficaces avec `pytest`

## Hooks Git (Lefthook)

Ce projet utilise [Lefthook](https://github.com/evilmartians/lefthook) pour garder les vérifications de qualité de code rapides et cohérentes. Les hooks configurés miroitent notre configuration pre-commit précédente :

- `ruff` - Linting et formatage Python (remplace black, isort et flake8)
- `markdownlint-cli2` - Linting Markdown
- `prettier` - Formatage de fichiers (markdown, yaml, json)
- `check-upstream` - Hook personnalisé pour vérifier les changements en amont

### Configuration

**Approche recommandée :**

```bash
make dev
```

**Configuration manuelle (si vous préférez étape par étape) :**

1. Installez Lefthook (choisissez l'option qui correspond à votre configuration) :

   ```sh
   brew install lefthook          # macOS (Homebrew)
   # ou
   cargo install lefthook         # Rust toolchain
   # ou
   asdf plugin add lefthook && asdf install lefthook latest
   ```

2. Installez les hooks git :

   ```sh
   lefthook install
   ```

3. (Optionnel) Exécutez sur tous les fichiers :

   ```sh
   lefthook run pre-commit --all
   ```

Les hooks s'exécuteront maintenant automatiquement à chaque commit. Si des vérifications échouent, vous devrez corriger les problèmes avant de pouvoir commiter.

### Sauter les hooks Git

Si vous devez sauter temporairement les vérifications Lefthook, utilisez le drapeau `--no-verify` :

```sh
git commit --no-verify -m "Your commit message"
```

Note : Ceci ne devrait être utilisé qu'en cas de nécessité absolue, car il contourne des vérifications importantes de qualité de code.

## Directives de test

Le projet utilise pytest pour les tests. Lors de l'ajout de nouvelles fonctionnalités ou de la correction de bugs, veuillez inclure des tests qui couvrent vos changements.

Notez que le répertoire `scripts/` contient des scripts de test pour les fonctionnalités qui ne peuvent pas être facilement testées avec pytest.
N'hésitez pas à ajouter des scripts ici pour tester des scénarios complexes ou des tests d'intégration qui seraient difficiles à implémenter
en utilisant le framework pytest standard.

### Exécution des tests

```sh
# Exécuter les tests standards (exclut les tests d'intégration avec appels API réels)
make test

# Exécuter uniquement les tests d'intégration de fournisseurs (nécessite des clés API)
make test-integration

# Exécuter tous les tests incluant les tests d'intégration de fournisseurs
make test-all

# Exécuter les tests avec couverture
make test-cov

# Exécuter un fichier de test spécifique
uv run -- pytest tests/test_prompt.py

# Exécuter un test spécifique
uv run -- pytest tests/test_prompt.py::TestExtractRepositoryContext::test_extract_repository_context_with_docstring
```

#### Tests d'intégration de fournisseurs

Les tests d'intégration de fournisseurs font des appels API réels pour vérifier que les implémentations de fournisseurs fonctionnent correctement avec les API réelles. Ces tests sont marqués avec `@pytest.mark.integration` et sont sautés par défaut pour :

- Éviter de consommer des crédits API pendant le développement régulier
- Empêcher les échecs de test lorsque les clés API ne sont pas configurées
- Garder l'exécution des tests rapide pour une itération rapide

Pour exécuter les tests d'intégration de fournisseurs :

1. **Configurez les clés API** pour les fournisseurs que vous voulez tester :

   ```sh
   export ANTHROPIC_API_KEY="your-key"
   export CEREBRAS_API_KEY="your-key"
   export GEMINI_API_KEY="your-key"
   export GROQ_API_KEY="your-key"
   export OPENAI_API_KEY="your-key"
   export OPENROUTER_API_KEY="your-key"
   export STREAMLAKE_API_KEY="your-key"
   export ZAI_API_KEY="your-key"
   # LM Studio et Ollama nécessitent une instance locale en cours d'exécution
   # Les clés API pour LM Studio et Ollama sont optionnelles sauf si votre déploiement applique l'authentification
   ```

2. **Exécutez les tests de fournisseurs** :

   ```sh
   make test-integration
   ```

Les tests sauteront les fournisseurs où les clés API ne sont pas configurées. Ces tests aident à détecter les changements d'API tôt et assurent la compatibilité avec les API des fournisseurs.

## Code de conduite

Soyez respectueux et constructif. Le harcèlement ou le comportement abusif ne sera pas toléré.

## Licence

En contribuant, vous acceptez que vos contributions seront licenciées sous la même licence que le projet.

---

## Où obtenir de l'aide

- Pour le dépannage, voir [../TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- Pour l'utilisation et les options CLI, voir [../USAGE.md](../USAGE.md)
- Pour les détails de licence, voir [../LICENSE](../LICENSE)

Merci d'aider à améliorer gac !
