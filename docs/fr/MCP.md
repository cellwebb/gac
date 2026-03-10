# Utiliser GAC comme serveur MCP

[English](../en/MCP.md) | [简体中文](../zh-CN/MCP.md) | [繁體中文](../zh-TW/MCP.md) | [日本語](../ja/MCP.md) | [한국어](../ko/MCP.md) | [हिन्दी](../hi/MCP.md) | [Tiếng Việt](../vi/MCP.md) | **Français** | [Русский](../ru/MCP.md) | [Español](../es/MCP.md) | [Português](../pt/MCP.md) | [Norsk](../no/MCP.md) | [Svenska](../sv/MCP.md) | [Deutsch](../de/MCP.md) | [Nederlands](../nl/MCP.md) | [Italiano](../it/MCP.md)

GAC peut fonctionner comme un serveur du [Model Context Protocol (MCP)](https://modelcontextprotocol.io/), permettant aux agents IA et aux éditeurs de générer des commits via des appels d'outils structurés au lieu de commandes shell.

## Table des matières

- [Utiliser GAC comme serveur MCP](#utiliser-gac-comme-serveur-mcp)
  - [Table des matières](#table-des-matières)
  - [Qu'est-ce que MCP ?](#quest-ce-que-mcp-)
  - [Avantages](#avantages)
  - [Installation](#installation)
    - [Claude Code](#claude-code)
    - [Cursor](#cursor)
    - [Autres clients MCP](#autres-clients-mcp)
  - [Outils disponibles](#outils-disponibles)
    - [gac_status](#gac_status)
    - [gac_commit](#gac_commit)
  - [Flux de travail](#flux-de-travail)
    - [Commit basique](#commit-basique)
    - [Aperçu avant le commit](#aperçu-avant-le-commit)
    - [Commits groupés](#commits-groupés)
    - [Commit avec contexte](#commit-avec-contexte)
  - [Configuration](#configuration)
  - [Dépannage](#dépannage)
  - [Voir aussi](#voir-aussi)

## Qu'est-ce que MCP ?

Le Model Context Protocol est un standard ouvert qui permet aux applications d'IA d'appeler des outils externes via une interface structurée. En exécutant GAC comme serveur MCP, tout client compatible MCP peut inspecter l'état du dépôt et créer des commits alimentés par l'IA sans invoquer directement des commandes shell.

## Avantages

- **Interaction structurée** : Les agents appellent des outils typés avec des paramètres validés au lieu d'analyser la sortie du shell
- **Flux de travail à deux outils** : `gac_status` pour inspecter, `gac_commit` pour agir — un ajustement naturel pour le raisonnement des agents
- **Capacités complètes de GAC** : Messages de commit IA, commits groupés, analyse de secrets et push — tout disponible via MCP
- **Aucune configuration supplémentaire** : Le serveur utilise votre configuration GAC existante (`~/.gac.env`, paramètres de fournisseur, etc.)

## Installation

Le serveur MCP est démarré avec `gac serve` et communique via stdio, le transport standard MCP.

### Claude Code

Ajoutez au `.mcp.json` de votre projet ou au `~/.claude/claude_code_config.json` global :

```json
{
  "mcpServers": {
    "gac": {
      "command": "uvx",
      "args": ["gac", "serve"]
    }
  }
}
```

Ou si vous avez GAC installé globalement :

```json
{
  "mcpServers": {
    "gac": {
      "command": "gac",
      "args": ["serve"]
    }
  }
}
```

### Cursor

Ajoutez aux paramètres MCP de Cursor (`.cursor/mcp.json`) :

```json
{
  "mcpServers": {
    "gac": {
      "command": "uvx",
      "args": ["gac", "serve"]
    }
  }
}
```

### Autres clients MCP

Tout client compatible MCP peut utiliser GAC. Le point d'entrée du serveur est :

```text
command: uvx
args: ["gac", "serve"]
transport: stdio
```

Si vous avez GAC installé (via `uv tool install gac`), vous pouvez utiliser `gac` directement au lieu de `uvx gac`.

## Outils disponibles

Le serveur expose deux outils :

### gac_status

Inspecte l'état du dépôt. Utilisez-le avant de commiter pour comprendre ce qui sera commité.

**Paramètres :**

| Parameter           | Type                                    | Default     | Description                                       |
| ------------------- | --------------------------------------- | ----------- | ------------------------------------------------- |
| `format`            | `"summary"` \| `"detailed"` \| `"json"` | `"summary"` | Format de sortie                                  |
| `include_diff`      | bool                                    | `false`     | Inclure le contenu complet du diff                |
| `include_stats`     | bool                                    | `true`      | Inclure les statistiques de changements de lignes |
| `include_history`   | int                                     | `0`         | Nombre de commits récents à inclure               |
| `staged_only`       | bool                                    | `false`     | Afficher uniquement les changements indexés       |
| `include_untracked` | bool                                    | `true`      | Inclure les fichiers non suivis                   |
| `max_diff_lines`    | int                                     | `500`       | Limiter la taille du diff (0 = illimité)          |

**Retourne :** Nom de la branche, état des fichiers (indexés/non indexés/non suivis/conflits), contenu optionnel du diff, statistiques optionnelles et historique optionnel des commits.

### gac_commit

Génère un message de commit alimenté par l'IA et exécute optionnellement le commit.

**Paramètres :**

| Parameter          | Type           | Default | Description                                                   |
| ------------------ | -------------- | ------- | ------------------------------------------------------------- |
| `stage_all`        | bool           | `false` | Indexer tous les changements avant de commiter (`git add -A`) |
| `files`            | list[str]      | `[]`    | Fichiers spécifiques à indexer                                |
| `dry_run`          | bool           | `false` | Aperçu sans exécution                                         |
| `message_only`     | bool           | `false` | Générer le message sans commiter                              |
| `push`             | bool           | `false` | Pousser vers le distant après le commit                       |
| `group`            | bool           | `false` | Diviser les changements en plusieurs commits logiques         |
| `one_liner`        | bool           | `false` | Message de commit sur une seule ligne                         |
| `scope`            | string \| null | `null`  | Portée de commit conventionnel (auto-détectée si non fournie) |
| `hint`             | string         | `""`    | Contexte additionnel pour de meilleurs messages               |
| `model`            | string \| null | `null`  | Remplacer le modèle IA (`provider:model_name`)                |
| `language`         | string \| null | `null`  | Remplacer la langue du message de commit                      |
| `skip_secret_scan` | bool           | `false` | Ignorer l'analyse de sécurité                                 |
| `no_verify`        | bool           | `false` | Ignorer les hooks de pre-commit                               |
| `auto_confirm`     | bool           | `false` | Ignorer les confirmations (requis pour les agents)            |

**Retourne :** Statut de succès, message de commit généré, hash du commit (si commité), liste des fichiers modifiés et éventuels avertissements.

## Flux de travail

### Commit basique

```text
1. gac_status()                              → Voir ce qui a changé
2. gac_commit(stage_all=true, auto_confirm=true)  → Indexer, générer le message et commiter
```

### Aperçu avant le commit

```text
1. gac_status(include_diff=true, include_stats=true)  → Examiner les changements en détail
2. gac_commit(stage_all=true, dry_run=true)            → Aperçu du message de commit
3. gac_commit(stage_all=true, auto_confirm=true)       → Exécuter le commit
```

### Commits groupés

```text
1. gac_status()                                           → Voir tous les changements
2. gac_commit(stage_all=true, group=true, dry_run=true)   → Aperçu des regroupements logiques
3. gac_commit(stage_all=true, group=true, auto_confirm=true)  → Exécuter les commits groupés
```

### Commit avec contexte

```text
1. gac_status(include_history=5)  → Voir les commits récents comme référence de style
2. gac_commit(
     stage_all=true,
     hint="Fixes login timeout bug from issue #42",
     scope="auth",
     auto_confirm=true
   )
```

## Configuration

Le serveur MCP utilise votre configuration GAC existante. Aucune configuration supplémentaire n'est nécessaire au-delà de :

1. **Fournisseur et modèle** : Exécutez `gac init` ou `gac model` pour configurer votre fournisseur d'IA
2. **Clés API** : Stockées dans `~/.gac.env` (configurées lors de `gac init`)
3. **Paramètres optionnels** : Toutes les variables d'environnement GAC s'appliquent (`GAC_LANGUAGE`, `GAC_VERBOSE`, etc.)

Voir la [documentation principale](USAGE.md#notes-de-configuration) pour toutes les options de configuration.

## Dépannage

### "No model configured"

Exécutez `gac init` pour configurer votre fournisseur d'IA et votre modèle avant d'utiliser le serveur MCP.

### "No staged changes found"

Indexez les fichiers manuellement (`git add`) ou utilisez `stage_all=true` dans l'appel à `gac_commit`.

### Le serveur ne démarre pas

Vérifiez que GAC est installé et accessible :

```bash
uvx gac --version
# ou
gac --version
```

Si vous utilisez `uvx`, assurez-vous que `uv` est installé et dans votre PATH.

### L'agent ne trouve pas le serveur

Assurez-vous que le fichier de configuration MCP est au bon emplacement pour votre client et que le chemin du `command` est accessible depuis votre environnement shell.

### Corruption de la sortie Rich

Le serveur MCP redirige automatiquement toute la sortie de la console Rich vers stderr pour empêcher la corruption du protocole stdio. Si vous voyez une sortie illisible, assurez-vous d'exécuter `gac serve` (et non `gac` directement) lors de l'utilisation de MCP.

## Voir aussi

- [Documentation principale](USAGE.md)
- [Configuration OAuth Claude Code](CLAUDE_CODE.md)
- [Configuration OAuth Qwen.ai](QWEN.md)
- [Guide de dépannage](TROUBLESHOOTING.md)
- [Spécification MCP](https://modelcontextprotocol.io/)
