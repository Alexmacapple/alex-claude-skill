---
name: claude-code-veille
description: "Veille, reference et migration Claude Code. 3 modes : veille, reference, migration. Utiliser quand l'utilisateur demande les nouveautes Claude Code, veut documenter une fonctionnalite ou prepare une mise a jour. Pas pour /help ou /doctor."
allowed-tools: "Bash, Read, Write, Glob, Grep, WebFetch"
argument-hint: "[veille|reference <sujet>|migration] [--output fichier.md]"
context: conversation
---

# Skill : /claude-code-veille

Veille technologique, documentation de référence et migration pour Claude Code. Analyse le changelog officiel, compare avec la version installée et le workflow en place.

---

## Déclencheurs

- `/claude-code-veille` → mode veille (défaut)
- `/claude-code-veille reference <sujet>` → documentation d'une fonctionnalité
- `/claude-code-veille migration` → détection des breaking changes
- "Quoi de neuf dans Claude Code ?"
- "Documente la fonctionnalité X de Claude Code"
- "Est-ce que ma config est compatible avec la dernière version ?"

---

## Mode 1 : veille (défaut)

Analyse les nouveautés de Claude Code et filtre ce qui est pertinent pour le workflow.

### Workflow

#### Étape 1 : collecte

1. Récupérer la version installée :
   ```bash
   claude --version
   ```
2. Fetcher le changelog depuis GitHub :
   ```bash
   gh api repos/anthropics/claude-code/contents/CHANGELOG.md --jq '.content' | base64 -d
   ```
3. Si `gh` échoue, utiliser WebFetch sur `https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md`

#### Étape 2 : analyse

1. Extraire les versions plus récentes que la version installée
2. Classer chaque changement par pertinence pour le workflow :

Voir `references/categories-pertinence.md` pour la grille complète de filtrage par catégorie.

#### Étape 3 : rapport

Écrire le rapport dans `veille/veille-claude-code-YYYY-MM-DD.md` :

```markdown
# Veille Claude Code — YYYY-MM-DD

**Version installée** : X.Y.Z
**Dernière version** : X.Y.Z
**Statut** : à jour | X versions de retard

## Nouveautés pertinentes pour ton workflow

### [fonctionnalité]
- **Ce que c'est** : description
- **Impact** : comment ça affecte ton workflow
- **Action recommandée** : ce qu'il faut faire (ou rien)

## Corrections de bugs qui te concernent

- [description] (version X.Y.Z)

## Autres changements (résumé)

- X corrections de bugs Windows/PowerShell (non pertinent)
- X améliorations internes
```

---

## Mode 2 : référence

Documente une fonctionnalité spécifique de Claude Code.

### Sujets disponibles

Voir `references/sujets-disponibles.md` pour la liste complète des sujets et fiches existantes.

### Workflow

#### Étape 1 : identification

1. Extraire le sujet de `$ARGUMENTS` (mot après "reference")
2. Si pas de sujet, demander via la conversation

#### Étape 2 : recherche

1. Chercher dans `fiches/` si une fiche existe déjà :
   ```
   Glob("fiches/*{sujet}*")
   ```
2. Si fiche trouvée : la lire et vérifier si elle est à jour par rapport au changelog
3. Si pas de fiche : chercher dans le changelog + code source fuité

#### Étape 3 : production

1. Si fiche existante et à jour : l'afficher et confirmer
2. Si fiche existante mais obsolète : proposer une mise à jour
3. Si pas de fiche : créer `veille/reference-{sujet}.md` avec cette structure :

```markdown
# Référence : {sujet}

Description courte de la fonctionnalité.

## Ce que c'est

Explication du fonctionnement.

## Configuration

Comment activer/configurer (fichier, commande, variable).

## Usage courant

Exemples concrets d'utilisation dans le workflow.

## Limitations

Ce que ça ne fait pas, cas limites connus.

*Source : changelog vX.Y.Z, code source fuité*
```

---

## Mode 3 : migration

Détecte les breaking changes et leur impact sur le workflow.

### Workflow

#### Étape 1 : collecte

