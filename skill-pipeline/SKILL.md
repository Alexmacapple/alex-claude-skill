---
name: skill-pipeline
description: Cycle de vie complet des skills Claude. Creation, validation structurelle Anthropic + SkillsBench (/65), evaluation semantique (/100), pressure testing (/5). Utiliser pour creer un skill, auditer un skill existant, lancer le pipeline complet ou tester la robustesse sous pression (--pressure).
argument-hint: "[nom-du-skill] [--create|--check|--review|--full|--pressure|--empirical] [--robust=N]"
allowed-tools: Read, Glob, Grep, Bash, Edit, Write
context: conversation
---

# Skill Pipeline — Cycle de vie des skills

Orchestre le cycle complet d'un skill Claude : creation, validation structurelle, evaluation semantique. Chaine automatiquement les skills `skill-creator`, `skill-conformity-checker` et `skill-review`.

## Declencheurs

- "/skill-pipeline", "pipeline skill", "cycle de vie skill"
- "cree un skill", "nouveau skill", "genere un skill"
- "audite ce skill", "verifie ce skill", "valide ce skill", "check ce skill"
- "score du skill", "evalue ce skill", "quality check skill"

## Modes d'utilisation

| Mode | Commande | Comportement |
|------|----------|--------------|
| `--create` | `/skill-pipeline mon-skill --create` | Cree le skill puis enchaine check + review + pressure |
| `--check` | `/skill-pipeline mon-skill --check` | Conformity-checker + skill-review + pressure sur un skill existant |
| `--full` | `/skill-pipeline mon-skill --full` | Alias de --create, active aussi --empirical |
| `--pressure` | `/skill-pipeline mon-skill --pressure` | Pressure testing seul sur un skill existant |
| `--empirical` | `/skill-pipeline mon-skill --empirical` | Test empirique seul : delta avec/sans skill (Phase 6, PRD-092) |
| `--robust=N` | `/skill-pipeline mon-skill --check --robust=5` | Phase 4 deleguee a /eval-robuste avec N runs paralleles (PRD-098 Phase 2). Combinable avec --check, --full, --review. Defaut sans flag : 1 run unique |
| (defaut) | `/skill-pipeline mon-skill` | Auto-detect : si le skill existe -> --check, sinon -> --create |

## Workflow

### Phase 1 : Detection et parsing

1. Parser `$ARGUMENTS` pour extraire :
   - **Nom du skill** : premier argument (kebab-case)
   - **Mode** : flag `--create`, `--check`, `--full`, ou auto-detection
   - **Flag robuste** (optionnel) : `--robust=N` avec N entier dans [2, 10]. Active la delegation de Phase 4 a `/eval-robuste` (PRD-098 Phase 2). Sans flag : 1 run unique de `skill-review`. Si N > 10 : exiger `--force`, sinon erreur explicite
2. Resoudre le chemin : `.claude/skills/{nom}/SKILL.md`
3. Verifier l'existence du skill :
   - Si le skill existe ET mode `--create` : avertir l'utilisateur que le skill existe deja, demander confirmation avant ecrasement
   - Si le skill N'EXISTE PAS et mode `--check` : afficher une erreur et lister les skills disponibles
   - Si aucun mode specifie : le skill existe -> `--check`, sinon -> `--create`
4. Afficher le mode selectionne avant de continuer :

```
[PIPELINE] Skill : {nom-du-skill}
[PIPELINE] Mode  : {create|check|full}
[PIPELINE] Chemin : .claude/skills/{nom}/
```

### Phase 0 : Gate de decision (modes create/full uniquement)

Cette phase est IGNOREE en mode `--check` (la decision de creer le skill est deja prise).

Elle est OBLIGATOIRE en modes `--create` et `--full` : rien n'est cree tant que le gate n'a pas verdicte.

1. Invoquer le skill `/to-skill-or-not-to-skill` avec comme argument une description courte de l'idee du skill :

```
/to-skill-or-not-to-skill "description de l'idee du skill {nom}"
```

2. Lire le verdict produit par le skill :
   - **Go** : l'arbre de decision valide la creation. Continuer a Phase 2.
   - **Pas de skill** : l'arbre refuse la creation. ARRETER le pipeline. Afficher l'alternative proposee (rule, instruction, guide, runbook, rien) et le squelette du fichier a creer. Message : « Le gate a verdicte Pas de skill. Suivre l'alternative recommandee plutot que creer ce skill. »
   - **Reformuler** : l'arbre demande une clarification. ARRETER le pipeline. Afficher les questions de clarification. Message : « Repondre aux questions puis relancer le pipeline. »
