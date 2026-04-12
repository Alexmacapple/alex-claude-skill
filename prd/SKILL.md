---
name: prd
description: Crée et gère les PRD du workspace avec workflow standardisé
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
argument-hint: "[sujet du PRD]"
context: conversation
---

# Skill : /prd

## Déclencheurs

- "crée un PRD", "nouveau PRD", "/prd"
- "PRD pour [sujet]"

## Seuil de déclenchement

Appliquer ce skill quand la décision :
- Impacte l'architecture, le workflow ou les conventions du workspace
- Nécessite un arbitrage entre 2+ approches
- Sera référencée dans le futur (traçabilité)

Ne PAS appliquer (et documenter pourquoi) quand :
- La modification est purement cosmétique ou triviale
- La décision est déjà couverte par un PRD existant
- Le changement est réversible en < 5 minutes

## Arguments

Le sujet du PRD est passé via `$ARGUMENTS` :
- `/prd Refonte du système de cache` -> `$ARGUMENTS` = "Refonte du système de cache"
- Si `$ARGUMENTS` est vide, demander le sujet à l'utilisateur avant de continuer

## Mode mise à jour

Si `$ARGUMENTS` contient un numéro de PRD existant (ex: `/prd PRD-091`) :

1. Lire le PRD existant
2. Demander à l'utilisateur ce qui doit être modifié
3. Appliquer les modifications
4. Mettre à jour le changelog du PRD (tableau en bas du fichier)
5. Mettre à jour CHANGELOG.MD (racine du workspace)
6. Commit avec message "docs: Mise à jour PRD-{NNN} - {description courte}"

Le mode mise à jour ne touche PAS au BACKLOG.MD (déjà renseigné à la création).

## Hors périmètre

- Review ou évaluation de PRD (utiliser `/skill-review`)
- Gestion des branches Git liées aux PRD

## Invariants (JAMAIS contournables)

- JAMAIS de PRD avec moins de 2 options réellement distinctes évaluées. "Pas d'alternative" n'est PAS une option.
- JAMAIS de PRD sans métriques de succès mesurables (chiffre, seuil ou condition vérifiable).
- JAMAIS de PRD considéré terminé sans mise à jour de BACKLOG.MD ET CHANGELOG.MD ET commit.
- Si une de ces conditions n'est pas remplie : STOP. Informer l'utilisateur et compléter avant de continuer.

## Excuses interdites

Ces rationalisations NE JUSTIFIENT PAS de contourner les invariants :

- "C'est urgent" -> Le PRD prend 5 minutes. L'urgence ne supprime pas les options.
- "C'est trivial / une micro-décision" -> Si c'est trivial, pas besoin de PRD. Mais si on fait un PRD, il est COMPLET.
- "La décision est déjà prise" -> Documenter les options évaluées AVANT la décision, même rétrospectivement.
- "Le contexte est presque plein" -> Les invariants tiennent en 4 lignes. Pas d'excuse.
- "On complétera après" -> Non. Un PRD incomplet n'est pas un PRD.

## Workflow

### Étape 0 : Vérifications préalables

Avant de commencer, vérifier que les fichiers nécessaires existent :
- `prd-meta-workflow/` — si absent, créer le dossier
- `prd-meta-workflow/BACKLOG.MD` — si absent, le signaler et le créer avec un en-tête minimal
- `CHANGELOG.MD` — si absent, le signaler et le créer avec un en-tête minimal

Si le commit échoue à cause du hook pre-commit (capitalisation, accents) : corriger uniquement le problème signalé et relancer.

### Étape 1 : Détection du prochain numéro

Lister les fichiers dans `prd-meta-workflow/` :
- Pattern : `PRD-NNN-*.MD`
- Extraire le numéro le plus élevé
- Incrémenter de 1 pour le nouveau PRD
- Si un numéro est utilisé par plusieurs fichiers (ex: PRD-003 x2), prendre N+1 après le plus haut et avertir l'utilisateur
- Vérifier la cohérence avec `prd-meta-workflow/BACKLOG.MD`

### Étape 2 : Génération du PRD

Créer `prd-meta-workflow/PRD-{NNN}-{slug}.MD` (slug en `kebab-case`, max 40 caractères) avec ce template :

