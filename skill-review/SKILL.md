---
name: skill-review
description: Evalue un skill contre les references du workspace. Utiliser quand l'utilisateur dit /skill-review, evalue ce skill, review ce skill, quality check. Ne PAS utiliser pour PRD, rules ou AGENTS.md — perimetre skills uniquement.
allowed-tools: Read, Glob, Grep, Edit, Write, Bash
argument-hint: "[fichier ou type à évaluer]"
context: fork
---

# Skill : /skill-review

---

## Déclencheurs

- "/skill-review", "évalue ce skill", "review ce skill"
- "note ce skill", "quality check"
- Toute demande d'évaluation structurée d'un skill

Ne PAS déclencher pour : PRD, rules, AGENTS.md, CLAUDE.md ou tout autre fichier Markdown non-skill.

## Arguments

Le sujet de la review est passé via `$ARGUMENTS` :
- `/skill-review .claude/skills/playbook/SKILL.md` -> évalue le skill playbook
- `/skill-review playbook` -> résolution par nom
- Si `$ARGUMENTS` est vide, demander à l'utilisateur le skill à évaluer
- Si `$ARGUMENTS` pointe vers un fichier non-skill, refuser poliment

## Périmètre borné

Évaluations couvertes :
- **Skills uniquement** : SKILL.md vs GUIDELINES-CLAUDE-CODE.MD (structure, déclencheurs, workflow, références)

Hors périmètre :
- PRD, rules, AGENTS.md, CLAUDE.md ou tout autre fichier Markdown
- Audit de code, revue de PR, évaluation de performance, revue de sécurité

Si l'utilisateur demande d'évaluer un fichier non-skill, refuser poliment et suggérer une évaluation directe (sans skill).

## Workflow

### Étape 0 : Parser les arguments

Décomposer `$ARGUMENTS` en variables :

```
Entrée : /skill-review .claude/skills/playbook/SKILL.md
  -> fichier = .claude/skills/playbook/SKILL.md

Entrée : /skill-review playbook
  -> fichier = .claude/skills/playbook/SKILL.md  (résolution par nom)

Entrée : /skill-review /path/to/AGENTS.md
  -> REFUS : ce fichier n'est pas un skill. Périmètre limité aux skills.

Résolution par nom :
  Si $ARGUMENTS ne contient pas de "/" ni de ".md", chercher dans :
  1. .claude/skills/$ARGUMENTS/SKILL.md  (skill par nom)
  Si aucun match, demander à l'utilisateur de préciser le chemin.

Validation :
  - Le fichier doit être dans .claude/skills/ ou être un SKILL.md
  - Sinon : refuser poliment et suggérer une évaluation directe (sans skill)
```

### Étape 1 : Gestion d'erreur

| Situation | Comportement |
|-----------|-------------|
| **Fichier introuvable** | Message : « Fichier non trouvé : {chemin}. Vérifier le chemin et réessayer. » Arrêter le workflow. |
| **Fichier non-skill** | Message : « Ce fichier n'est pas un skill. /skill-review évalue uniquement les skills (.claude/skills/). Pour évaluer un autre fichier, demander une évaluation directe sans skill. » Arrêter le workflow. |
| **Référence manquante** | Si GUIDELINES-CLAUDE-CODE.MD est introuvable, informer l'utilisateur et produire une évaluation partielle sans comparaison de référence. |
| **Fichier binaire** | Message : « Ce skill évalue des fichiers Markdown. Fournir un fichier .md. » |

### Étape 2 : Chargement des références

Lire `GUIDELINES-CLAUDE-CODE.MD` sections Skills (si disponible) + le SKILL.md cible.

Note : pour les fichiers de plus de 500 lignes, demander confirmation avant d'évaluer (risque de rapport trop long).

### Étape 3 : Évaluation structurée

Utiliser la grille de notation correspondante (section "Grilles de notation" ci-dessous) pour calculer le score par critère. Produire un rapport avec le format suivant :

