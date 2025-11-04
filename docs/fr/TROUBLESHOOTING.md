# Dépannage de gac

[English](../en/TROUBLESHOOTING.md) | [简体中文](../zh-CN/TROUBLESHOOTING.md) | [繁體中文](../zh-TW/TROUBLESHOOTING.md) | [日本語](../ja/TROUBLESHOOTING.md) | [한국어](../ko/TROUBLESHOOTING.md) | [हिन्दी](../hi/TROUBLESHOOTING.md) | **Français** | [Русский](../ru/TROUBLESHOOTING.md) | [Español](../es/TROUBLESHOOTING.md) | [Português](../pt/TROUBLESHOOTING.md) | [Deutsch](../de/TROUBLESHOOTING.md) | [Nederlands](../nl/TROUBLESHOOTING.md)

Ce guide couvre les problèmes courants et solutions pour installer, configurer et exécuter gac.

## Table des matières

- [Dépannage de gac](#dépannage-de-gac)
  - [Table des matières](#table-des-matières)
  - [1. Problèmes d'installation](#1-problèmes-dinstallation)
  - [2. Problèmes de configuration](#2-problèmes-de-configuration)
  - [3. Erreurs de fournisseur/API](#3-erreurs-de-fournisseurapi)
  - [4. Problèmes de regroupement de commits](#4-problèmes-de-regroupement-de-commits)
  - [5. Sécurité et détection de secrets](#5-sécurité-et-détection-de-secrets)
  - [6. Problèmes de hooks Pre-commit et Lefthook](#6-problèmes-de-hooks-pre-commit-et-lefthook)
  - [7. Problèmes de workflow courants](#7-problèmes-de-workflow-courants)
  - [8. Débogage général](#8-débogage-général)
  - Toujours bloqué ?
  - [Où obtenir une aide supplémentaire](#où-obtenir-une-aide-supplémentaire)

## 1. Problèmes d'installation

**Problème :** Commande `gac` non trouvée après l'installation

- Assurez-vous d'avoir installé avec `uv tool install gac` ou `uvx gac`
- Si vous avez utilisé `uv tool install`, vérifiez l'installation avec `uv tool list`
- Assurez-vous que `uv` est installé et dans votre `$PATH`
- Redémarrez votre terminal après l'installation

**Problème :** Permission refusée ou impossible d'écrire des fichiers

- Vérifiez les permissions du répertoire
- Essayez d'exécuter avec les permissions appropriées ou changez la propriété du répertoire

## 2. Problèmes de configuration

**Problème :** gac ne trouve pas votre clé API ou modèle

- Si vous êtes nouveau, exécutez `gac init` pour configurer de manière interactive votre fournisseur, modèle et clés API
- Assurez-vous que vos `.gac.env` ou variables d'environnement sont correctement configurés
- Exécutez `gac --log-level=debug` pour voir quels fichiers de configuration sont chargés et déboguer les problèmes de configuration
- Vérifiez les fautes de frappe dans les noms de variables (ex: `GAC_GROQ_API_KEY`)

**Problème :** Les changements `$HOME/.gac.env` au niveau utilisateur ne sont pas pris en compte

- Assurez-vous d'éditer le bon fichier pour votre OS :
  - Sur macOS/Linux : `$HOME/.gac.env` (habituellement `/Users/<votre-nom-utilisateur>/.gac.env` ou `/home/<votre-nom-utilisateur>/.gac.env`)
  - Sur Windows : `$HOME/.gac.env` (généralement `C:\Users\<votre-nom-utilisateur>\.gac.env` ou utilisez `%USERPROFILE%`)
- Exécutez `gac --log-level=debug` pour confirmer que la configuration au niveau utilisateur est chargée
- Redémarrez votre terminal ou ré-exécutez votre shell pour recharger les variables d'environnement
- Si cela ne fonctionne toujours pas, vérifiez les fautes de frappe et les permissions de fichier

**Problème :** Les changements `.gac.env` au niveau projet ne sont pas pris en compte

- Assurez-vous que votre projet contient un fichier `.gac.env` dans le répertoire racine (à côté de votre dossier `.git`)
- Exécutez `gac --log-level=debug` pour confirmer que la configuration au niveau projet est chargée
- Si vous éditez `.gac.env`, redémarrez votre terminal ou ré-exécutez votre shell pour recharger les variables d'environnement
- Si cela ne fonctionne toujours pas, vérifiez les fautes de frappe et les permissions de fichier

**Problème :** Impossible de définir ou changer la langue des messages de commit

- Exécutez `gac language` (ou `gac lang`) pour sélectionner de manière interactive parmi 25+ langues supportées
- Utilisez le drapeau `-l <langue>` pour remplacer la langue pour un seul commit (ex: `gac -l zh-CN`, `gac -l French`)
- Vérifiez votre configuration avec `gac config show` pour voir le paramètre de langue actuel
- Le paramètre de langue est stocké dans `GAC_LANGUAGE` dans votre fichier `.gac.env`

## 3. Erreurs de fournisseur/API

**Problème :** Erreurs d'authentification ou API

- Assurez-vous d'avoir configuré les clés API correctes pour votre modèle choisi (ex: `ANTHROPIC_API_KEY`, `GROQ_API_KEY`)
- Vérifiez deux fois votre clé API et le statut du compte de votre fournisseur
- Pour Ollama et LM Studio, confirmez que l'URL API correspond à votre instance locale. Les clés API ne sont nécessaires que si vous avez activé l'authentification.

**Problème :** Modèle non disponible ou non supporté

- Streamlake utilise des IDs de point de terminaison d'inférence au lieu de noms de modèle. Assurez-vous de fournir l'ID de point de terminaison de leur console.
- Vérifiez que le nom du modèle est correct et supporté par votre fournisseur
- Vérifiez la documentation du fournisseur pour les modèles disponibles

## 4. Problèmes de regroupement de commits

**Problème :** Le drapeau `--group` ne fonctionne pas comme attendu

- Le drapeau `--group` analyse automatiquement les changements indexés et peut créer plusieurs commits logiques
- L'IA peut décider qu'un seul commit a du sens pour votre ensemble de changements indexés, même avec `--group`
- Ceci est un comportement intentionnel - l'IA groupe les changements basés sur les relations logiques, pas seulement la quantité
- Assurez-vous d'avoir plusieurs changements non liés indexés (ex: correction de bug + ajout de fonctionnalité) pour de meilleurs résultats
- Utilisez `gac --show-prompt` pour déboguer ce que voit l'IA

**Problème :** Commits regroupés incorrectement ou non regroupés quand attendu

- Le regroupement est déterminé par l'analyse de vos changements par l'IA
- L'IA peut créer un seul commit si elle détermine que les changements sont logiquement liés
- Essayez d'ajouter des indices avec `-h "indice"` pour guider la logique de regroupement (ex: `-h "séparer la correction de bug de la refactorisation"`)
- Revoyez les groupes générés avant de confirmer
- Si le regroupement ne fonctionne pas bien pour votre cas d'usage, commitez les changements séparément à la place

## 5. Sécurité et détection de secrets

**Problème :** Faux positif : l'analyse de secrets détecte des non-secrets

- L'analyseur de sécurité recherche des motifs qui ressemblent à des clés API, jetons et mots de passe
- Si vous commitez du code d'exemple, des fixtures de test, ou de la documentation avec des clés de remplacement, vous pouvez voir des faux positifs
- Utilisez `--skip-secret-scan` pour contourner l'analyse si vous êtes certain que les changements sont sûrs
- Envisagez d'exclure les fichiers d'exemple/test des commits, ou utilisez des remplacements clairement marqués

**Problème :** L'analyse de secrets ne détecte pas de vrais secrets

- L'analyseur utilise des motifs et peut ne pas attraper tous les types de secrets
- Revoyez toujours vos changements indexés avec `git diff --staged` avant de commiter
- Envisagez d'utiliser des outils de sécurité supplémentaires comme `git-secrets` ou `gitleaks` pour une protection complète
- Signalez tous les motifs manqués comme des problèmes pour aider à améliorer la détection

**Problème :** Besoin de désactiver l'analyse de secrets de manière permanente

- Définissez `GAC_SKIP_SECRET_SCAN=true` dans votre fichier `.gac.env`
- Utilisez `gac config set GAC_SKIP_SECRET_SCAN true`
- Note : Ne désactivez que si vous avez d'autres mesures de sécurité en place

## 6. Problèmes de hooks Pre-commit et Lefthook

**Problème :** Les hooks pre-commit ou lefthook échouent et bloquent les commits

- Utilisez `gac --no-verify` pour sauter temporairement tous les hooks pre-commit et lefthook
- Corrigez les problèmes sous-jacents causant l'échec des hooks
- Envisagez d'ajuster votre configuration pre-commit ou lefthook si les hooks sont trop stricts

**Problème :** Les hooks pre-commit ou lefthook prennent trop de temps ou interfèrent avec le workflow

- Utilisez `gac --no-verify` pour sauter temporairement tous les hooks pre-commit et lefthook
- Envisagez de configurer les hooks pre-commit dans `.pre-commit-config.yaml` ou les hooks lefthook dans `.lefthook.yml` pour être moins agressifs pour votre workflow
- Revoyez votre configuration de hook pour optimiser les performances

## 7. Problèmes de workflow courants

**Problème :** Aucun changement à commiter / rien d'indexé

- gac nécessite des changements indexés pour générer un message de commit
- Utilisez `git add <fichiers>` pour indexer les changements, ou utilisez `gac -a` pour indexer automatiquement tous les changements
- Vérifiez `git status` pour voir quels fichiers ont été modifiés
- Utilisez `gac diff` pour voir une vue filtrée de vos changements

**Problème :** Le message de commit n'est pas ce que j'attendais

- Utilisez le système de feedback interactif : tapez `r` pour relancer, `e` pour éditer, ou fournissez un feedback en langage naturel
- Ajoutez du contexte avec `-h "votre indice"` pour guider l'IA
- Utilisez `-o` pour des messages plus simples sur une ligne ou `-v` pour des messages plus détaillés
- Utilisez `--show-prompt` pour voir quelles informations l'IA reçoit

**Problème :** gac est trop lent

- Utilisez `gac -y` pour sauter l'invite de confirmation
- Utilisez `gac -q` pour le mode silencieux avec moins de sortie
- Envisagez d'utiliser des modèles plus rapides/bon marché pour les commits de routine
- Utilisez `gac --no-verify` pour sauter les hooks s'ils vous ralentissent

**Problème :** Impossible d'éditer ou de fournir un feedback après la génération du message

- À l'invite, tapez `e` pour entrer en mode édition (supporte les bindings vi/emacs)
- Tapez `r` pour régénérer sans feedback
- Ou tapez simplement votre feedback directement (ex: "rends-le plus court", "concentre-toi sur la correction du bug")
- Appuyez sur Entrée sur une entrée vide pour voir l'invite à nouveau

## 8. Débogage général

- Utilisez `gac init` pour réinitialiser ou mettre à jour votre configuration de manière interactive
- Utilisez `gac --log-level=debug` pour une sortie de débogage détaillée et le logging
- Utilisez `gac --show-prompt` pour voir quel prompt est envoyé à l'IA
- Utilisez `gac --help` pour voir tous les drapeaux de ligne de commande disponibles
- Utilisez `gac config show` pour voir toutes les valeurs de configuration actuelles
- Vérifiez les logs pour les messages d'erreur et les traces de pile
- Vérifiez le [README.md](../README.md) principal pour les fonctionnalités, exemples et instructions de démarrage rapide

## Toujours bloqué ?

- Cherchez les problèmes existants ou ouvrez-en un nouveau sur le [dépôt GitHub](https://github.com/cellwebb/gac)
- Incluez des détails sur votre OS, version Python, version gac, fournisseur, et sortie d'erreur
- Plus vous fournissez de détails, plus votre problème peut être résolu rapidement

## Où obtenir une aide supplémentaire

- Pour les fonctionnalités et exemples d'utilisation, voir le [README.md](../README.md) principal
- Pour les prompts système personnalisés, voir [CUSTOM_SYSTEM_PROMPTS.md](CUSTOM_SYSTEM_PROMPTS.md)
- Pour les directives de contribution, voir [CONTRIBUTING.md](CONTRIBUTING.md)
- Pour les informations de licence, voir [../LICENSE](../LICENSE)