3. Afficher :

```
[PIPELINE] Phase 0 : Gate decision ........... {Go | Pas de skill | Reformuler}
```

**Reference** : PRD-099, rule `.claude/rules/skill-decision-rules.md`. Le gate a ete valide empiriquement en Phase 0 du PRD-099 avec un taux d'accord arbre/humain de 6/6 sur 6 skills rétro-évalués.

**Option de contournement** : `--skip-gate` permet de forcer la creation sans passer par le gate, avec un avertissement affiche. A reserver aux cas ou l'utilisateur a deja applique l'arbre manuellement. N'est jamais le comportement par defaut.

### Phase 2 : Creation (modes create/full uniquement)

Cette phase est IGNOREE en mode `--check`. Elle n'est lancee qu'apres un verdict `Go` de Phase 0.

1. Invoquer le skill `skill-creator` en suivant son workflow complet (6 etapes)
   - Passer le nom du skill comme argument
   - Laisser le skill-creator generer la structure (SKILL.md + scripts/ + references/ si necessaire)
2. Verifier que `.claude/skills/{nom}/SKILL.md` a bien ete cree
   - Si le fichier n'existe pas apres creation : signaler l'echec et ARRETER le pipeline
3. Afficher :

```
[PIPELINE] Phase 2 : Creation .............. OK
```

### Phase 3 : Validation structurelle

Executer le script de conformite structurelle (Anthropic S01-S15 + SkillsBench S16-S20).

1. Lancer la commande :

```bash
python3 .claude/skills/skill-conformity-checker/scripts/check_structure.py .claude/skills/{nom}/ --json
```

2. Parser la sortie JSON pour extraire :
   - `score_structurel` : note sur 65
   - `verdict` : Conforme (>= 58) / Acceptable (45-57) / Non conforme (32-44) / Rejet (< 32)
   - `details.skillsbench` : sous-score SkillsBench sur 15 avec les critères S16-S20
   - `violations` : liste des criteres echoues avec severite
3. Si score < 40 :
   - Lister les violations CRITIQUE et MAJEUR
   - Proposer des corrections automatiques pour chaque violation
   - Appliquer les corrections acceptees
   - Re-executer le script pour obtenir le score actualise
4. Afficher :

```
[PIPELINE] Phase 3 : Conformite structurelle  {score}/65 — {verdict}
           SkillsBench : {score_sb}/15 (S16-S20)
```

### Phase 4 : Evaluation semantique

Invoquer le workflow de `skill-review` sur le skill.

**Mode par defaut (1 run)** :

1. Lire le fichier `.claude/skills/skill-review/SKILL.md` pour charger ses instructions
2. Lire le fichier `.claude/skills/skill-review/references/grilles.md` pour charger les grilles de notation
3. Executer l'evaluation semantique en suivant le workflow de skill-review :
   - Charger les references (GUIDELINES-CLAUDE-CODE.MD)
   - Evaluer le SKILL.md selon la grille (100 pts)
   - Identifier conformites, non-conformites, actions correctives
4. Collecter :
   - `score` : note sur 100
   - Liste des actions correctives avec priorites
5. Afficher :

```
[PIPELINE] Phase 4 : Evaluation semantique .. {score}/100
```

**Mode robuste (--robust=N, PRD-098 Phase 2)** :

Si l'utilisateur a passe `--robust=N` au pipeline, deleguer la Phase 4 a
`/eval-robuste` au lieu d'un run unique :

1. Verifier que N est dans [2, 10] (ou --force au-dela). Sinon : erreur.
2. **Garde-fou de cout** : afficher l'estimation `N × ~60 k tokens` et :
   - N <= 4 : executer sans demander
   - 5 <= N <= 7 : executer sans demander mais afficher le cout
   - N >= 8 : demander confirmation explicite a l'utilisateur avant d'executer
3. Deleguer en invoquant le skill eval-robuste avec la cible courante :
   `/eval-robuste <skill-cible> --n=N`
4. `/eval-robuste` produit un rapport contenant mediane, sigma, IC, verdict
   (STABLE/INSTABLE). Recuperer la mediane comme `score`.
5. Archiver le chemin du `baseline.json` produit par eval-robuste — il devient
   reutilisable via `/eval-robuste --compare-to=...` lors d'un futur run du
   pipeline sur le meme skill.
6. Afficher :

```
[PIPELINE] Phase 4 : Evaluation semantique robuste (N={N}) .. mediane {score}/100, sigma {sigma}
           Baseline archivee : .claude/outputs/eval-robuste/{skill}/{ts}/baseline.json
```

