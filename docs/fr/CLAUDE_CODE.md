# Utiliser Claude Code avec GAC

[English](../en/CLAUDE_CODE.md) | [简体中文](../zh-CN/CLAUDE_CODE.md) | [繁體中文](../zh-TW/CLAUDE_CODE.md) | [日本語](../ja/CLAUDE_CODE.md) | [한국어](../ko/CLAUDE_CODE.md) | [हिन्दी](../hi/CLAUDE_CODE.md) | [Tiếng Việt](../vi/CLAUDE_CODE.md) | **Français** | [Русский](../ru/CLAUDE_CODE.md) | [Español](../es/CLAUDE_CODE.md) | [Português](../pt/CLAUDE_CODE.md) | [Norsk](../no/CLAUDE_CODE.md) | [Svenska](../sv/CLAUDE_CODE.md) | [Deutsch](../de/CLAUDE_CODE.md) | [Nederlands](../nl/CLAUDE_CODE.md) | [Italiano](../it/CLAUDE_CODE.md)

GAC prend en charge l'authentification via les abonnements Claude Code, vous permettant d'utiliser votre abonnement Claude Code au lieu de payer pour l'API Anthropic coûteuse. C'est parfait pour les utilisateurs qui ont déjà accès à Claude Code via leur abonnement.

## Qu'est-ce que Claude Code ?

Claude Code est le service d'abonnement d'Anthropic qui fournit un accès aux modèles Claude basé sur OAuth. Au lieu d'utiliser des clés API (qui sont facturées par token), Claude Code utilise des tokens OAuth de votre abonnement.

## Avantages

- **Rentable** : Utilisez votre abonnement Claude Code existant au lieu de payer séparément pour l'accès API
- **Mêmes modèles** : Accédez aux mêmes modèles Claude (par exemple, `claude-sonnet-4-5`)
- **Facturation séparée** : L'utilisation de Claude Code est séparée de la facturation de l'API Anthropic

## Configuration

GAC inclut une authentification OAuth intégrée pour Claude Code. Le processus de configuration est entièrement automatisé et ouvrira votre navigateur pour l'authentification.

### Option 1 : Lors de la configuration initiale (Recommandé)

Lors de l'exécution de `gac init`, sélectionnez simplement "Claude Code" comme votre fournisseur :

```bash
gac init
```

L'assistant va :

1. Vous demander de sélectionner "Claude Code" dans la liste des fournisseurs
2. Ouvrir automatiquement votre navigateur pour l'authentification OAuth
3. Sauvegarder votre jeton d'accès dans `~/.gac.env`
4. Définir le modèle par défaut

### Option 2 : Basculer vers Claude Code plus tard

Si vous avez déjà configuré GAC avec un autre fournisseur et souhaitez passer à Claude Code :

```bash
gac model
```

Ensuite :

1. Sélectionnez "Claude Code" dans la liste des fournisseurs
2. Votre navigateur s'ouvrira automatiquement pour l'authentification OAuth
3. Jeton sauvegardé dans `~/.gac.env`
4. Modèle configuré automatiquement

### Utiliser GAC normalement

Une fois authentifié, utilisez GAC comme d'habitude :

```bash
# Stagez vos changements
git add .

# Générez et commitez avec Claude Code
gac

# Ou substituez le modèle pour un commit unique
gac -m claude-code:claude-sonnet-4-5
```

## Modèles disponibles

Claude Code fournit un accès aux mêmes modèles que l'API Anthropic. Les modèles actuels de la famille Claude 4.5 incluent :

- `claude-sonnet-4-5` - Dernier modèle Sonnet le plus intelligent, meilleur pour le codage
- `claude-haiku-4-5` - Rapide et efficace
- `claude-opus-4-5` - Modèle le plus capable pour le raisonnement complexe

Consultez la [documentation Claude](https://docs.claude.com/en/docs/about-claude/models/overview) pour la liste complète des modèles disponibles.

## Dépannage

### Jeton expiré

Si vous voyez des erreurs d'authentification, votre jeton a peut-être expiré. Réauthentifiez-vous en exécutant :

```bash
gac auth claude-code login
```

Votre navigateur s'ouvrira automatiquement pour une nouvelle authentification OAuth. Alternativement, vous pouvez exécuter `gac model`, sélectionner "Claude Code (OAuth)" et choisir "Se réauthentifier (obtenir un nouveau jeton)".

### Vérifier l'état d'authentification

Pour vérifier si vous êtes actuellement authentifié :

```bash
gac auth claude-code status
```

Ou vérifiez tous les fournisseurs à la fois :

```bash
gac auth
```

### Déconnexion

Pour supprimer votre jeton stocké :

```bash
gac auth claude-code logout
```

### "CLAUDE_CODE_ACCESS_TOKEN non trouvé"

Cela signifie que GAC ne peut pas trouver votre jeton d'accès. Authentifiez-vous en exécutant :

```bash
gac model
```

Ensuite sélectionnez "Claude Code" dans la liste des fournisseurs. Le flux OAuth démarrera automatiquement.

### "Échec de l'authentification"

Si l'authentification OAuth échoue :

1. Assurez-vous d'avoir un abonnement Claude Code actif
2. Vérifiez que votre navigateur s'ouvre correctement
3. Essayez un autre navigateur si les problèmes persistent
4. Vérifiez la connectivité réseau à `claude.ai`
5. Vérifiez que les ports 8765-8795 sont disponibles pour le serveur de callback local

## Différences avec le fournisseur Anthropic

| Fonctionnalité     | Anthropic (`anthropic:`)      | Claude Code (`claude-code:`)                              |
| ------------------ | ----------------------------- | --------------------------------------------------------- |
| Authentification   | Clé API (`ANTHROPIC_API_KEY`) | OAuth (flux navigateur automatique)                       |
| Facturation        | Facturation API par token     | Basé sur l'abonnement                                     |
| Configuration      | Saisie manuelle de clé API    | OAuth automatique via `gac init` ou `gac model`           |
| Gestion des jetons | Clés API longue durée         | Jetons OAuth (peuvent expirer, réauth facile via `model`) |
| Modèles            | Mêmes modèles                 | Mêmes modèles                                             |

## Notes de sécurité

- **Ne commitez jamais votre jeton d'accès** dans le contrôle de version
- GAC stocke automatiquement les jetons dans `~/.gac.env` (en dehors de votre répertoire de projet)
- Les jetons peuvent expirer et nécessiteront une réauthentification via `gac model`
- Le flux OAuth utilise PKCE (Proof Key for Code Exchange) pour une sécurité renforcée
- Le serveur de callback local ne s'exécute que sur localhost (ports 8765-8795)

## Voir aussi

- [Documentation principale](USAGE.md)
- [Guide de configuration de Qwen.ai](QWEN.md)
- [Guide de dépannage](TROUBLESHOOTING.md)
- [Documentation Claude Code](https://claude.ai/code)
