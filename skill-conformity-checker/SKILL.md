---
name: skill-conformity-checker
description: Valide la conformite structurelle d'un SKILL.md (standards Anthropic, score /50, deterministe). Utiliser quand l'utilisateur dit "verifie ce skill" ou "check skill". Pour l'evaluation semantique, utiliser /skill-review.
allowed-tools: Bash, Read, Glob
argument-hint: "[skill à auditer]"
disable-model-invocation: true
---

# Skill : /skill-conformity-checker

Validation structurelle des skills Claude selon les standards Anthropic. Score sur 50 points, 100% déterministe et reproductible (±0 entre deux exécutions).

## Déclencheurs

- "/skill-conformity-checker", "vérifie ce skill", "check skill"
- "audit de conformité", "ce skill est-il conforme"
- Toute demande de validation structurelle d'un SKILL.md avant publication

## Workflow

Le processus suit 3 phases séquentielles :

1. Collecter le chemin du skill à auditer
2. Exécuter la validation structurelle (script Python)
3. Produire le rapport

### Phase 1 : Identification du skill

Déterminer le chemin via `$ARGUMENTS` ou interaction :

```
Entrée : /skill-conformity-checker .claude/skills/pdf/SKILL.md
  -> chemin = .claude/skills/pdf/SKILL.md

Entrée : /skill-conformity-checker pdf
  -> chemin = .claude/skills/pdf/SKILL.md  (résolution par nom)

Résolution par nom :
  Si $ARGUMENTS ne contient pas de "/" ni de ".md", chercher dans :
  .claude/skills/$ARGUMENTS/SKILL.md
  Si aucun match, demander à l'utilisateur de préciser le chemin.
```

- Si l'utilisateur fournit un chemin : l'utiliser directement
- Si l'utilisateur nomme un skill : chercher dans `.claude/skills/{nom}/SKILL.md`
- Si aucun chemin : demander à l'utilisateur

### Phase 2 : Validation structurelle (50 pts)

Exécuter le script de validation programmatique :

```bash
python3 scripts/check_structure.py <chemin-du-skill> --json
```

Le script vérifie 15 critères déterministes (frontmatter, structure, ressources) et produit un score sur 50. Le résultat est 100% reproductible entre deux exécutions.

Consulter `references/criteres-conformite.md` pour le détail des critères S01-S15.

### Phase 3 : Rapport

Produire le rapport au format suivant :

```
## Score structurel : XX/50

## Verdict : [Conforme|Acceptable|Non conforme|Rejet]

## Points conformes
- [liste des critères OK]

## Violations
| Sévérité | ID | Critère | Score | Action corrective |
|----------|----|---------|-------|-------------------|
| CRITIQUE | Sxx | ... | 0/N | ... |
| MAJEUR   | Sxx | ... | X/N | ... |

## Actions correctives prioritaires
1. [action la plus urgente]
2. [action suivante]

Version des critères : 2.0.0

Note : pour une évaluation sémantique (qualité de la description,
exemples, cohérence), utiliser /skill-review.
```

## Gestion des erreurs

| Scénario | Comportement |
|----------|-------------|
| Script `check_structure.py` introuvable | Signaler l'erreur et indiquer le chemin attendu (`scripts/check_structure.py`) |
| Fichier SKILL.md absent dans le dossier | Le script retourne exit code 2 — signaler l'absence et arrêter l'audit |
| Frontmatter YAML invalide (syntaxe cassée) | Le script détecte l'erreur — afficher le message YAML et continuer avec score frontmatter = 0 |
| Dossier skill inexistant | Afficher "Dossier introuvable" et demander le bon chemin |

Si le script retourne exit code 2 (erreur critique), signaler immédiatement.

## Exemples d'utilisation

```text
Utilisateur : vérifie le skill /pdf

Claude :
> Phase 1 : Skill identifié — .claude/skills/pdf/
> Phase 2 : Validation structurelle...
>   Score : 46/50 (0 critique, 1 majeur, 0 mineur)
>   Violations :
>     MAJEUR S04 (0/2) — Description sans conditions de déclenchement
>   Verdict : Conforme
```

```text
Utilisateur : audit de conformité de /transfer

Claude :
> Phase 1 : Skill identifié — .claude/skills/transfer/
> Phase 2 : Validation structurelle...
>   Score : 29/50 (1 critique, 1 majeur, 1 mineur)
>   Violations :
>     CRITIQUE S01 (0/3) — Frontmatter YAML absent
>     MAJEUR S09 (0/4) — README.md présent dans le dossier
>     MINEUR S10 (1/3) — 16 titres H1
>   Verdict : Non conforme
>   Actions correctives :
>     1. Ajouter un frontmatter YAML avec name et description
>     2. Supprimer le README.md du dossier
```

## Seuils de verdict

| Score | Verdict |
|-------|---------|
| 45-50 | Conforme — prêt pour production |
| 35-44 | Acceptable — corrections mineures recommandées |
| 25-34 | Non conforme — corrections requises |
| < 25 | Rejet — refonte nécessaire |

## Contraintes

- TOUJOURS exécuter le script check_structure.py (pas d'évaluation manuelle des critères structurels)
- TOUJOURS indiquer la version des critères dans le rapport
- TOUJOURS renvoyer vers `/skill-review` pour l'évaluation sémantique
- JAMAIS modifier le fichier audité
- JAMAIS attribuer un verdict "Conforme" si un critère CRITIQUE est en échec

## Checklist finale

- [ ] Chemin du skill résolu (via `$ARGUMENTS` ou demande utilisateur)
- [ ] Script `check_structure.py` exécuté avec succès
- [ ] Rapport produit avec score, verdict et violations
- [ ] Version des critères indiquée dans le rapport
- [ ] Renvoi vers `/skill-review` pour l'évaluation sémantique
