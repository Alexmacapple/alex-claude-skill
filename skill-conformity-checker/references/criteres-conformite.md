# Critères de conformité Anthropic + SkillsBench — Référence

Sources :
- "The Complete Guide to Building Skills for Claude" (Anthropic, janvier 2026)
- SkillsBench benchmark empirique (arXiv:2602.12670v1, Li et al., février 2026)

Codification : council multi-LLM (session partir-de-la-fiche-oprationnelle-0216-1106) + intégration PRD-092 (avril 2026).

## Grille de scoring (65 points, déterministe)

### Critères structurels Anthropic (S01-S15, 50 pts)

| ID | Critère | Points | Sévérité | Méthode |
|----|---------|--------|----------|---------|
| S01 | Frontmatter YAML avec délimiteurs `---` | 3 | Critique | Regex |
| S02 | Champ `name` présent, kebab-case | 5 | Critique | Regex + YAML |
| S03 | Champ `description` présent, < 1024 car. | 4 | Critique | YAML + len |
| S04 | Description inclut des conditions de déclenchement | 2 | Majeur | Regex patterns |
| S05 | Pas de chevrons XML dans le frontmatter | 2 | Critique | Regex |
| S06 | Pas de nom réservé (claude/anthropic) | 2 | Critique | String match |
| S07 | Fichier nommé exactement SKILL.md | 3 | Critique | Filesystem |
| S08 | Dossier en kebab-case | 3 | Majeur | Regex |
| S09 | Pas de README.md dans le dossier | 4 | Majeur | Filesystem |
| S10 | Titre H1 unique | 3 | Majeur | Regex |
| S11 | Au moins 2 sections H2 | 5 | Majeur | Regex |
| S12 | Corps > 20 lignes et < 500 lignes (plafond dur) | 4 | Mineur | Line count |
| S13 | Au moins 1 bloc de code / exemple | 4 | Mineur | Regex |
| S14 | Liens relatifs valides (pas de liens cassés) | 4 | Majeur | Filesystem |
| S15 | Name == nom du dossier | 2 | Mineur | String match |
| **Sous-total Anthropic** | | **50** | | |

### Critères empiriques SkillsBench (S16-S20, 15 pts)

Ajoutés par PRD-092 pour intégrer les findings empiriques de SkillsBench. Ces critères durcissent la qualité sans casser la compatibilité avec les skills existants (scoring proportionnel).

| ID | Critère | Points | Sévérité | Méthode | Finding source |
|----|---------|--------|----------|---------|---------------|
| S16 | Corps ≤ 300 lignes (cible empirique, complète S12) | 3 | Mineur | Line count | Finding 6 (longueur modérée) |
| S17 | Section `Checklist` présente ET ≥ 2 items `- [ ]` | 3 | Majeur | Regex titre + count | Réduction Incomplete Solution (10,2 %) |
| S18 | Section `Pièges` / `Pitfalls` / `Conventions` présente | 2 | Mineur | Regex titre | Réduction Quality Below Threshold (49,8 %) |
| S19 | Guidance négative (`NE PAS` / `JAMAIS` / `Do NOT` / `hors périmètre`) ≥ 1 | 3 | Majeur | Regex count | Réduction Specification Violation (3,3 %) |
| S20 | Section `Exemple` présente ET ≥ 1 bloc de code ` ``` ` | 4 | Majeur | Regex titre + blocs | Discussion §5 (exemples > doc exhaustive) |
| **Sous-total SkillsBench** | | **15** | | | |
| **Total général** | | **65** | | | |

**Arbitrage S12 vs S16** : S12 reste à < 500 lignes comme **plafond dur** (au-delà = déduction). S16 ajoute la **cible empirique à 300 lignes** avec déduction légère entre 301 et 400, et déduction totale au-dessus de 400. Un skill peut donc légitimement vivre à 350 lignes (S12 : 4/4, S16 : 1/3) sans être disqualifié.

## Seuils de conformité

Seuils proportionnels (ex-/50 × 1,3 = /65) :

| Score | Verdict | Action |
|-------|---------|--------|
| 58-65 | Conforme | Prêt pour production |
| 45-57 | Acceptable | Corrections mineures recommandées |
| 32-44 | Non conforme | Corrections requises avant utilisation |
| < 32 | Rejet | Refonte nécessaire |

## Sévérités

| Sévérité | Impact | Exemple |
|----------|--------|---------|
| Critique | Échec immédiat si non corrigé | Frontmatter absent, nom réservé |
| Majeur | Dégrade fortement la qualité | Description sans triggers, pas d'exemples |
| Mineur | Amélioration recommandée | Corps trop long, conventions de style |
| Info | Observation sans impact | Pas de liens relatifs |

## Évaluation sémantique

Les critères sémantiques (qualité de la description, gestion d'erreurs, exemples, cohérence) sont évalués par le skill `/skill-review` via sa grille "Conformité Anthropic". Ce fichier ne couvre que la partie structurelle déterministe.

## Source de calibration

Les SKILL.md existants du workspace .claude/skills/ servent de corpus de référence.
Pas de jeu de test artificiel — calibration sur le réel.

## Versionnement

Ce fichier de critères est versionné. Chaque rapport doit indiquer la version utilisée.

| Version | Date | Changements |
|---------|------|-------------|
| 2.0.0 | 2026-02-16 | Version initiale : 15 critères Anthropic (S01-S15), score /50 |
| 3.0.0 | 2026-04-10 | PRD-092 : +5 critères SkillsBench (S16-S20), score /65, seuils proportionnels |

Version actuelle : 3.0.0 (2026-04-10)
