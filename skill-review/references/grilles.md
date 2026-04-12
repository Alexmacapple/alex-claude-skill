# Grilles de notation — /skill-review

## PRD (score /100)

| Critère | Points |
|---------|--------|
| Structure conforme au template | 20 |
| Problème clairement énoncé | 15 |
| Au moins 2 options évaluées | 15 |
| Décision justifiée | 15 |
| Plan d'implémentation numéroté | 15 |
| Métriques de succès mesurables | 10 |
| Changelog présent | 10 |

## Skill (score /100)

| Critère | Points |
|---------|--------|
| Frontmatter complet | 10 |
| Déclencheurs clairs | 10 |
| Workflow en étapes | 15 |
| Contraintes documentées | 10 |
| Checklist finale | 5 |
| Cohérence avec GUIDELINES | 10 |
| **Conformité Anthropic (Q01-Q07)** | **40** |

### Grille conformité Anthropic (40 pts)

Critères sémantiques issus du guide officiel "The Complete Guide to Building Skills for Claude" (janvier 2026). Référence complète : `.claude/skills/skill-conformity-checker/references/criteres-conformite.md`.

| ID | Critère | Points |
|----|---------|--------|
| Q01 | Description combine quoi + quand avec phrases concrètes | /8 |
| Q02 | Gestion d'erreurs documentée (scénarios, fallbacks) | /6 |
| Q03 | Contraintes impératives présentes (JAMAIS/TOUJOURS) | /6 |
| Q04 | Exemples d'utilisation concrets (input -> output) | /6 |
| Q05 | Divulgation progressive respectée (SKILL.md lean) | /5 |
| Q06 | Cohérence instructions / structure | /5 |
| Q07 | Conventions respectées (langue, nommage, pas d'emojis) | /4 |

### Grille densité sémantique (bonus diagnostique)

Axes transversaux pour évaluer la qualité du skill en tant que spécification pour un LLM. Ne modifie pas le score /100 — sert de diagnostic complémentaire pour les prescriptions.

| Axe | Question directrice |
|-----|---------------------|
| **Pertinence** | Chaque instruction guide-t-elle réellement le comportement du LLM ? |
| **Densité** | Y a-t-il du remplissage supprimable sans perte ? |
| **Exhaustivité** | Les cas limites sont-ils couverts ? |
| **Cohérence** | Les contraintes et le workflow se contredisent-ils ? |
| **Opérabilité** | Un LLM sans contexte additionnel peut-il exécuter ce skill ? |

Utiliser ces axes pour identifier les faiblesses qualitatives et formuler des prescriptions concrètes (voir contraintes anti-hedging dans SKILL.md).

### Grille SkillsBench (bonus diagnostique, PRD-092)

Axes empiriques issus de SkillsBench (arXiv:2602.12670v1, février 2026). Cette grille produit des **prescriptions orientées action**, pas des points ajoutés au score /100. Son rôle est d'aider l'auteur du skill à se poser les bonnes questions stratégiques sur le ciblage et la composabilité.

| Axe | Question directrice | Finding source | Signaux |
|-----|---------------------|----------------|---------|
| **Domaine** | Le skill cible-t-il un domaine peu représenté en pré-entraînement des LLMs ? | Finding 4 (+51,9 pp Healthcare vs +4,5 pp Software Eng) | Zone rouge : code Python générique, git, format standard. Zone verte : réglementation locale, format métier propriétaire, spec récente peu indexée |
| **Focalisation** | Le skill résout-il une classe unique de tâches ou plusieurs classes mélangées ? | Finding 5 (2-3 modules optimal, 4+ rendement décroissant) | Zone rouge : skill qui couvre 4+ cas d'usage hétérogènes. Zone verte : skill mono-classe composable avec d'autres |
| **Composabilité** | Le skill peut-il coexister avec 2 autres skills sans guidance conflictuelle ? | Finding 5 (surcharge cognitive au-delà de 3 skills chargés) | Zone rouge : skill qui réécrit les règles de base (formatage, git). Zone verte : skill qui complète sans contredire |

**Mode d'emploi** : pour chaque axe, produire une ligne de prescription dans le rapport avec ce format :

```
[Domaine] : <verte|orange|rouge> — <justification d'une phrase> — <action recommandée>
```

Exemples attendus :

```
[Domaine]       : verte — spec RGAA 4.1.2 peu couverte en pré-entraînement — garder tel quel, gain estimé > 30 pp
[Focalisation]  : orange — le skill couvre à la fois audit RGAA et remédiation — envisager de scinder en /audit-rgaa et /fix-rgaa
[Composabilité] : verte — compatible avec /accessible-pdf et /audit-a11y-complet — rien à changer
```

**Quand cette grille déclenche une action** : si un axe passe en rouge, proposer une refonte ciblée (scission, recentrage, abandon) avant la mise en production. Ne pas bloquer le verdict /100, mais inclure la recommandation en section « Actions correctives » du rapport avec priorité haute.

**Référence** : SkillsBench `guidelines-skills.md` Partie V (auto-audit) pour la checklist complète.

Note : pour la validation structurelle déterministe (frontmatter, nommage, liens, critères empiriques SkillsBench S16-S20), utiliser `/skill-conformity-checker`. Score max depuis PRD-092 : 65 pts (50 Anthropic + 15 SkillsBench).

## Rule (score /100)

| Critère | Points |
|---------|--------|
| Format BON/MAUVAIS avec exemples | 25 |
| Pertinence des patterns | 25 |
| Portée définie (paths) ou activation permanente justifiée | 20 |
| Concision (< 100 lignes) | 15 |
| Cohérence interne | 15 |
