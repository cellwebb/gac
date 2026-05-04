# Utiliser ChatGPT OAuth avec GAC

**English** | [简体中文](../zh-CN/CHATGPT_OAUTH.md) | [繁體中文](../zh-TW/CHATGPT_OAUTH.md) | [日本語](../ja/CHATGPT_OAUTH.md) | [한국어](../ko/CHATGPT_OAUTH.md) | [हिन्दी](../hi/CHATGPT_OAUTH.md) | [Tiếng Việt](../vi/CHATGPT_OAUTH.md) | [Français](../fr/CHATGPT_OAUTH.md) | [Русский](../ru/CHATGPT_OAUTH.md) | [Español](../es/CHATGPT_OAUTH.md) | [Português](../pt/CHATGPT_OAUTH.md) | [Norsk](../no/CHATGPT_OAUTH.md) | [Svenska](../sv/CHATGPT_OAUTH.md) | [Deutsch](../de/CHATGPT_OAUTH.md) | [Nederlands](../nl/CHATGPT_OAUTH.md) | [Italiano](../it/CHATGPT_OAUTH.md)

GAC prend en charge l'authentification via ChatGPT OAuth, vous permettant d'utiliser votre abonnement ChatGPT pour accéder à l'API Codex d'OpenAI au lieu de payer séparément des clés API OpenAI. Cela reflète le même flux OAuth utilisé par le CLI Codex d'OpenAI.