```markdown
# PRD-{NNN} : {Titre}

**Statut** : Brouillon
**Date** : {YYYY-MM-DD}
**Auteur** : Alex
**Source** : {conversation, issue, observation, rapport insights}

---

## Vision

Le quoi : quel pattern ce PRD propose-t-il ?
{Décrire l'idée centrale — ce qui change fondamentalement, pas les détails techniques}

Le pourquoi : pourquoi ce pattern fonctionne-t-il ? (mécanisme, pas slogan)
{Expliquer le mécanisme cognitif ou conceptuel sous-jacent — pourquoi ça marche, pas juste ce que ça fait}

Le comment : renvoyé au Plan d'implémentation — pas dans la Vision.

## Exemple bout-en-bout {(projeté) ou (réel)}

{Un cas d'usage concret en 15-20 lignes : entrée, exécution, sortie. Marquer (projeté) si écrit avant implémentation, (réel) si basé sur une expérience. Mettre à jour en (réel) après implémentation.}

---

## Contexte

{Description du contexte et du problème observé}

---

## Problème

{Énoncé précis du problème à résoudre}

---

## Solution

{Description de la solution proposée}

---

## Options évaluées

### Option A (retenue) : {nom}

**Avantages** :
- ...

**Inconvénients** :
- ...

### Option B : {nom}

**Avantages** :
- ...

**Inconvénients** :
- ...

---

## Décision

{Option retenue et justification}

---

## Plan d'implémentation

1. ...
2. ...

---

## Métriques de succès

- ...

---

## Limites inhérentes au LLM
{Section obligatoire si le PRD produit un skill, un prompt ou un artefact
exécuté par un LLM. Supprimer cette section sinon.}

Lister les limites structurelles du modèle qui affectent la solution :
- Génération vs restitution (le LLM ne sait pas ce qu'il invente)
- Biais de sortie (registre, style, longueur)
- Absence d'ancrage dans des sources vérifiables
- Coût réel (entrée + sortie, pas seulement le prompt)
- {Toute limite spécifique au domaine du PRD}

---

## Changelog

| Date | Auteur | Changement |
|------|--------|------------|
| {date} | Alex + Claude | Creation du PRD |
```

### Étape 3 : Validation croisée (optionnelle)

Si l'utilisateur demande une validation, proposer :
- `/connu-inconnu` sur le PRD — cartographie des angles morts
- `/avocat-du-diable` sur le PRD — revue critique structurée
- `/council` ou `/synthese-multi-llm` — délibération multi-modèle

Les deux premiers peuvent être lancés en parallèle.
Intégrer les retours dans le PRD avant de passer à l'étape suivante.

### Étape 3bis : Introspection LLM (conditionnelle)

Si le PRD produit un skill, un prompt ou un artefact exécuté par un LLM :
1. Poser la question : « En tant que LLM qui va implémenter ce PRD, qu'est-ce qui te manque ? »
2. Intégrer les réponses comme section « Spécifications d'implémentation » dans le PRD
3. Points typiques : prompts adaptés, grille de scoring, mécanique d'interaction, gestion du contexte, critères d'arrêt, fallbacks

Cette étape fait le pont entre le quoi/pourquoi (PRD) et le comment (SKILL.md). Elle force la transparence sur les limites opérationnelles du modèle avant l'implémentation.

**Déclencheur** : le PRD mentionne « skill », « prompt », « SKILL.md » ou « concept incarné » dans sa Solution.

### Étape 4 : Mise à jour des documents

- Ajouter une entrée dans `prd-meta-workflow/BACKLOG.MD` (index des PRD)
- Ajouter une entrée dans `CHANGELOG.MD` (racine du workspace)

### Étape 5 : Commit

- `git add` du PRD + BACKLOG + CHANGELOG
- Message : "docs: Création PRD-{NNN} - {titre court}"

## Exemples d'utilisation

```text
Utilisateur : /prd Systeme de notifications push

Claude :
> Détection du prochain numéro... PRD-008
> Génération du PRD en cours...
> Fichier créé : prd-meta-workflow/PRD-008-notifications-push.MD
> BACKLOG.MD mis à jour
> CHANGELOG.MD mis à jour
> Commit : "docs: Création PRD-008 - Notifications push"
```

```text
Utilisateur : /prd

Claude :
> Aucun sujet spécifié. Quel est le sujet du PRD ?

Utilisateur : Optimisation des requêtes base de données

Claude :
> Détection du prochain numéro... PRD-009
> Génération du PRD en cours...
> Fichier créé : prd-meta-workflow/PRD-009-optimisation-requetes-bdd.MD
> Validation croisée ? (optionnel) [oui/non]
```

## Conditions de complétion (TOUTES obligatoires)

Le skill est terminé UNIQUEMENT quand TOUTES ces conditions sont vérifiées :
- [ ] Numéro PRD correct (pas de doublon) — vérifié par `ls prd-meta-workflow/PRD-*`
- [ ] TOUTES les sections du template présentes et remplies (pas de placeholder)
- [ ] Section Vision remplie (idée centrale + pourquoi ça marche)
- [ ] Section Exemple bout-en-bout présente (marquée projeté ou réel)
- [ ] Au moins 2 options réellement distinctes évaluées avec avantages ET inconvénients
- [ ] Plan d'implémentation avec étapes numérotées (pas "à définir")
- [ ] Métriques de succès mesurables (chiffre ou condition vérifiable, pas "améliorer X")
- [ ] Si PRD skill/prompt/artefact LLM : section « Limites inhérentes au LLM » présente et remplie
- [ ] Si PRD skill/prompt/artefact LLM : étape 3bis « Introspection LLM » proposée à l'utilisateur
- [ ] BACKLOG.MD mis à jour — vérifié par `git diff prd-meta-workflow/BACKLOG.MD`
- [ ] CHANGELOG.MD mis à jour — vérifié par `git diff CHANGELOG.MD`
- [ ] Commit effectué — vérifié par `git log -1`

Si une condition échoue : corriger AVANT de signaler la fin du skill.