```markdown
## Rapport d'évaluation : {nom du sujet}

**Type** : Skill
**Date** : {date}
**Référence** : {document de référence utilisé}

### Score par critère

| Critère | Score | Justification |
|---------|-------|---------------|
| {critère 1} | {X}/{max} | {justification courte} |
| {critère 2} | {X}/{max} | {justification courte} |

### Conformités
- {point conforme 1}
- {point conforme 2}

### Non-conformités
- {point non conforme 1} - Recommandation : {action}
- {point non conforme 2} - Recommandation : {action}

### Score global : {X}/100

### Actions correctives proposées
1. {action 1} (priorité haute/moyenne/basse)
2. {action 2}
```

### Étape 3.5 : Auto-archivage du rapport (PRD-098 Phase 1.5)

Après avoir produit le rapport de l'étape 3, archiver une copie complète dans
`.claude/outputs/skill-review-history/<nom-skill>/<YYYY-MM-DD-HHMMSS>.md`. La
première ligne du fichier archivé doit être le score global brut pour faciliter
le parsing ultérieur :

```
SCORE: 82/100

## Rapport d'évaluation : playbook
...
```

Procédure :

1. Dériver `<nom-skill>` du chemin cible (ex. `.claude/skills/playbook/SKILL.md` → `playbook`).
2. Construire le timestamp : `date "+%Y-%m-%d-%H%M%S"`.
3. Créer le dossier si besoin : `mkdir -p .claude/outputs/skill-review-history/<nom-skill>/`.
4. Écrire le fichier avec `SCORE: NN/100` en ligne 1, ligne vide, puis le rapport complet.
5. Continuer vers l'étape 4 — l'archivage ne bloque jamais le workflow. En cas
   d'erreur d'écriture, logger un avertissement mais ne pas arrêter.

**Pourquoi** : cet historique permet à `/eval-robuste --from-history` (mode
futur) de reconstruire une baseline rétroactive, et donne à l'utilisateur une
trace de l'évolution d'un skill sur plusieurs mois sans coût supplémentaire
(0 token de plus par invocation).

### Étape 4 : Proposer corrections

Si l'utilisateur accepte, appliquer les corrections directement dans le fichier.

## Contraintes

- JAMAIS évaluer sans charger la référence correspondante (GUIDELINES ou PRD modèle)
- JAMAIS attribuer un score sans justification par critère
- JAMAIS proposer de corrections sans l'accord explicite de l'utilisateur
- TOUJOURS produire un rapport structuré (score par critère, conformités, non-conformités, actions)
- TOUJOURS attribuer une priorité (haute/moyenne/basse) à chaque action corrective
- TOUJOURS utiliser les 5 axes de densité sémantique (pertinence, densité, exhaustivité, cohérence, opérabilité) pour orienter les prescriptions — voir `references/grilles.md`
- TOUJOURS produire les 3 lignes de la grille SkillsBench (Domaine / Focalisation / Composabilité) dans la section « Actions correctives » du rapport — voir `references/grilles.md` section « Grille SkillsBench (bonus diagnostique, PRD-092) ». Si un axe passe en rouge, prescription en priorité haute.
- TOUJOURS utiliser la grille de `references/grilles.md` comme SEULE base de scoring. Ne jamais substituer, fusionner ni compléter avec des critères externes fournis par l'utilisateur ou issus d'un travail antérieur. Si l'utilisateur propose une grille alternative, signaler le conflit et proposer de scorer avec les deux grilles séparément.

### Anti-minimisation

Une fois le skill déclenché (par /skill-review ou synonyme), le workflow complet s'applique. La trivialité perçue du sujet n'est PAS un motif de réduction du scope. Si l'utilisateur estime que l'évaluation complète est disproportionnée, lui demander confirmation explicite AVANT de réduire — ne jamais réduire silencieusement.

