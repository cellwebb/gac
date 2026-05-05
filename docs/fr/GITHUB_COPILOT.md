# Utiliser GitHub Copilot avec GAC

[English](../en/GITHUB_COPILOT.md) | [简体中文](../zh-CN/GITHUB_COPILOT.md) | [繁體中文](../zh-TW/GITHUB_COPILOT.md) | [日本語](../ja/GITHUB_COPILOT.md) | [한국어](../ko/GITHUB_COPILOT.md) | [हिन्दी](../hi/GITHUB_COPILOT.md) | [Tiếng Việt](../vi/GITHUB_COPILOT.md) | **Français** | [Русский](../ru/GITHUB_COPILOT.md) | [Español](../es/GITHUB_COPILOT.md) | [Português](../pt/GITHUB_COPILOT.md) | [Norsk](../no/GITHUB_COPILOT.md) | [Svenska](../sv/GITHUB_COPILOT.md) | [Deutsch](../de/GITHUB_COPILOT.md) | [Nederlands](../nl/GITHUB_COPILOT.md) | [Italiano](../it/GITHUB_COPILOT.md)

GAC prend en charge l'authentification via GitHub Copilot, vous permettant d'utiliser votre abonnement Copilot pour accéder à des modèles d'OpenAI, Anthropic, Google et plus — tout inclus dans votre plan GitHub Copilot.

## Qu'est-ce que GitHub Copilot OAuth ?

GitHub Copilot OAuth utilise le **Device Flow** — une méthode d'authentification sécurisée basée sur le navigateur qui ne nécessite pas de serveur de rappel local. Vous visitez une URL, saisissez un code à usage unique et autorisez GAC à utiliser votre accès Copilot. En coulisses, GAC échange votre jeton OAuth GitHub de longue durée contre des jetons de session Copilot de courte durée (~30 min) qui accordent l'accès à l'API Copilot.

Cela vous donne accès à des modèles de plusieurs fournisseurs via un seul abonnement :

- **OpenAI** — `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`
- **Anthropic** — `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5`
- **Google** — `gemini-2.5-pro`, `gemini-2.5-flash`

## Avantages

- **Accès multi-fournisseurs** : Utilisez des modèles d'OpenAI, Anthropic et Google via un seul abonnement
- **Rapport coût-efficacité** : Utilisez votre abonnement Copilot existant au lieu de payer séparément des clés API
- **Aucune gestion de clé API** : Authentification Device Flow — pas de clés à faire tourner ou stocker
- **Prise en charge de GitHub Enterprise** : Fonctionne avec les instances GHE via le drapeau `--host`

## Configuration

### Option 1 : Lors de la configuration initiale (Recommandé)

Lors de l'exécution de `gac init`, sélectionnez simplement « Copilot » comme fournisseur :

```bash
gac init
```

L'assistant :

1. Vous demandera de sélectionner « Copilot » dans la liste des fournisseurs
2. Affichera un code à usage unique et ouvrira votre navigateur pour l'authentification Device Flow
3. Enregistrera votre jeton OAuth dans `~/.gac/oauth/copilot.json`
4. Définira le modèle par défaut

### Option 2 : Passer à Copilot plus tard

Si vous avez déjà configuré GAC avec un autre fournisseur :

```bash
gac model
```

Puis sélectionnez « Copilot » dans la liste des fournisseurs et authentifiez-vous.

### Option 3 : Connexion directe

Authentifiez-vous directement sans changer votre modèle par défaut :

```bash
gac auth copilot login
```

### Utiliser GAC normalement

Une fois authentifié, utilisez GAC comme d'habitude :

```bash
# Stager vos modifications
git add .

# Générer et committer avec Copilot
gac

# Ou remplacer le modèle pour un commit unique
gac -m copilot:gpt-4.1
gac -m copilot:claude-sonnet-4.5
gac -m copilot:gemini-2.5-pro
```

## Modèles disponibles

Copilot donne accès à des modèles de plusieurs fournisseurs. Les modèles actuels incluent :

