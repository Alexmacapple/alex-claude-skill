# Le skill /raisonnement-code, expliqué pour Loïc

*Document pédagogique — avril 2026*

---

## 1. L'approche : pourquoi ce skill existe

Imagine que tu demandes à Claude Code « est-ce que ce patch est correct ? ». Sans ce skill, Claude fait ce qu'il fait toujours : il lit le diff, réfléchit 2 secondes, et te dit « oui, ça a l'air bon ». Sauf que dans 22 % des cas, il se trompe. Il a deviné depuis le nom de la fonction au lieu de tracer le code. Il a sauté un chemin d'exécution. Il a conclu trop tôt qu'une différence était sans effet.

Ce skill s'inspire d'un papier de Meta de mars 2026 (« Agentic Code Reasoning », Ugare & Chandra) qui a montré qu'en forçant le LLM à structurer son raisonnement — poser des prémisses, tracer les chemins, prouver chaque affirmation — on passe de 78 % à 93 % de précision sur la vérification de patchs. Sans changer le modèle. Juste en changeant comment on lui demande de réfléchir.

Le principe s'appelle le **raisonnement semi-formel**. C'est le juste milieu entre « dis-moi ce que tu penses » (trop libre, plein d'erreurs) et « prouve-le mathématiquement en Lean » (impraticable sur un vrai dépôt). Le semi-formel, c'est : chaque affirmation doit citer une ligne de code. Si tu ne peux pas montrer la preuve, tu ne l'affirmes pas.

---

## 2. Les alternatives écartées

On aurait pu simplement coller les prompts du papier dans un fichier CLAUDE.md. Mais les prompts du papier sont en anglais, conçus pour un agent SWE-agent avec des capacités spécifiques (100 steps, bash tools), et pas structurés pour Claude Code.

On a aussi envisagé 3 skills séparés (un par mode : patch, bug, qa). Rejeté parce que le tronc commun (prémisses → trace → flux → hypothèse → conclusion) est le même dans les 3 cas — seuls les templates de sortie diffèrent. Un seul skill avec 3 modes est plus simple à maintenir.

Enfin, on a écarté l'idée de laisser le skill se déclencher automatiquement sur tout diff. Le raisonnement semi-formel consomme du contexte (~1100 tokens fixes + le code cible) et prend du temps. Sur un renommage de variable, c'est du gaspillage. Le skill est invoqué explicitement quand la situation le justifie.

---

## 3. L'architecture : comment c'est construit

```
.claude/skills/raisonnement-code/
├── SKILL.md                          ← Le cerveau (245 lignes)
├── context.txt                       ← Archive de recherche (papier + PRD)
└── references/
    ├── template-patch.md             ← Template mode patch (~80 lignes)
    ├── template-bug.md               ← Template mode bug (~90 lignes)
    └── template-qa.md                ← Template mode qa (~65 lignes)
```

Le SKILL.md contient le processus commun en 7 étapes, le triage, les garde-fous anti-hallucination, et les exemples. Les templates dans `references/` sont des formats de sortie détaillés que le skill charge à la demande via `Read`. C'est le même pattern que `/avocat-du-diable` avec ses fichiers de référence — on ne charge que ce dont on a besoin.

Le flux concret quand tu tapes `/raisonnement-code bug — test_export échoue` :

1. Claude Code charge le SKILL.md
2. Il lit le triage → signal « bug » → mode bug
3. Il exécute `Read("references/template-bug.md")`
4. Il applique les 7 étapes sur ton code
5. Il produit une sortie structurée avec prémisses, traces, et verdict

---

## 4. Les outils et méthodes

Le skill repose sur 4 outils Claude Code : `Read` (lire les fichiers), `Grep` (chercher dans le code), `Glob` (trouver des fichiers), `Bash` (exécuter `git diff`, `git log`).

La méthode vient directement du papier Meta. Les 3 templates reprennent fidèlement les appendices A, B et D :

- **Mode patch** (Appendice A) : DÉFINITIONS → PRÉMISSES (P1-P4) → CLAIMS numérotés par test (F1a, F1b, P1a...) → CAS LIMITES → CONTRE-EXEMPLE ou preuve d'absence → CONCLUSION test par test
- **Mode bug** (Appendice B) : SÉMANTIQUE DU TEST (T1, T2...) → TRACE structurée (METHOD/LOCATION/BEHAVIOR/RELEVANT) → CLAIMS de divergence citant les prémisses (D1→T[N]) → CLASSEMENT
- **Mode qa** (Appendice D) : TABLE DE TRACE des fonctions → FLUX DE DONNÉES (Created/Modified/Used) → PROPRIÉTÉS SÉMANTIQUES avec preuves → HYPOTHÈSE ALTERNATIVE structurée → VERDICT

Le format d'exploration agentic (quand le skill navigue dans le dépôt pour trouver le bug) suit aussi le papier : pour chaque fichier lu, il documente HYPOTHÈSE → OBSERVATIONS → MISE À JOUR des hypothèses → PROCHAINE ACTION.

---

## 5. Les compromis

Le principal compromis est entre **fidélité au papier** et **praticité dans Claude Code**.

Le papier autorise l'agent à exécuter des scripts Python indépendants pour tester le comportement du langage (ex. « que retourne `format()` quand on lui passe un entier ? »). On a décidé de ne pas implémenter ça dans le MVP — le skill reste en lecture seule. Si Claude a besoin de vérifier un comportement de bibliothèque, il peut consulter les sources dans `opensrc/` au lieu d'exécuter du code.

Autre compromis : les templates du papier ont 8-9 sections, notre processus commun en a 7. On a fusionné certaines sections pour garder la cohérence entre les 3 modes, quitte à perdre un peu de granularité sur le mode QA.

Enfin, la guidance « 50-100 lignes max » est un ajout absent du papier. Sans elle, le skill pourrait produire des analyses de 300 lignes sur un diff complexe — techniquement correctes mais illisibles.

---

## 6. Les erreurs et impasses

La première version du skill (V1) était trop générique. Les prémisses étaient en texte libre, les traces narratives, pas de numérotation. Les 3 audits croisés (skill-review, avocat-du-diable, connu-inconnu) ont fait émerger les lacunes.

La vraie erreur a été de ne pas vérifier la conformité au papier dès le début. On a construit le skill à partir du `context.txt` (notes Perplexity) au lieu de relire les appendices originaux. Résultat : la V1 avait ~70 % de conformité. Il a fallu une passe dédiée de comparaison point par point avec le papier pour monter à ~95 %.

Leçon : quand on implémente un papier, toujours vérifier contre la source primaire, pas contre un résumé.

---

## 7. Les pièges à éviter

**Piège 1 : utiliser le skill sur des tâches triviales.** Si le bug est « il manque un import », le raisonnement semi-formel est une perte de temps. Le skill est fait pour les cas où l'intuition ne suffit pas.

**Piège 2 : croire que le format garantit la qualité.** Le papier montre que le format structuré améliore la précision, mais ne l'élimine pas. L'erreur la plus courante reste le « confident wrong answer » — un raisonnement élaboré qui aboutit à une conclusion fausse parce qu'un handler downstream a été manqué.

**Piège 3 : ignorer le verdict « PREUVES INSUFFISANTES ».** C'est le verdict le plus honnête et le plus utile. Quand Claude ne peut pas prouver, il doit le dire. Si tu vois « PATCH PLAUSIBLEMENT CORRECT » sans citations `fichier:ligne`, c'est que le skill n'a pas été appliqué correctement.

**Piège 4 : oublier l'hypothèse alternative.** C'est l'étape que le LLM a le plus tendance à bâcler. Si l'hypothèse alternative est une phrase vague, relance.

---

## 8. Le regard expert

Un expert en vérification formelle remarquerait que le « semi-formel » est un compromis pragmatique, pas une innovation théorique. Ce qui est innovant, c'est de montrer que ça marche suffisamment bien en pratique (78 % → 93 %) pour être utile sans l'infrastructure d'une preuve formelle.

Un expert Claude Code remarquerait que le skill exploite un pattern puissant : les références externalisées chargées à la demande. Charger 80 lignes de template au lieu de 245 lignes de SKILL.md + 235 lignes de templates économise du contexte quand un seul mode est utilisé.

Un expert en prompt engineering remarquerait que les garde-fous JAMAIS sont la partie la plus importante du skill — plus que les templates eux-mêmes. Les 5 interdictions ciblent précisément les 3 erreurs fréquentes identifiées par le papier : deviner depuis le nom, sauter un chemin, conclure trop tôt.

---

## 9. Les leçons transférables

**Leçon 1 : la structure du raisonnement compte plus que la qualité du modèle.** Le papier utilise le même modèle (Opus 4.5) avec et sans le raisonnement semi-formel. La seule différence est le format du prompt. +15 points de précision juste en structurant le raisonnement. C'est applicable à n'importe quelle tâche où le LLM connaît la réponse mais se trompe à l'exécution.

**Leçon 2 : les certificats de preuve empêchent les raccourcis cognitifs.** Obliger le LLM à citer `fichier:ligne` pour chaque affirmation l'empêche de deviner. C'est le même principe que les tests unitaires : on écrit le test non pas pour prouver que ça marche, mais pour s'empêcher de croire que ça marche.

**Leçon 3 : l'hypothèse alternative est le test le plus puissant.** Se demander « et si j'avais tort ? » et chercher activement la preuve du contraire est plus efficace que de chercher des confirmations. C'est le steel-man inversé — au lieu de chercher pourquoi c'est bien, chercher pourquoi c'est faux.

**Leçon 4 : un papier de recherche peut devenir un outil quotidien.** Le chemin du papier au skill a pris ~2 heures : lire le papier, extraire la méthode, transposer en templates, évaluer, corriger. Ce pattern (papier → skill) est reproductible pour n'importe quelle méthodologie documentée.

---

## Comment l'utiliser en 30 secondes

```bash
# Vérifier un patch
/raisonnement-code patch — vérifie le diff de server.py

# Localiser un bug
/raisonnement-code bug — test_auth échoue avec 401 au lieu de 200

# Comprendre un comportement
/raisonnement-code qa — est-ce que delete_user supprime les fichiers S3 ?
```

Le skill produit une sortie structurée avec prémisses, traces, hypothèse alternative, et verdict. Chaque affirmation cite `fichier:ligne`. Si une preuve manque, le verdict est `PREUVES INSUFFISANTES` — et c'est la meilleure réponse possible.

---

*Source : Ugare & Chandra, « Agentic Code Reasoning », Meta 2026, arXiv 2603.01896v2*
*Skill : `.claude/skills/raisonnement-code/`*
*Document généré le 5 avril 2026*
