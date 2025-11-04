# Prompts système personnalisés

[English](../en/CUSTOM_SYSTEM_PROMPTS.md) | [简体中文](../zh-CN/CUSTOM_SYSTEM_PROMPTS.md) | [繁體中文](../zh-TW/CUSTOM_SYSTEM_PROMPTS.md) | [日本語](../ja/CUSTOM_SYSTEM_PROMPTS.md) | [한국어](../ko/CUSTOM_SYSTEM_PROMPTS.md) | [हिन्दी](../hi/CUSTOM_SYSTEM_PROMPTS.md) | [Tiếng Việt](../vi/CUSTOM_SYSTEM_PROMPTS.md) | **Français** | [Русский](../ru/CUSTOM_SYSTEM_PROMPTS.md) | [Español](../es/CUSTOM_SYSTEM_PROMPTS.md) | [Português](../pt/CUSTOM_SYSTEM_PROMPTS.md) | [Deutsch](../de/CUSTOM_SYSTEM_PROMPTS.md) | [Nederlands](../nl/CUSTOM_SYSTEM_PROMPTS.md)

Ce guide explique comment personnaliser le prompt système que GAC utilise pour générer des messages de commit, vous permettant de définir votre propre style et conventions de message de commit.

## Table des matières

- [Prompts système personnalisés](#prompts-système-personnalisés)
  - [Table des matières](#table-des-matières)
  - Que sont les prompts système ?
  - Pourquoi utiliser des prompts système personnalisés ?
  - [Démarrage rapide](#démarrage-rapide)
  - [Écrire votre prompt système personnalisé](#écrire-votre-prompt-système-personnalisé)
  - [Exemples](#exemples)
    - [Style de commit avec emojis](#style-de-commit-avec-emojis)
    - [Conventions spécifiques à l'équipe](#conventions-spécifiques-à-léquipe)
    - [Style technique détaillé](#style-technique-détaillé)
  - [Meilleures pratiques](#meilleures-pratiques)
    - [À faire :](#à-faire)
    - [À ne pas faire :](#à-ne-pas-faire)
    - [Conseils :](#conseils)
  - [Dépannage](#dépannage)
    - [Les messages ont toujours le préfixe "chore:"](#les-messages-ont-toujours-le-préfixe-chore)
    - [L'IA ignore mes instructions](#lia-ignore-mes-instructions)
    - [Les messages sont trop longs/courts](#les-messages-sont-trop-longscourts)
    - [Le prompt personnalisé n'est pas utilisé](#le-prompt-personnalisé-nest-pas-utilisé)
    - [Je veux revenir au défaut](#je-veux-revenir-au-défaut)
  - [Documentation connexe](#documentation-connexe)
  - Besoin d'aide ?

## Que sont les prompts système ?

GAC utilise deux prompts lors de la génération de messages de commit :

1. **Prompt système** (personnalisable) : Instructions qui définissent le rôle, le style et les conventions pour les messages de commit
2. **Prompt utilisateur** (automatique) : Les données de git diff montrant ce qui a changé

Le prompt système dit à l'IA _comment_ écrire les messages de commit, tandis que le prompt utilisateur fournit le _quoi_ (les changements de code réels).

## Pourquoi utiliser des prompts système personnalisés ?

Vous pourriez vouloir un prompt système personnalisé si :

- Votre équipe utilise un style de message de commit différent des commits conventionnels
- Vous préférez les emojis, préfixes ou d'autres formats personnalisés
- Vous voulez plus ou moins de détails dans les messages de commit
- Vous avez des directives ou modèles spécifiques à l'entreprise
- Vous voulez correspondre à la voix et au ton de votre équipe
- Vous voulez des messages de commit dans une langue différente (voir Configuration de langue ci-dessous)

## Démarrage rapide

1. **Créez votre fichier de prompt système personnalisé :**

   ```bash
   # Copiez l'exemple comme point de départ
   cp custom_system_prompt.example.txt ~/.config/gac/my_system_prompt.txt

   # Ou créez le vôtre à partir de zéro
   vim ~/.config/gac/my_system_prompt.txt
   ```

2. **Ajoutez à votre fichier `.gac.env` :**

   ```bash
   # Dans ~/.gac.env ou .gac.env au niveau projet
   GAC_SYSTEM_PROMPT_PATH=/path/to/your/custom_system_prompt.txt
   ```

3. **Testez-le :**

   ```bash
   gac --dry-run
   ```

C'est tout ! GAC utilisera maintenant vos instructions personnalisées au lieu du défaut.

## Écrire votre prompt système personnalisé

Votre prompt système personnalisé peut être du texte brut - aucun format spécial ou balises XML requis. Écrivez simplement des instructions claires sur la manière dont l'IA devrait générer les messages de commit.

**Points clés à inclure :**

1. **Définition du rôle** - Ce que l'IA devrait faire
2. **Exigences de format** - Structure, longueur, style
3. **Exemples** - Montrez à quoi ressemblent de bons messages de commit
4. **Contraintes** - Quoi éviter ou exigences à respecter

**Exemple de structure :**

```text
Vous êtes un rédacteur de messages de commit pour [votre projet/équipe].

Lors de l'analyse des changements de code, créez un message de commit qui :

1. [Première exigence]
2. [Deuxième exigence]
3. [Troisième exigence]

Format de l'exemple :
[Montrez un exemple de message de commit]

Votre réponse complète sera utilisée directement comme message de commit.
```

## Exemples

### Style de commit avec emojis

Voyez [`custom_system_prompt.example.txt`](../../examples/custom_system_prompt.example.txt) pour un exemple complet avec emojis.

**Extrait rapide :**

```text
Vous êtes un rédacteur de messages de commit qui utilise des emojis et un ton amical.

Commencez chaque message avec un emoji :
- 🎉 pour les nouvelles fonctionnalités
- 🐛 pour les corrections de bugs
- 📝 pour la documentation
- ♻️ pour les refactorisations

Gardez la première ligne sous 72 caractères et expliquez POURQUOI le changement est important.
```

### Conventions spécifiques à l'équipe

```text
Vous écrivez des messages de commit pour une application bancaire d'entreprise.

Exigences :
1. Commencez par un numéro de ticket JIRA entre crochets (ex: [BANK-1234])
2. Utilisez un ton formel et professionnel
3. Incluez les implications de sécurité si pertinent
4. Référez aux exigences de conformité (PCI-DSS, SOC2, etc.)
5. Gardez les messages concis mais complets

Format :
[TICKET-123] Bref résumé du changement

Explication détaillée de ce qui a changé et pourquoi. Incluez :
- Justification métier
- Approche technique
- Évaluation des risques (si applicable)

Exemple :
[BANK-1234] Implémenter la limitation de débit pour les points de terminaison de connexion

Ajouté une limitation de débit basée sur Redis pour prévenir les attaques par force brute.
Limite les tentatives de connexion à 5 par IP par 15 minutes.
Conforme aux exigences de sécurité SOC2 pour le contrôle d'accès.
```

### Style technique détaillé

```text
Vous êtes un rédacteur technique de messages de commit qui crée une documentation complète.

Pour chaque commit, fournissez :

1. Un titre clair et descriptif (sous 72 caractères)
2. Une ligne vide
3. QUOI : Ce qui a été modifié (2-3 phrases)
4. POURQUOI : Pourquoi le changement était nécessaire (2-3 phrases)
5. COMMENT : Approche technique ou détails d'implémentation clés
6. IMPACT : Fichiers/composants affectés et effets secondaires potentiels

Utilisez une précision technique. Référez des fonctions, classes et modules spécifiques.
Utilisez le temps présent et la voix active.

Exemple :
Refactoriser le middleware d'authentification pour utiliser l'injection de dépendances

QUOI : Rempli l'état d'authentification global par AuthService injectable. Mis à jour
tous les gestionnaires de routes pour accepter AuthService par injection de constructeur.

POURQUOI : L'état global rendait les tests difficiles et créait des dépendances cachées.
L'injection de dépendances améliore la testabilité et rend les dépendances explicites.

COMMENT : Créé l'interface AuthService, implémenté JWTAuthService et
MockAuthService. Modifié les constructeurs de gestionnaire de routes pour exiger AuthService.
Mis à jour la configuration du conteneur d'injection de dépendances.

IMPACT : Affecte toutes les routes authentifiées. Aucun changement de comportement pour les utilisateurs.
Les tests s'exécutent maintenant 3x plus rapidement avec MockAuthService. Migration requise pour
routes/auth.ts, routes/api.ts, et routes/admin.ts.
```

## Meilleures pratiques

### À faire

- ✅ **Soyez spécifique** - Des instructions claires produisent de meilleurs résultats
- ✅ **Incluez des exemples** - Montrez à l'IA à quoi ressemble le bien
- ✅ **Testez itérativement** - Essayez votre prompt, affinez en fonction des résultats
- ✅ **Restez concentré** - Trop de règles peuvent confondre l'IA
- ✅ **Utilisez une terminologie cohérente** - Tenez-vous aux mêmes termes tout au long
- ✅ **Terminez par un rappel** - Renforcez que la réponse sera utilis telle quelle

### À ne pas faire

- ❌ **Utilisez des balises XML** - Le texte brut fonctionne mieux (sauf si vous voulez spécifiquement cette structure)
- ❌ **Rendez-le trop long** - Visez 200-500 mots d'instructions
- ❌ **Contradisez-vous** - Soyez cohérent dans vos exigences
- ❌ **Oubliez la fin** - Rappelez toujours : "Votre réponse complète sera utilisée directement comme message de commit"

### Conseils

- **Commencez avec l'exemple** - Copiez `../../examples/custom_system_prompt.example.txt` et modifiez-le
- **Testez avec `--dry-run`** - Voyez le résultat sans faire de commit
- **Utilisez `--show-prompt`** - Voyez ce qui est envoyé à l'IA
- **Itérez en fonction des résultats** - Si les messages ne sont pas tout à fait droits, ajustez vos instructions
- **Versionnez votre prompt** - Gardez votre prompt personnalisé dans le dépôt de votre équipe
- **Prompts spécifiques au projet** - Utilisez `.gac.env` au niveau projet pour des styles spécifiques au projet

## Dépannage

### Les messages ont toujours le préfixe "chore:"

**Problème :** Vos messages de commit avec emojis reçoivent l'ajout de "chore:".

**Solution :** Ceci ne devrait pas se produire - GAC désactive automatiquement l'application des commits conventionnels lors de l'utilisation de prompts système personnalisés. Si vous voyez cela, veuillez [signaler un problème](https://github.com/cellwebb/gac/issues).

### L'IA ignore mes instructions

**Problème :** Les messages générés ne suivent pas votre format personnalisé.

**Solution :**

1. Rendez vos instructions plus explicites et spécifiques
2. Ajoutez des exemples clairs du format désiré
3. Terminez par : "Votre réponse complète sera utilisée directement comme message de commit"
4. Réduisez le nombre d'exigences - trop peuvent confondre l'IA
5. Essayez d'utiliser un modèle différent (certains suivent mieux les instructions que d'autres)

### Les messages sont trop longs/courts

**Problème :** Les messages générés ne correspondent pas à vos exigences de longueur.

**Solution :**

- Soyez explicite sur la longueur (ex: "Gardez les messages sous 50 caractères")
- Montrez des exemples de la longueur exacte que vous voulez
- Envisagez d'utiliser le drapeau `--one-liner` aussi pour les messages courts

### Le prompt personnalisé n'est pas utilisé

**Problème :** GAC utilise toujours le format de commit par défaut.

**Solution :**

1. Vérifiez que `GAC_SYSTEM_PROMPT_PATH` est correctement configuré :

   ```bash
   gac config get GAC_SYSTEM_PROMPT_PATH
   ```

2. Vérifiez que le chemin du fichier existe et est lisible :

   ```bash
   cat "$GAC_SYSTEM_PROMPT_PATH"
   ```

3. Vérifiez les fichiers `.gac.env` dans cet ordre :
   - Au niveau projet : `./.gac.env`
   - Au niveau utilisateur : `~/.gac.env`
4. Essayez un chemin absolu au lieu d'un chemin relatif

### Configuration de langue

**Note :** Vous n'avez pas besoin d'un prompt système personnalisé pour changer la langue des messages de commit !

Si vous voulez seulement changer la langue de vos messages de commit (tout en gardant le format de commit conventionnel standard), utilisez le sélecteur de langue interactif :

```bash
gac language
```

Ceci présentera un menu interactif avec 25+ langues dans leurs scripts natifs (Español, Français, 日本語, etc.). Sélectionnez votre langue préférée, et elle configurera automatiquement `GAC_LANGUAGE` dans votre fichier `~/.gac.env`.

Alternativement, vous pouvez définir la langue manuellement :

```bash
# Dans ~/.gac.env ou .gac.env au niveau projet
GAC_LANGUAGE=French
```

Par défaut, les préfixes de commits conventionnels (feat:, fix, etc.) restent en anglais pour la compatibilité avec les outils de changelog et pipelines CI/CD, tandis que tout autre texte est dans votre langue spécifiée.

**Vous voulez traduire les préfixes aussi ?** Définissez `GAC_TRANSLATE_PREFIXES=true` dans votre `.gac.env` pour une localisation complète :

```bash
GAC_LANGUAGE=French
GAC_TRANSLATE_PREFIXES=true
```

Ceci traduira tout, y compris les préfixes (ex: `correction:` au lieu de `fix:`).

Ceci est plus simple que de créer un prompt système personnalisé si la langue est votre seul besoin de personnalisation.

### Je veux revenir au défaut

**Problème :** Je veux temporairement utiliser les prompts par défaut.

**Solution :**

```bash
# Option 1 : Supprimer la variable d'environnement
gac config unset GAC_SYSTEM_PROMPT_PATH

# Option 2 : Commenter dans .gac.env
# GAC_SYSTEM_PROMPT_PATH=/path/to/custom_prompt.txt

# Option 3 : Utiliser un .gac.env différent pour des projets spécifiques
```

---

## Documentation connexe

- [USAGE.md](../USAGE.md) - Drapeaux et options de ligne de commande
- [README.md](../README.md) - Installation et configuration de base
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Dépannage général

## Besoin d'aide ?

- Signaler des problèmes : [GitHub Issues](https://github.com/cellwebb/gac/issues)
- Partagez vos prompts personnalisés : Les contributions sont bienvenues !