**Quand utiliser --robust=N** : quand le skill evalue est suspecte d'avoir un
score bruite (oscillations observees sur des runs successifs), quand on veut
mesurer la baseline de variance avant un cycle de refactor, ou quand on doit
decider si une regression apparente entre deux passes est reelle ou du bruit
d'evaluateur. Le defaut reste le run unique : plus rapide, coherent avec
l'usage courant du pipeline.

### Phase 5 : Pressure testing

Tester la robustesse du skill sous scenarios adverses.

1. Lire les scenarios de pression : `.claude/skills/skill-review/references/pressure-scenarios.md`
2. Pour chaque scenario (S1-S5), analyser :
   - Le skill contient-il une formulation qui resiste a cette pression ?
   - L'agent pourrait-il rationaliser un contournement ?
   - Critere binaire : RESPECTE ou CONTOURNE
3. Produire le score : X/5
4. Si score < 3/5 :
   - Lister les failles identifiees
   - Proposer des renforcements GREEN concrets (texte exact)
   - Si l'utilisateur accepte, appliquer les renforcements
   - Re-evaluer pour confirmer l'amelioration
5. Afficher :

```
[PIPELINE] Phase 5 : Pressure testing ...... {score}/5
```

**En mode `--pressure` seul** : executer uniquement cette phase, ignorer les phases 2-4.

**Evaluation** : le pressure testing evalue la formulation du skill, pas le comportement reel en session. Le monitoring post-hoc (observation sur 10 sessions) est le vrai signal — cette phase est un premier filtre.

### Phase 6 : Test empirique (PRD-092, optionnel)

Mesurer le delta reel de performance avec et sans le skill sur une tache representative. Inspiration directe du protocole SkillsBench (arXiv:2602.12670v1).

Cette phase est **optionnelle** et ne bloque JAMAIS le verdict final. Elle est activee par :
- `--empirical` : phase 6 seule
- `--full` : cree + check + review + pressure + empirical (pipeline complet)

Processus :

1. Demander a l'utilisateur une tache representative du domaine du skill.
   - Exemple pour `/audit-rgaa` : « Audite la page https://exemple.fr selon le RGAA 4.1.2 »
   - La tache doit etre verifiable (succes observable) et reproductible
2. Proposer d'executer la tache **deux fois** :
   - Session A : sans le skill charge (baseline)
   - Session B : avec le skill charge (condition enrichie)
3. Pour chaque session, collecter :
   - Duree d'execution
   - Livrables produits (fichiers, output, decisions)
   - Conformite au resultat attendu (OUI/NON/PARTIEL)
4. Comparer les deux sessions et produire le rapport :

```
[PIPELINE] Phase 6 : Test empirique (optionnel)
  Tache         : {description courte}
  Session A (baseline)  : {duree} | livrables {count_A} | conformite {verdict_A}
  Session B (avec skill) : {duree} | livrables {count_B} | conformite {verdict_B}
  Delta observe : {OUI/NON} ameliore | {details}
  Estimation gain : {+X pp | non mesurable}
```

5. Proposer d'ajouter une trace dans le skill lui-meme sous la forme d'un commentaire HTML :

```html
<!--
Test empirique PRD-092 ({date}) :
- Tache : {description}
- Baseline : {verdict}
- Avec skill : {verdict}
- Gain observe : {details}
-->
```

**Limites de la phase 6** :
- C'est une mesure **subjective** et non-reproductible (1 trial vs les 5 de SkillsBench)
- Pas d'isolation container, pas de scoring automatique
- L'objectif est **creer l'habitude** de mesurer, pas de produire une metrique rigoureuse
- Pour une mesure rigoureuse, se referer a SkillsBench ou a une future infrastructure Harbor

**Quand sauter la phase 6** : tache trop complexe pour 2 executions rapides (budget temps), tache non-verifiable par observation humaine, skill purement mecanique sans delta observable.

---

## Rapport final

A la fin du pipeline, produire un rapport combine :