1. Version installée (`claude --version`)
2. Changelog GitHub (même méthode que mode veille)
3. Lire la configuration actuelle :
   ```
   Read .claude/settings.json          → hooks et permissions
   Bash grep CLAUDE_CODE ~/.zshrc      → variables d'environnement
   Read CLAUDE.md                      → conventions
   Glob .claude/rules/*.md             → règles actives
   ```

#### Étape 2 : détection

1. Extraire les lignes commençant par "Changed", "Removed", "Deprecated" depuis la dernière version
2. Pour chaque changement, vérifier l'impact :
   - Hook modifié ? → vérifier settings.json
   - Variable supprimée ? → vérifier ~/.zshrc
   - Commande renommée ? → vérifier CLAUDE.md et rules
   - Permission changée ? → vérifier settings.json
   - Comportement par défaut modifié ? → signaler

#### Étape 3 : rapport

Écrire dans `veille/migration-YYYY-MM-DD.md` :

```markdown
# Migration Claude Code — YYYY-MM-DD

**De** : version X.Y.Z → **Vers** : version X.Y.Z

## Breaking changes

### [changement]
- **Ce qui change** : description
- **Impact sur ton workflow** : fichier ou config concerné
- **Action** : ce qu'il faut modifier

## Changements de comportement par défaut

### [changement]
- **Avant** : comportement précédent
- **Maintenant** : nouveau comportement
- **Action** : adapter ou ignorer

## Aucune action requise

- [liste des changements sans impact]
```

---

## Règles

- **TOUJOURS** vérifier la version installée avant d'analyser le changelog
- **TOUJOURS** filtrer par pertinence — ne pas lister 50 corrections de bugs Windows
- **TOUJOURS** proposer des actions concrètes (pas juste "à surveiller")
- **TOUJOURS** écrire le rapport dans un fichier (pas dans le chat si > 30 lignes)
- **JAMAIS** inventer des fonctionnalités non présentes dans le changelog
- **JAMAIS** recommander une action sans vérifier l'impact sur la config existante

---

## Gestion d'erreurs

| Situation | Comportement |
|-----------|-------------|
| `gh` non disponible | Fallback WebFetch sur raw.githubusercontent.com |
| Changelog inaccessible | Message d'erreur, proposer de vérifier la connexion |
| Version non trouvée dans le changelog | Indiquer la version la plus proche |
| Sujet de référence inconnu | Lister les sujets disponibles |
| Aucun breaking change | Rapport positif ("aucune action requise") |
| Plus de 5 versions de retard | Résumer les changements par version, recommander une migration progressive, lancer `/claude-code-veille migration` en priorité |
| Changelog très long (> 1000 lignes) | Ne traiter que les versions depuis la version installée, ignorer l'historique antérieur |
| Aucun argument (`$ARGUMENTS` vide) | Mode veille par défaut |
| Répertoire de fiches introuvable (`fiches/`) | Chercher dans `veille/` en fallback, signaler le répertoire manquant |

---

## Exemples d'utilisation

```
/claude-code-veille
```
> Version installée : 2.1.89
> Dernière version : 2.1.89
> Statut : à jour — 9 nouveautés pertinentes identifiées
> Rapport écrit dans veille/veille-claude-code-2026-04-01.md

```
/claude-code-veille reference hooks
```
> Fiche existante trouvée : fiches/guide-13-hooks-claude-code.md
> Vérification par rapport au changelog... 2 nouveautés manquantes
> Mise à jour proposée

```
/claude-code-veille reference buddy
```
> Aucune fiche existante pour "buddy"
> Création de veille/reference-buddy.md (45 lignes)

```
/claude-code-veille migration
```
> De : 2.1.86 → Vers : 2.1.89
> 1 breaking change détecté (thinking summaries désactivés)
> 0 variables supprimées
> Rapport écrit dans veille/migration-2026-04-01.md

---

## Checklist finale

- [ ] La version installée est correctement détectée
- [ ] Le changelog est fetché et parsé
- [ ] Les changements sont filtrés par pertinence
- [ ] Le rapport est écrit dans un fichier (pas dans le chat)
- [ ] Les actions recommandées sont concrètes et vérifiables
- [ ] Les fiches existantes sont référencées quand elles existent