| Fournisseur | Modèles                                                                                        |
| ----------- | ---------------------------------------------------------------------------------------------- |
| OpenAI      | `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `o3`, `o4-mini`                                           |
| Anthropic   | `claude-opus-4.6`, `claude-opus-4`, `claude-sonnet-4`, `claude-sonnet-4.5`, `claude-haiku-4.5` |
| Google      | `gemini-2.5-pro`, `gemini-2.5-flash`                                                           |

> **Note :** La liste de modèles affichée après la connexion est informative et peut devenir obsolète à mesure que GitHub ajoute de nouveaux modèles. Consultez la [documentation GitHub Copilot](https://docs.github.com/en/copilot) pour les modèles disponibles les plus récents.

## GitHub Enterprise

Pour vous authentifier avec une instance GitHub Enterprise :

```bash
gac auth copilot login --host ghe.mycompany.com
```

GAC utilisera automatiquement les endpoints Device Flow et API corrects pour votre instance GHE. Le jeton de session est mis en cache par hôte, donc différentes instances GHE sont gérées indépendamment.

## Commandes CLI

GAC fournit des commandes CLI dédiées pour la gestion de l'authentification Copilot :

### Connexion

Authentifiez-vous ou ré-authentifiez-vous avec GitHub Copilot :

```bash
gac auth copilot login
```

Votre navigateur s'ouvrira sur une page Device Flow où vous saisissez un code à usage unique. Si vous êtes déjà authentifié, il vous sera demandé si vous souhaitez vous ré-authentifier.

Pour GitHub Enterprise :

```bash
gac auth copilot login --host ghe.mycompany.com
```

### Déconnexion

Supprimez les jetons Copilot stockés :

```bash
gac auth copilot logout
```

Cela supprime le fichier de jeton stocké à `~/.gac/oauth/copilot.json` et le cache de session.

### Statut

Vérifiez votre statut d'authentification Copilot actuel :

```bash
gac auth copilot status
```

Ou vérifiez tous les fournisseurs en une fois :

```bash
gac auth
```

## Comment ça fonctionne

Le flux d'authentification Copilot diffère de l'OAuth ChatGPT et Claude Code :

1. **Device Flow** — GAC demande un code d'appareil à GitHub et l'affiche
2. **Autorisation du navigateur** — Vous visitez l'URL et saisissez le code
3. **Sondage de jeton** — GAC interroge GitHub jusqu'à ce que vous complétiez l'autorisation
4. **Échange de jeton de session** — Le jeton OAuth GitHub est échangé contre un jeton de session Copilot de courte durée
5. **Actualisation automatique** — Les jetons de session (~30 min) sont automatiquement renouvelés à partir du jeton OAuth mis en cache

Contrairement à l'OAuth basé sur PKCE (ChatGPT/Claude Code), le Device Flow ne nécessite pas de serveur de rappel local ni de gestion de ports.

## Dépannage

### « Authentification Copilot introuvable »

Exécutez la commande de connexion pour vous authentifier :

```bash
gac auth copilot login
```

### « Impossible d'obtenir le jeton de session Copilot »

Cela signifie que GAC a obtenu un jeton OAuth GitHub mais n'a pas pu l'échanger contre un jeton de session Copilot. Cela signifie généralement :

1. **Pas d'abonnement Copilot** — Votre compte GitHub n'a pas d'abonnement Copilot actif
2. **Jeton révoqué** — Le jeton OAuth a été révoqué ; ré-authentifiez-vous avec `gac auth copilot login`

### Jeton de session expiré

Les jetons de session expirent après ~30 minutes. GAC les renouvelle automatiquement à partir du jeton OAuth mis en cache, vous ne devriez donc pas avoir besoin de vous ré-authentifier fréquemment. Si l'actualisation automatique échoue :

```bash
gac auth copilot login
```

### « Nom d'hôte invalide ou non sécurisé »

Le drapeau `--host` valide strictement les noms d'hôte pour prévenir les attaques SSRF. Si vous voyez cette erreur :

- Assurez-vous que le nom d'hôte n'inclut pas de ports (ex. utilisez `ghe.company.com` pas `ghe.company.com:8080`)
- N'incluez pas de protocoles ni de chemins (ex. utilisez `ghe.company.com` pas `https://ghe.company.com/api`)
- Les adresses IP privées et `localhost` sont bloquées pour des raisons de sécurité

### Problèmes GitHub Enterprise

Si l'authentification GHE échoue :

1. Vérifiez que votre instance GHE a Copilot activé
2. Vérifiez que le nom d'hôte de votre GHE est accessible depuis votre machine
3. Assurez-vous que votre compte GHE a une licence Copilot
4. Essayez avec le drapeau `--host` explicitement : `gac auth copilot login --host ghe.mycompany.com`

## Différences avec les autres fournisseurs OAuth

| Fonctionnalité      | ChatGPT OAuth               | Claude Code              | Copilot                                         |
| ------------------- | --------------------------- | ------------------------ | ----------------------------------------------- |
| Méthode d'auth      | PKCE (rappel navigateur)    | PKCE (rappel navigateur) | Device Flow (code à usage unique)               |
| Serveur de rappel   | Ports 1455-1465             | Ports 8765-8795          | Non nécessaire                                  |
| Durée du jeton      | Longue durée (auto-refresh) | Expirant (ré-auth)       | Session ~30 min (auto-refresh)                  |
| Modèles             | OpenAI optimisé Codex       | Famille Claude           | Multi-fournisseur (OpenAI + Anthropic + Google) |
| Prise en charge GHE | Non                         | Non                      | Oui (drapeau `--host`)                          |

## Notes de sécurité

- **Ne commitez jamais votre jeton OAuth** dans le contrôle de version
- GAC stocke les jetons OAuth dans `~/.gac/oauth/copilot.json` (en dehors de votre répertoire de projet)
- Les jetons de session sont mis en cache dans `~/.gac/oauth/copilot_session.json` avec des permissions `0o600`
- Les noms d'hôte sont strictement validés pour prévenir les attaques SSRF et d'injection d'URL
- Les adresses IP privées, adresses de bouclage et `localhost` sont bloqués comme noms d'hôte
- Le Device Flow n'expose aucun port local, réduisant la surface d'attaque

## Voir aussi

- [Documentation principale](USAGE.md)
- [Guide de dépannage](TROUBLESHOOTING.md)
- [Guide ChatGPT OAuth](CHATGPT_OAUTH.md)
- [Guide Claude Code](CLAUDE_CODE.md)
- [Documentation GitHub Copilot](https://docs.github.com/en/copilot)
