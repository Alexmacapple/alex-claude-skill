# /raisonnement-code — Revue de code semi-formelle

*Basé sur le papier Meta « Agentic Code Reasoning » (Ugare & Chandra, arXiv 2603.01896v2, mars 2026)*

---

## Le problème

Quand tu demandes à Claude Code « est-ce que ce patch est correct ? », il devine dans 22 % des cas. Il suppose le comportement d'une fonction depuis son nom, saute un chemin d'exécution, ou conclut trop tôt qu'une différence est sans effet.

Ce skill force Claude à **prouver** au lieu de deviner. Chaque affirmation doit citer `fichier:ligne`. Pas de preuve, pas d'affirmation.

**Résultat** : la précision passe de 78 % à 93 % sur la vérification de patchs (papier Meta, 7 modèles, 70 combinaisons testées).

---

## Usage rapide

```bash
# Vérifier un patch ou un diff
/raisonnement-code patch — vérifie le diff de auth.py

# Localiser un bug
/raisonnement-code bug — test_export échoue avec KeyError

# Comprendre un comportement
/raisonnement-code qa — est-ce que delete_user supprime les fichiers S3 ?
```

---

## Les 3 modes

### Mode `patch`

**Quand** : tu as un diff, une PR, ou deux variantes d'un correctif à comparer.

**Ce que le skill produit** :
- Définitions formelles (équivalence modulo tests)
- Prémisses numérotées (P1-P4) sur chaque patch
- Claims par test (F2P, P2P) avec traces d'exécution
- Cas limites + contre-exemple ou preuve d'absence
- Verdict : `PATCH CORRECT` / `NON CORRECT` / `ÉQUIVALENTS` / `NON ÉQUIVALENTS` / `PREUVES INSUFFISANTES`

### Mode `bug`

**Quand** : un test échoue, un comportement est inattendu, tu ne trouves pas la cause.

**Ce que le skill produit** :
- Prémisses formelles sur le test (T1, T2...)
- Trace structurée depuis le point d'entrée (tableau METHOD / LOCATION / BEHAVIOR)
- Claims de divergence citant les prémisses (D1→T[N])
- Hypothèses concurrentes départagées
- Verdict : `CAUSE IDENTIFIÉE` / `PLUSIEURS CAUSES` / `PREUVES INSUFFISANTES`

### Mode `qa`

**Quand** : tu veux savoir ce que fait réellement un morceau de code, avec preuves.

**Ce que le skill produit** :
- Table de trace des fonctions
- Flux de données (Created / Modified / Used)
- Propriétés sémantiques avec preuves fichier:ligne
- Vérification d'hypothèse alternative
- Verdict : `OUI` / `NON` / `PARTIELLEMENT` / `IMPOSSIBLE À ÉTABLIR`

---

## Quand l'utiliser

| Situation | Utiliser ? |
|-----------|-----------|
| Diff complexe avec effets de bord | **Oui** |
| Bug qui résiste à l'intuition | **Oui** |
| « Est-ce que ce code fait X ? » sur du code interprocédural | **Oui** |
| Renommage de variable, typo, import manquant | Non — le raisonnement libre suffit |
| Scan de sécurité (credentials, eval) | Non — utiliser `/code-review` |
| Critique globale d'un plan | Non — utiliser `/avocat-du-diable` |

---

## Ce qui se passe sous le capot

1. Le skill charge le SKILL.md (245 lignes)
2. Il détecte le mode (patch/bug/qa) depuis ta demande
3. Il charge le template de référence correspondant via `Read`
4. Il lit ton code source via `Read`, `Grep`, `Glob`
5. Il applique les 7 étapes dans l'ordre : reformulation → prémisses → périmètre → trace → flux → hypothèse → conclusion
6. Il produit une sortie de 50-100 lignes avec verdict et preuves `fichier:ligne`

---

## Installation

```bash
cp -r raisonnement-code ~/.claude/skills/
```

---

## Fichiers

```
raisonnement-code/
├── SKILL.md                          # Le skill (245 lignes)
├── README.md                         # Ce fichier
└── references/
    ├── template-patch.md             # Template mode patch (~80 lignes)
    ├── template-bug.md               # Template mode bug (~90 lignes)
    └── template-qa.md                # Template mode qa (~65 lignes)
```

---

## Le raisonnement semi-formel, en une phrase

Le juste milieu entre « dis-moi ce que tu penses » (trop libre, 78 % de précision) et « prouve-le en Lean » (impraticable). Chaque affirmation cite une ligne de code. Si tu ne peux pas montrer la preuve, tu ne l'affirmes pas.

---

## Référence scientifique

Shubham Ugare & Satish Chandra, « Agentic Code Reasoning », Meta, mars 2026
- arXiv : https://arxiv.org/abs/2603.01896
- Version HTML : https://arxiv.org/html/2603.01896v2
- Résultats : 78 % → 93 % (patch), 87 % (code QA), +5-12 pp (localisation de bugs)
- Méthode : semi-formal reasoning avec certificats de preuve structurés
