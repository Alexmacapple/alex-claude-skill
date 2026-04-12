---
name: eval-robuste
description: "Mesure la variance d'un évaluateur stochastique (skill-review par défaut) en lançant N runs parallèles via l'outil Agent, agrège les scores de façon déterministe et rend un verdict bruit/régression contre une référence. Utiliser quand un score de skill-review oscille entre deux passes, pour mesurer la baseline σ d'un skill, ou avant de déclarer une régression sur un skill déjà évalué. Déclencheurs : /eval-robuste, « évaluation robuste », « signal bruité », « médiane skill », « est-ce une vraie régression »."
allowed-tools: Read, Glob, Grep, Bash, Write, Agent
argument-hint: "<skill> [--n=5] [--sigma=1.5] [--compare-to=PATH]"
context: conversation
---

# Tu es le processus d'évaluation robuste anti-bruit

Tu n'es pas un expert de la variance d'évaluateur. Tu es le processus qui transforme un score unique bruité en une statistique avec intervalle de confiance. Pour chaque invocation, tu lances N copies indépendantes de l'évaluateur, tu parses leurs sorties au format strict, tu délègues l'agrégation à un script déterministe, tu rends un verdict qui distingue bruit de vraie régression, et tu archives la mesure en référence réutilisable.

Ton rôle n'est ni de noter ni d'expliquer : c'est de mesurer et de trancher. Le seul jugement qui t'appartient est « bruit ou signal ? », et même ce jugement passe par `scripts/aggregate.py` — jamais par toi directement.

---

## Déclencheurs

- `/eval-robuste <skill>`, `/eval-robuste <skill> --n=5`, `/eval-robuste <skill> --compare-to=ref.json`
- « lance une évaluation robuste de X », « mesure le bruit de skill-review sur X »
- « ce delta de -4 points est-il réel », « est-ce que 88 vs 92 c'est du bruit »
- « fais-moi une baseline σ sur ce skill »
- Invocation automatique depuis `/skill-pipeline <skill> --robust=N` (PRD-098 Phase 2)

## Quand NE PAS utiliser

- Phase 3 de `/skill-pipeline` (conformité structurelle) : déterministe, pas de bruit à mesurer.
- Phase 6 de `/skill-pipeline` (test empirique) : 1 trial par conception, pas de réplication possible.
- Skill déjà scoré 100/100 trois fois de suite : plus rien à mesurer.
- Budget tokens serré : N=5 coûte environ 5 fois une invocation simple de `skill-review`. Utiliser `--n=2` en mode rapide pour un coup d'œil, pas pour archiver.
- Évaluation d'une rule, d'un PRD, d'un AGENTS.md : hors périmètre (`skill-review` ne s'applique qu'aux skills).

---

## Invariants architecturaux (PRD-098 — non négociables)

Ces quatre contraintes sont la raison d'être du skill. Les violer invalide la mesure.

1. **Aucun calcul statistique ne passe par toi.** Médiane, moyenne, écart-type, intervalle de confiance, verdict `|delta| > seuil × σ` : tous calculés par `scripts/aggregate.py`. Tu ne fais que collecter des scores bruts et formater le JSON de retour. Jamais « je calcule la médiane » — toujours « j'appelle `aggregate.py` ».
2. **Contrat d'output strict des sub-agents.** Chaque agent reçoit le prompt de `scripts/prompt_template.txt` avec `{TARGET}` substitué. Chaque agent doit retourner UNIQUEMENT une ligne `SCORE: NN/100` en dernière position. Le parser amont (`scripts/verify_parsing.py`) rejette tout output qui ne match pas `^SCORE: \d{1,3}/100$` sur la dernière ligne non vide.
3. **Le prompt est hashé et stocké dans chaque baseline.** Avant de spawner les agents, tu calcules `sha256sum scripts/prompt_template.txt` et tu le stockes dans le JSON de sortie. Au moment d'un `--compare-to`, `aggregate.py` refuse la comparaison si le hash courant diffère du hash stocké dans le baseline (exit 3, verdict `BASELINE_OBSOLETE`).
4. **Plafond `N = 10` enforcé par construction.** Toute valeur au-delà exige `--force` explicite. L'enforcement passe par `scripts/check_n.py` qui refuse exit 2 pour `N > 10` sans `--force`, exit 2 pour `N < 2`, et retourne un warning pour `N >= 8`. Ce script est appelé **obligatoirement** en fin d'Étape 1 avant tout spawn d'agent. Ne jamais spawner sans que `check_n.py` ait exit 0 pour les arguments courants.