> ⚠️ **Attention — utilisation non approuvée :** Cela utilise le même flux OAuth que le CLI Codex d'OpenAI, et bien que cela fonctionne actuellement, OpenAI peut restreindre l'utilisation des jetons tiers à tout moment. GAC est suffisamment petit pour avoir échappé à l'attention jusqu'à présent, mais l'utilisation de ChatGPT OAuth ici **n'est pas officiellement approuvée** pour les outils tiers et pourrait cesser de fonctionner à tout moment. Si vous avez besoin d'une génération fiable de messages de commit, utilisez un fournisseur API direct (`openai`, etc.). Consultez la [documentation Codex d'OpenAI](https://openai.com/codex) pour la politique actuelle.

## Qu'est-ce que ChatGPT OAuth ?

ChatGPT OAuth vous permet de tirer parti de votre abonnement ChatGPT Plus ou Pro existant pour accéder à l'API Codex afin de générer des messages de commit. Au lieu de gérer des clés API et une facturation par jeton, vous vous authentifiez une fois via votre navigateur et GAC gère automatiquement le cycle de vie du jeton.

## Avantages

- **Rapport coût-efficacité** : Utilisez votre abonnement ChatGPT Plus/Pro existant au lieu de payer séparément l'accès API
- **Mêmes modèles** : Accédez aux modèles optimisés pour Codex (`gpt-5.5`, `gpt-5.4`, `gpt-5.3-codex`)
- **Aucune gestion de clé API** : L'OAuth basé sur le navigateur signifie qu'aucune clé API n'est à faire tourner ou à stocker
- **Facturation séparée** : L'utilisation de ChatGPT OAuth est séparée de la facturation API OpenAI directe

## Configuration

GAC inclut une authentification OAuth intégrée pour ChatGPT. Le processus de configuration est entièrement automatisé et ouvrira votre navigateur pour l'authentification.

### Option 1 : Lors de la configuration initiale (Recommandé)

Lors de l'exécution de `gac init`, sélectionnez simplement « ChatGPT OAuth » comme fournisseur :

```bash
gac init
```

L'assistant :

1. Vous demandera de sélectionner « ChatGPT OAuth » dans la liste des fournisseurs
2. Ouvrira automatiquement votre navigateur pour l'authentification OAuth
3. Enregistrera votre jeton d'accès dans `~/.gac/oauth/chatgpt-oauth.json`
4. Définira le modèle par défaut

### Option 2 : Passer à ChatGPT OAuth plus tard

Si vous avez déjà configuré GAC avec un autre fournisseur et que vous souhaitez passer à ChatGPT OAuth :

```bash
gac model
```

Ensuite :

1. Sélectionnez « ChatGPT OAuth » dans la liste des fournisseurs
2. Votre navigateur s'ouvrira automatiquement pour l'authentification OAuth
3. Le jeton est enregistré dans `~/.gac/oauth/chatgpt-oauth.json`
4. Le modèle est configuré automatiquement

### Utiliser GAC normalement

Une fois authentifié, utilisez GAC comme d'habitude :

```bash
# Stager vos modifications
git add .

# Générer et committer avec ChatGPT OAuth
gac

# Ou remplacer le modèle pour un commit unique
gac -m chatgpt-oauth:gpt-5.5
```

## Modèles disponibles

ChatGPT OAuth donne accès aux modèles optimisés pour Codex. Les modèles actuels incluent :

- `gpt-5.5` — Dernier modèle Codex le plus performant
- `gpt-5.4` — Modèle Codex de génération précédente
- `gpt-5.3-codex` — Modèle Codex de troisième génération

Consultez la [documentation OpenAI](https://platform.openai.com/docs/models) pour la liste complète des modèles disponibles.

## Commandes CLI

GAC fournit des commandes CLI dédiées pour la gestion de ChatGPT OAuth :

### Connexion

Authentifiez-vous ou ré-authentifiez-vous avec ChatGPT OAuth :

```bash
gac auth chatgpt login
```

Votre navigateur s'ouvrira automatiquement pour terminer le flux OAuth. Si vous êtes déjà authentifié, cela actualisera vos jetons.

### Déconnexion

Supprimez les jetons ChatGPT OAuth stockés :

```bash
gac auth chatgpt logout
```

Cela supprime le fichier de jeton stocké à `~/.gac/oauth/chatgpt-oauth.json`.

### Statut

Vérifiez votre statut d'authentification ChatGPT OAuth actuel :

```bash
gac auth chatgpt status
```

Ou vérifiez tous les fournisseurs en une fois :

```bash
gac auth
```

## Dépannage

### Jeton expiré

Si vous voyez des erreurs d'authentification, votre jeton a peut-être expiré. Ré-authentifiez-vous en exécutant :

```bash
gac auth chatgpt login
```

Votre navigateur s'ouvrira automatiquement pour une nouvelle authentification OAuth. GAC utilise automatiquement les jetons d'actualisation pour renouveler l'accès sans ré-authentification lorsque cela est possible.

### Vérifier le statut d'authentification

Pour vérifier si vous êtes actuellement authentifié :

```bash
gac auth chatgpt status
```

Ou vérifiez tous les fournisseurs en une fois :

```bash
gac auth
```

### Déconnexion

Pour supprimer votre jeton stocké :

```bash
gac auth chatgpt logout
```

### « Jeton ChatGPT OAuth introuvable »

Cela signifie que GAC ne trouve pas votre jeton d'accès. Authentifiez-vous en exécutant :

```bash
gac model
```

Sélectionnez ensuite « ChatGPT OAuth » dans la liste des fournisseurs. Le flux OAuth démarrera automatiquement.

### « Échec de l'authentification »

Si l'authentification OAuth échoue :

1. Assurez-vous d'avoir un abonnement ChatGPT Plus ou Pro actif
2. Vérifiez que votre navigateur s'ouvre correctement
3. Essayez un autre navigateur si les problèmes persistent
4. Vérifiez la connectivité réseau vers `auth.openai.com`
5. Vérifiez que les ports 1455-1465 sont disponibles pour le serveur de rappel local

### Port déjà utilisé

Le serveur de rappel OAuth essaie automatiquement les ports 1455-1465. Si tous les ports sont occupés :

```bash
# Sur macOS/Linux :
lsof -ti:1455-1465 | xargs kill -9

# Sur Windows (PowerShell) :
Get-NetTCPConnection -LocalPort 1455,1456,1457,1458,1459,1460,1461,1462,1463,1464,1465 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

Puis ré-exécutez `gac auth chatgpt login`.

## Différences avec le fournisseur OpenAI

| Fonctionnalité     | OpenAI (`openai:`)            | ChatGPT OAuth (`chatgpt-oauth:`)                                     |
| ------------------ | ----------------------------- | -------------------------------------------------------------------- |
| Authentification   | Clé API (`OPENAI_API_KEY`)    | OAuth (flux de navigateur automatisé)                                |
| Facturation        | Facturation API par jeton     | Basée sur l'abonnement (ChatGPT Plus/Pro)                            |
| Configuration      | Saisie manuelle de la clé API | OAuth automatique via `gac init` ou `gac model`                      |
| Gestion des jetons | Clés API de longue durée      | Jetons OAuth (actualisation automatique avec jetons d'actualisation) |
| Modèles            | Tous les modèles OpenAI       | Modèles optimisés pour Codex                                         |

## Notes de sécurité

- **Ne commitez jamais votre jeton d'accès** dans le contrôle de version
- GAC stocke les jetons OAuth dans `~/.gac/oauth/chatgpt-oauth.json` (en dehors de votre répertoire de projet)
- Le flux OAuth utilise PKCE (Proof Key for Code Exchange) pour une sécurité renforcée
- Le serveur de rappel local s'exécute uniquement sur localhost (ports 1455-1465)
- Les jetons d'actualisation sont utilisés pour renouveler automatiquement l'accès sans ré-authentification

## Voir aussi

- [Documentation principale](USAGE.md)
- [Guide de dépannage](TROUBLESHOOTING.md)
- [Documentation Codex d'OpenAI](https://openai.com/codex)
