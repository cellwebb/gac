[English](../en/QWEN.md) | [简体中文](../zh-CN/QWEN.md) | [繁體中文](../zh-TW/QWEN.md) | [日本語](../ja/QWEN.md) | [한국어](../ko/QWEN.md) | [हिन्दी](../hi/QWEN.md) | [Tiếng Việt](../vi/QWEN.md) | **Français** | [Русский](../ru/QWEN.md) | [Español](../es/QWEN.md) | [Português](../pt/QWEN.md) | [Norsk](../no/QWEN.md) | [Svenska](../sv/QWEN.md) | [Deutsch](../de/QWEN.md) | [Nederlands](../nl/QWEN.md) | [Italiano](../it/QWEN.md)

# Utiliser Qwen.ai avec GAC

GAC prend en charge l'authentification via Qwen.ai OAuth, vous permettant d'utiliser votre compte Qwen.ai pour la génération de messages de commit. Cela utilise l'authentification par flux d'appareil OAuth pour une expérience de connexion transparente.

## Qu'est-ce que Qwen.ai ?

Qwen.ai est la plateforme d'IA d'Alibaba Cloud qui donne accès à la famille de grands modèles de langage Qwen. GAC prend en charge l'authentification basée sur OAuth, vous permettant d'utiliser votre compte Qwen.ai sans avoir à gérer manuellement les clés API.

## Avantages

- **Authentification facile** : Flux d'appareil OAuth - connectez-vous simplement avec votre navigateur
- **Pas de gestion de clé API** : L'authentification est gérée automatiquement
- **Accès aux modèles Qwen** : Utilisez de puissants modèles Qwen pour la génération de messages de commit

## Configuration

GAC inclut une authentification OAuth intégrée pour Qwen.ai utilisant le flux d'appareil. Le processus de configuration affichera un code et ouvrira votre navigateur pour l'authentification.

### Option 1 : Lors de la configuration initiale (Recommandé)

Lors de l'exécution de `gac init`, sélectionnez simplement "Qwen.ai (OAuth)" comme fournisseur :

```bash
gac init
```

L'assistant va :

1. Vous demander de sélectionner "Qwen.ai (OAuth)" dans la liste des fournisseurs
2. Afficher un code d'appareil et ouvrir votre navigateur
3. Vous vous authentifierez sur Qwen.ai et saisirez le code
4. Enregistrer votre jeton d'accès en toute sécurité
5. Définir le modèle par défaut

### Option 2 : Passer à Qwen.ai plus tard

Si vous avez déjà configuré GAC avec un autre fournisseur et souhaitez passer à Qwen.ai :

```bash
gac model
```

Ensuite :

1. Sélectionnez "Qwen.ai (OAuth)" dans la liste des fournisseurs
2. Suivez le flux d'authentification par code d'appareil
3. Jeton enregistré en toute sécurité dans `~/.gac/oauth/qwen.json`
4. Modèle configuré automatiquement

### Option 3 : Connexion directe

Vous pouvez également vous authentifier directement en utilisant :

```bash
gac auth qwen login
```

Cela va :

1. Afficher un code d'appareil
2. Ouvrir votre navigateur sur la page d'authentification Qwen.ai
3. Après votre authentification, le jeton est enregistré automatiquement

### Utiliser GAC normalement

Une fois authentifié, utilisez GAC comme d'habitude :

```bash
# Indexer vos modifications
git add .

# Générer et commiter avec Qwen.ai
gac

# Ou remplacer le modèle pour un seul commit
gac -m qwen:qwen3-coder-plus
```

## Modèles disponibles

L'intégration Qwen.ai OAuth utilise :

- `qwen3-coder-plus` - Optimisé pour les tâches de codage (par défaut)

C'est le modèle disponible via le point de terminaison OAuth portal.qwen.ai. Pour d'autres modèles Qwen, envisagez d'utiliser le fournisseur OpenRouter qui offre des options de modèles Qwen supplémentaires.

## Commandes d'authentification

GAC fournit plusieurs commandes pour gérer l'authentification Qwen.ai :

```bash
# Se connecter à Qwen.ai
gac auth qwen login

# Vérifier l'état de l'authentification
gac auth qwen status

# Se déconnecter et supprimer le jeton stocké
gac auth qwen logout

# Vérifier l'état de tous les fournisseurs OAuth
gac auth
```

### Options de connexion

```bash
# Connexion standard (ouvre le navigateur automatiquement)
gac auth qwen login

# Connexion sans ouvrir le navigateur (affiche l'URL à visiter manuellement)
gac auth qwen login --no-browser

# Mode silencieux (sortie minimale)
gac auth qwen login --quiet
```

## Dépannage

### Jeton expiré

Si vous voyez des erreurs d'authentification, votre jeton a peut-être expiré. Ré-authentifiez-vous en exécutant :

```bash
gac auth qwen login
```

Le flux de code d'appareil démarrera et votre navigateur s'ouvrira pour la ré-authentification.

### Vérifier l'état de l'authentification

Pour vérifier si vous êtes actuellement authentifié :

```bash
gac auth qwen status
```

Ou vérifiez tous les fournisseurs à la fois :

```bash
gac auth
```

### Déconnexion

Pour supprimer votre jeton stocké :

```bash
gac auth qwen logout
```

### "Qwen authentication not found" (Authentification Qwen introuvable)

Cela signifie que GAC ne peut pas trouver votre jeton d'accès. Authentifiez-vous en exécutant :

```bash
gac auth qwen login
```

Ou exécutez `gac model` et sélectionnez "Qwen.ai (OAuth)" dans la liste des fournisseurs.

### "Authentication failed" (Échec de l'authentification)

Si l'authentification OAuth échoue :

1. Assurez-vous d'avoir un compte Qwen.ai
2. Vérifiez que votre navigateur s'ouvre correctement
3. Vérifiez que vous avez saisi le code d'appareil correctement
4. Essayez un autre navigateur si les problèmes persistent
5. Vérifiez la connectivité réseau vers `qwen.ai`

### Le code d'appareil ne fonctionne pas

Si l'authentification par code d'appareil ne fonctionne pas :

1. Assurez-vous que le code n'a pas expiré (les codes sont valides pour une durée limitée)
2. Essayez d'exécuter à nouveau `gac auth qwen login` pour obtenir un nouveau code
3. Utilisez le drapeau `--no-browser` et visitez manuellement l'URL si l'ouverture du navigateur échoue

## Notes de sécurité

- **Ne commitez jamais votre jeton d'accès** dans le contrôle de version
- GAC stocke automatiquement les jetons dans `~/.gac/oauth/qwen.json` (en dehors de votre répertoire de projet)
- Les fichiers de jetons ont des permissions restreintes (lisibles uniquement par le propriétaire)
- Les jetons peuvent expirer et nécessiteront une ré-authentification
- Le flux d'appareil OAuth est conçu pour une authentification sécurisée sur les systèmes sans tête

## Voir aussi

- [Documentation principale](USAGE.md)
- [Configuration de Claude Code](CLAUDE_CODE.md)
- [Guide de dépannage](TROUBLESHOOTING.md)
- [Documentation Qwen.ai](https://qwen.ai)