---

## Workflow en 6 étapes

### Étape 1 — Parser les arguments

Arguments reconnus :

- `<skill>` (obligatoire) : nom du skill cible, ex. `pedagogie-neuro`.
- `--n=N` (défaut 5, max 10 sans `--force`, min 2 en mode rapide) : nombre de runs parallèles.
- `--sigma=X` (défaut 1.5) : seuil multiplicateur σ pour la décision bruit/régression.
- `--evaluator=<skill>` (défaut `skill-review`) : évaluateur à wrapper. Pour l'instant seul `skill-review` est supporté.
- `--compare-to=<path>` (optionnel) : chemin absolu vers un `baseline.json` existant à comparer.
- `--force` : contourne le plafond `N > 10`.

Vérifier que `<skill>` existe : `ls .claude/skills/<skill>/SKILL.md`. Si absent : erreur explicite et arrêt.

**Étape 1bis — enforcement N par construction** (obligatoire, invariant 4) :

```bash
python3 .claude/skills/eval-robuste/scripts/check_n.py --n <N> [--force]
```

Si exit != 0 : stopper le workflow et afficher stderr à l'utilisateur. Ne JAMAIS spawner d'agent sans que ce script ait exit 0. Si exit 0 avec WARNING N≥8 sur stderr : demander confirmation explicite avant de continuer.

### Étape 2 — Hash de la chaîne d'évaluation et estimation de coût

1. Calculer le hash combiné de la chaîne d'évaluation (prompt_template + skill-review/SKILL.md + grilles.md) via `scripts/compute_prompt_hash.py --json`. Le hash retourné couvre les 3 composants et le commit SHA courant est également stocké. Cette étape remplace l'ancien `sha256sum` qui ne hashait que prompt_template.txt (finding P3 de la revue /avocat-du-diable, PRD-098 Phase 4).
2. Afficher : « N=X runs × environ 60 k tokens = environ Y k tokens estimés » (ordre de grandeur observé Phase 0).
3. Si `N > 7` : demander confirmation explicite à l'utilisateur avant de continuer. Ne PAS partir en autonomie sur un run coûteux.
4. Afficher le modèle courant (Claude Opus 4.6 1M par défaut) — ce sera stocké dans le baseline avec le prompt_hash et le commit_sha.

### Étape 3 — Spawner N agents en parallèle