```
=== RAPPORT SKILL-PIPELINE : {nom-du-skill} ===

Phase 0 : Gate decision ......... {Go | Pas de skill | Reformuler | IGNOREE (mode check)}
Phase 2 : Creation .............. {OK|IGNOREE (mode check ou gate negatif)}
Phase 3 : Conformite structurelle  {score}/65 — {verdict}
  - SkillsBench : {score_sb}/15 (S16-S20)
  - Violations : {liste ou "aucune"}
Phase 4 : Evaluation semantique .. {score}/100
  - Grille SkillsBench : Domaine {verte|orange|rouge} / Focalisation {...} / Composabilite {...}
  - Actions correctives : {liste avec priorites}
Phase 5 : Pressure testing ...... {score}/5
  - Failles : {liste ou "aucune"}
Phase 6 : Test empirique ........ {OK|IGNOREE (mode non --full/--empirical)}
  - Delta observe : {resume ou "non mesure"}

Score combine : {structurel}/65 + {semantique}/100 + {pressure x 10}/50 = {total}/215
Verdict : {verdict-final}

Actions recommandees :
1. {corrections priorite haute}
2. {corrections priorite moyenne}
3. {corrections priorite basse}
```

## Seuils de verdict final

Seuils proportionnels au passage /200 → /215 (+15 pts SkillsBench) :

| Score combine /215 | Verdict |
|-------------------|---------|
| >= 172 | Conforme (production-ready) |
| 129-171 | Acceptable (corrections mineures) |
| 86-128 | Non conforme (corrections requises) |
| < 86 | Rejet (refonte necessaire) |

## Contraintes

- JAMAIS modifier les skills `skill-creator`, `skill-conformity-checker`, `skill-review` ou `to-skill-or-not-to-skill`
- JAMAIS sauter une phase : les phases s'enchainent sequentiellement
- JAMAIS sauter le gate Phase 0 en mode `--create` ou `--full` sauf si `--skip-gate` est explicitement passe (avec avertissement)
- JAMAIS creer un skill si le gate Phase 0 a verdicte `Pas de skill` ou `Reformuler`
- TOUJOURS afficher le rapport final meme si une phase echoue (indiquer ECHEC pour la phase concernee)
- TOUJOURS executer le script check_structure.py avec le flag `--json` pour un parsing fiable
- Si le skill-creator ou to-skill-or-not-to-skill n'est pas disponible, signaler l'erreur clairement et proposer une creation manuelle

## Exemples d'utilisation

```text
Utilisateur : /skill-pipeline pdf --check

Claude :
> [PIPELINE] Skill : pdf
> [PIPELINE] Mode  : check
> [PIPELINE] Chemin : .claude/skills/pdf/
>
> [PIPELINE] Phase 3 : Conformite structurelle  55/65 — Acceptable
> [PIPELINE] Phase 4 : Evaluation semantique .. 82/100
>
> === RAPPORT SKILL-PIPELINE : pdf ===
> Phase 2 : Creation .............. IGNOREE (mode check)
> Phase 3 : Conformite structurelle  55/65 — Acceptable
>   - Violations : S04 (description sans triggers)
> Phase 4 : Evaluation semantique .. 82/100
>   - Actions correctives : 3 (1 haute, 2 moyennes)
> Score combine : 55/65 + 82/100 = 137/165
> Verdict : Conforme (production-ready)
```

```text
Utilisateur : /skill-pipeline mon-nouveau-skill

Claude :
> [PIPELINE] Skill : mon-nouveau-skill
> [PIPELINE] Mode  : create (skill inexistant, auto-detect)
> [PIPELINE] Chemin : .claude/skills/mon-nouveau-skill/
>
> [PIPELINE] Phase 2 : Creation .............. OK (SKILL.md + scripts/)
> [PIPELINE] Phase 3 : Conformite structurelle  60/65 — Conforme
> [PIPELINE] Phase 4 : Evaluation semantique .. 88/100
> Score combine : 60/65 + 88/100 = 148/165
> Verdict : Conforme (production-ready)
```

```text
Utilisateur : /skill-pipeline skill-inexistant --check

Claude :
> [PIPELINE] Erreur : .claude/skills/skill-inexistant/SKILL.md introuvable.
> Skills disponibles : pdf, playbook, transfer, prd, skill-review, ...
> Utiliser --create pour creer ce skill.
```

## Checklist avant cloture

- [ ] Le mode a ete correctement detecte ou applique
- [ ] Phase 0 executee en mode --create ou --full, verdict Go obtenu (ou pipeline arrete si verdict Pas de skill / Reformuler)
- [ ] Phase 2 executee (si applicable) et SKILL.md cree
- [ ] Phase 3 executee et score /65 obtenu (incluant sous-score SkillsBench /15)
- [ ] Phase 4 executee et score /100 obtenu (incluant grille SkillsBench diagnostique)
- [ ] Phase 5 executee et score /5 obtenu
- [ ] Phase 6 executee si mode --full ou --empirical, ignoree sinon
- [ ] Rapport final affiche avec score combine /215 et verdict