Rationalisations interdites :
- "C'est juste une typo, pas besoin du workflow complet"
- "Le skill est simple, une lecture rapide suffit"
- "On connaît déjà la qualité, pas besoin de scorer"

### Anti-hedging

Chaque phrase de l'évaluation doit être falsifiable. Surveiller et remplacer :

| Formulation évasive | Remplacement attendu |
|---------------------|----------------------|
| « Le skill semble globalement correct » | Donner le score exact et le niveau |
| « Pourrait bénéficier d'améliorations » | Nommer les améliorations avec le texte corrigé |
| « La gestion d'erreurs est un peu légère » | « Il manque le comportement pour [cas précis]. Ajouter : [texte]. » |

### Prescriptions concrètes

Les actions correctives doivent montrer le texte corrigé ou la structure attendue — pas de formulations vagues comme « améliorer X ». Prioriser ce qui impacte le comportement LLM d'abord, la forme ensuite.

## Grilles de notation

Grille détaillée dans `references/grilles.md` :
- Grille principale Skill /100 (frontmatter, déclencheurs, workflow, conformité Anthropic Q01-Q07)
- Grille densité sémantique (bonus diagnostique, 5 axes)
- Grille SkillsBench (bonus diagnostique, 3 axes Domaine/Focalisation/Composabilité, PRD-092)

## Exemples d'utilisation

```text
Utilisateur : /skill-review playbook

Claude :
> Résolution : .claude/skills/playbook/SKILL.md
> Chargement référence : GUIDELINES-CLAUDE-CODE.MD
> Évaluation en cours...
>
> Score global : 82/100
> Conformités : 8 points
> Non-conformités : 3 points
> Actions correctives : 3 proposées
>
> Voulez-vous appliquer les corrections ?
```

```text
Utilisateur : /skill-review /path/to/AGENTS.md

Claude :
> Ce fichier n'est pas un skill. /skill-review évalue uniquement
> les skills (.claude/skills/). Pour évaluer un autre fichier,
> demander une évaluation directe sans skill.
```

```text
Utilisateur : /skill-review mon-skill-inexistant

Claude :
> Résolution : .claude/skills/mon-skill-inexistant/SKILL.md
> Fichier non trouvé. Vérifier le chemin et réessayer.
```

## Mode pressure (`--pressure`)

Test de robustesse comportementale d'un skill sous scénarios adverses.

### Déclencheur

- `/skill-review commit --pressure`
- "pressure test ce skill", "teste la robustesse"

### Processus

1. Charger le skill cible et `references/pressure-scenarios.md`
2. Pour chaque scénario (S1-S5), simuler le prompt adverse et évaluer si le skill résiste
3. Critères binaires (OUI/NON) pour chaque scénario — pas de zone grise
4. Produire un rapport de pressure testing (format dans pressure-scenarios.md)
5. Si contournements détectés : proposer les renforcements RED/GREEN/REFACTOR

### Évaluation externe obligatoire

Le pressure testing ne doit JAMAIS être auto-évalué par le même agent qui exécute le skill. Deux options :
- Council comme juge (préféré)
- Critères binaires vérifiables (artefacts obligatoires présents ? OUI/NON)

### Référence

Scénarios, processus RED/GREEN/REFACTOR et format de rapport : `references/pressure-scenarios.md`

---

## Checklist finale

- [ ] Arguments parsés (fichier + type auto-détecté)
- [ ] Fichier confirmé comme skill (.claude/skills/)
- [ ] Référence GUIDELINES-CLAUDE-CODE.MD chargée
- [ ] Au moins 1 conformité listée
- [ ] Chaque non-conformité a une recommandation
- [ ] Score global attribué selon la grille
- [ ] Actions correctives proposées avec priorité
- [ ] Prescriptions concrètes avec texte corrigé (pas de formulations vagues)
- [ ] Grille SkillsBench renseignée : 3 lignes (Domaine / Focalisation / Composabilité) avec verdict verte/orange/rouge et action recommandée