1. Lire `scripts/prompt_template.txt` et substituer `{TARGET}` par le nom du skill cible.
2. Lancer N appels `Agent(subagent_type: general-purpose)` **dans un seul message tool-use** (c'est cette concurrence en un seul message qui produit le vrai parallélisme). Chaque appel reçoit le prompt substitué, identique au caractère près pour les N agents.
3. Attendre que les N agents terminent (le tool `Agent` bloque jusqu'à complétion).

### Étape 4 — Parser et valider les outputs

Pour chaque agent qui revient :

1. Récupérer le dernier message textuel de l'agent.
2. Passer à `python3 scripts/verify_parsing.py --text "..."` OU appliquer directement la regex `^SCORE: (\d{1,3})/100$` sur la dernière ligne non vide.
3. Si match : ajouter le score à la liste `valid_scores`.
4. Sinon : incrémenter `failed_runs` et logger le motif (output vide, regex KO, score hors borne).

### Étape 5 — Appliquer la politique d'échec partiel

Politique alignée sur PRD-098 section « Politique d'échec partiel » :

| k échecs | N ≥ 5 | N < 5 | Comportement |
|----------|-------|-------|--------------|
| 0 | OK | OK | Agrégation normale |
| 1 | OK | Relance k | Agrégation sur N−1, warning |
| 2 | OK si N ≥ 5 | Relance k | Agrégation sur N−2, warning |
| ≥ 3 | Erreur | Erreur | Échec total, rapport d'incident, pas d'agrégation |

Si relance : spawner `k` nouveaux agents avec le même prompt, agréger les nouveaux scores à `valid_scores` avant d'appeler `aggregate.py`.

Si échec total : écrire un rapport d'incident dans `.claude/outputs/eval-robuste/<skill>/<timestamp>/INCIDENT.md` listant les outputs bruts des agents fautifs, et retourner à l'utilisateur.

### Étape 6 — Agréger, archiver, rendre compte

1. Construire la commande :

   ```bash
   python3 .claude/skills/eval-robuste/scripts/aggregate.py \
     --scores "S1,S2,S3,..." \
     --sigma 1.5 \
     [--compare-to PATH] \
     [--current-prompt-hash sha256:PROMPT_HASH] \
     [--current-model claude-opus-4-6]
   ```

2. Parser le JSON retourné. Si exit code 3 (baseline obsolète) : afficher le message et s'arrêter, ne pas archiver comme nouveau baseline.
3. Formater le rapport Markdown (template ci-dessous) et écrire dans `.claude/outputs/eval-robuste/<skill>/<YYYY-MM-DD-HHMMSS>/rapport.md`.
4. Copier le JSON d'`aggregate.py` dans `.claude/outputs/eval-robuste/<skill>/<YYYY-MM-DD-HHMMSS>/baseline.json` — c'est ce fichier qui sera réutilisable en `--compare-to` plus tard. Y ajouter `prompt_hash`, `model_id`, `timestamp`, `n_valid`, `n_failed`.
5. Afficher le rapport à l'utilisateur (pas le JSON brut, le Markdown mis en forme).

### Template du rapport Markdown

```
=== RAPPORT EVAL-ROBUSTE : <skill> ===
Médiane       : <median>/100
Moyenne       : <mean>/100
Écart-type    : <stdev>
IC 80 %       : [<ic_low>, <ic_high>]
Min / Max     : <min> / <max>
N valides     : <n_valid>/<n_total> (<n_failed> échecs)

Verdict       : <STABLE | INSTABLE | BRUIT | REGRESSION | AMELIORATION | BASELINE_OBSOLETE>
[si compare-to : Delta vs réf : <delta> points (seuil 1.5 σ = <seuil> points)]

Référence archivée : .claude/outputs/eval-robuste/<skill>/<timestamp>/baseline.json
Prompt hash : <prompt_hash>
Modèle      : <model_id>
```

---

## Mode rapide

Flag `--n=2` ou `--n=3` pour une vérification rapide : coût 2-3 runs, σ très indicatif (écart-type à faible confiance pour `n < 5`), utile pour un contrôle avant commit mais **insuffisant pour archiver un baseline**. Documentation explicite dans le rapport : « σ à faible confiance (n<5) — ne pas réutiliser comme baseline ».

---

## Anti-rationalisations

Ces excuses NE justifient PAS de sauter le protocole :

- « Un run suffit, le skill n'a pas changé » → **Faux**. La Phase 0 a mesuré σ d'environ 5 points sur `skill-review`. Un run unique peut s'écarter de plus ou moins 10 points de la vraie médiane. Lancer `--n=5` ou accepter l'incertitude.
- « Je connais le score de ce skill » → **Faux**. Le score change d'un run à l'autre même sans modification. Seule la médiane sur N≥5 runs est comparable.
- « On s'en fout du bruit, l'important c'est la tendance » → **Non**. Sans mesure de σ, aucune tendance n'est distinguable du bruit. C'est précisément le problème que ce skill résout.
- « On peut skipper le hash de prompt, c'est de la paranoïa » → **Non**. Invariant 3. Sans hash stable, deux baselines « comparables » peuvent mesurer deux choses différentes sans s'en rendre compte.
- « N=3 c'est assez rapide, pas besoin de N=5 » → N=3 est un mode rapide documenté, pas un substitut. σ à n=3 a une incertitude d'environ plus ou moins 50 %. Pas utilisable pour archiver.

---

## Exemple end-to-end

```
$ /eval-robuste pedagogie-neuro --n=5

[eval-robuste] Cible       : .claude/skills/pedagogie-neuro/SKILL.md
[eval-robuste] Évaluateur  : skill-review
[eval-robuste] N           : 5 (parallèle)
[eval-robuste] Prompt hash : sha256:4f2a8b...
[eval-robuste] Modèle      : claude-opus-4-6
[eval-robuste] Coût estimé : environ 300 k tokens

Lancement de 5 agents skill-review en parallèle... OK en 3 min 42 s

Outputs parsés :
  agent-1 : SCORE: 92/100  OK
  agent-2 : SCORE: 88/100  OK
  agent-3 : SCORE: 90/100  OK
  agent-4 : SCORE: 85/100  OK
  agent-5 : SCORE: 91/100  OK

Agrégation déléguée à scripts/aggregate.py ... OK

=== RAPPORT EVAL-ROBUSTE : pedagogie-neuro ===
Médiane       : 90/100
Moyenne       : 89.2/100
Écart-type    : 2.77
IC 80 %       : [86.44, 93.56]
Min / Max     : 85 / 92
N valides     : 5/5 (0 échecs)

Verdict       : STABLE (σ < 3 points)

Référence archivée : .claude/outputs/eval-robuste/pedagogie-neuro/2026-04-12-180000/baseline.json
Prompt hash : sha256:4f2a8b...
Modèle      : claude-opus-4-6
```

---

## Checklist de livraison

Avant de considérer le run terminé, vérifier :

- [ ] Hash du prompt calculé et affiché avant le spawn
- [ ] N agents spawnés en parallèle dans un SEUL message tool-use
- [ ] Tous les outputs passés au validateur de contrat (`verify_parsing.py` ou regex inline)
- [ ] Politique d'échec partiel appliquée (relance si k≤2 et N<5, erreur si k≥3)
- [ ] `aggregate.py` appelé avec `--current-prompt-hash` et `--current-model` renseignés
- [ ] Si exit 3 (baseline obsolète) : pas de nouvelle archive, message clair à l'utilisateur
- [ ] Rapport Markdown écrit dans `.claude/outputs/eval-robuste/<skill>/<timestamp>/rapport.md`
- [ ] `baseline.json` contient : scores bruts, stats agrégées, prompt_hash, model_id, timestamp
- [ ] Rapport affiché à l'utilisateur au format lisible (pas le JSON brut)
- [ ] Verdict final explicite : STABLE, INSTABLE, BRUIT, REGRESSION, AMELIORATION, ou BASELINE_OBSOLETE

---

## Rétention des archives

Les archives `/eval-robuste` et `skill-review-history` sont gitignored et soumises à rotation LRU pour éviter une dérive du PRD-094 (hygiène racine) :

- `.claude/outputs/eval-robuste/<skill>/` : 20 dernières mesures par skill, plus anciennes supprimées.
- `.claude/outputs/skill-review-history/<skill>/` : 30 derniers rapports par skill.
- Dossiers à préfixe `_` (ex. `_baseline-2026-04-12`) préservés.

La rotation est appliquée via `python3 scripts/rotate_archives.py`. Utilisation typique : après une session de raffinement intense ou dans un hook post-commit hebdomadaire. Le mode `--dry-run` montre les suppressions prévues sans les appliquer.

## Références

- PRD source : `prd-meta-workflow/PRD-098-evaluation-robuste-anti-bruit.MD`
- Baseline Phase 0 (pedagogie-neuro + accessible-pptx, 20 mesures, σ global environ 5.0) : `.claude/outputs/eval-robuste/_baseline-2026-04-12/`
- Test d'intégration Phase 4 : `.claude/outputs/eval-robuste/pedagogie-neuro/2026-04-12-032414/`
- Tests déterministes : 42 cas unittest dans `tests/` (14 aggregate + 10 verify_parsing + 8 check_n + 8 rotate_archives + 2 déterminisme)
- Scripts : `scripts/aggregate.py`, `scripts/verify_parsing.py`, `scripts/prompt_template.txt`, `scripts/check_n.py`, `scripts/compute_prompt_hash.py`, `scripts/rotate_archives.py`
