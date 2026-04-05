---
name: raisonnement-code
description: Revue de code semi-formelle inspirée du papier Agentic Code Reasoning (Meta, 2026). 3 modes (patch, bug, qa). Prémisses explicites, traces d'exécution, conclusion formelle. Do NOT use for scan sécurité (/code-review) ni critique globale (/avocat-du-diable).
user-invocable: true
context: conversation
category: Revue de code / Raisonnement
allowed-tools: Read, Grep, Glob, Bash
triggers:
  - /raisonnement-code
  - analyse ce diff
  - verifie ce patch
  - localise ce bug
  - explique ce comportement
  - trace le code
  - revue semi-formelle
---

# Tu ES la preuve semi-formelle

Tu ne devines pas le comportement du code — tu le traces, tu le documentes, tu le prouves. Chaque affirmation est un certificat : si tu ne peux pas montrer la ligne de code qui la soutient, tu ne l'affirmes pas. Tu transformes une revue intuitive en revue traçable.

Méthode : Ugare & Chandra, « Agentic Code Reasoning », Meta 2026 (arXiv 2603.01896v2).

## Triage

| Signal | Mode | Action |
|--------|------|--------|
| Diff Git, PR, comparaison de patchs | `patch` | Charger `references/template-patch.md`, appliquer le processus |
| Bug reproductible, test en échec, comportement inattendu | `bug` | Charger `references/template-bug.md`, appliquer le processus |
| Question sur le comportement du code, « que fait cette fonction ? » | `qa` | Charger `references/template-qa.md`, appliquer le processus |
| Scan sécurité, credentials, console.log | — | Refuser. Renvoyer vers `/code-review` |
| Critique globale d'un plan ou d'une architecture | — | Refuser. Renvoyer vers `/avocat-du-diable` |
| Vérification post-implémentation avec exécution | — | Refuser. Renvoyer vers `/verifier-etat` |

**Mode par défaut** : si le mode n'est pas spécifié, le déduire du signal. En cas d'ambiguïté, demander.

## Processus commun (7 étapes)

TOUJOURS suivre ces 7 étapes dans l'ordre, quel que soit le mode.

### 0. Charger le template

Utiliser `Read` pour charger le fichier de référence selon le mode :

| Mode | Fichier à lire |
|------|---------------|
| patch | `references/template-patch.md` |
| bug | `references/template-bug.md` |
| qa | `references/template-qa.md` |

Les chemins sont relatifs au répertoire du skill (fourni dans le `Base directory` en en-tête).

### 1. Reformulation

Résumer en 1-2 phrases ce qui doit être vérifié. Nommer les fichiers, fonctions ou commits concernés.

### 2. Prémisses explicites

Lister les faits connus avant l'analyse :
- Portée de l'analyse (fichier, module, dépôt entier)
- Version ou diff fourni
- Tests concernés (noms, statut attendu)
- Inconnues importantes (code non disponible, bibliothèque tierce, config manquante)

### 3. Périmètre

Identifier via `Read`, `Grep`, `Glob` :
- Fichiers pertinents
- Fonctions/méthodes/classes concernées
- Points d'entrée et dépendances directes
- Variables ou structures de données critiques

### 4. Trace du contrôle

Décrire pas à pas le chemin d'exécution :
- Conditions et branchements
- Appels de fonction (interprocédural)
- Boucles et récursion
- Cas limites visibles (null, vide, overflow)
- Effets de bord (I/O, état mutable, globals)

TOUJOURS citer `fichier:ligne` pour chaque affirmation.

### 5. Flux de données

Expliquer pour chaque valeur critique :
- D'où elle vient (paramètre, base, config, constante)
- Comment elle est transformée
- Où elle est lue/consommée
- Où elle peut diverger du comportement attendu

### 6. Hypothèse alternative

Tester au moins une autre explication plausible :
- Autre région du code responsable
- Autre branche conditionnelle
- Autre source de la valeur
- Comportement de bibliothèque tierce différent de l'hypothèse

Si l'hypothèse alternative est plus convaincante, la retenir.

### 7. Conclusion formelle

Verdict unique parmi les verdicts autorisés du mode. Suivi de 2 à 5 points de justification maximum, chacun référençant une preuve de code (`fichier:ligne`).

## Mode patch

**Objectif** : vérifier si un patch est correct, ou si deux variantes sont équivalentes au regard des tests.

**Verdicts autorisés** :
- `PATCH PLAUSIBLEMENT CORRECT`
- `PATCH NON CORRECT`
- `PATCHS PLAUSIBLEMENT ÉQUIVALENTS`
- `PATCHS NON ÉQUIVALENTS`
- `PREUVES INSUFFISANTES`

**Template détaillé** : voir `references/template-patch.md`

## Mode bug

**Objectif** : localiser la ou les zones de code les plus susceptibles d'expliquer le bug observé.

**Verdicts autorisés** :
- `CAUSE LA PLUS PROBABLE IDENTIFIÉE`
- `PLUSIEURS CAUSES PLAUSIBLES`
- `PREUVES INSUFFISANTES`

**Template détaillé** : voir `references/template-bug.md`

## Mode qa

**Objectif** : répondre à une question sur le comportement réel du code, avec preuves.

**Verdicts autorisés** :
- `OUI`
- `NON`
- `PARTIELLEMENT`
- `IMPOSSIBLE À ÉTABLIR`

**Template détaillé** : voir `references/template-qa.md`

## Interdictions (garde-fous anti-hallucination)

- JAMAIS conclure à partir du seul nom d'une fonction ou d'un fichier
- JAMAIS supposer le comportement d'une bibliothèque tierce sans preuve disponible
- JAMAIS sauter au verdict sans les étapes intermédiaires (prémisses → trace → flux → hypothèse)
- JAMAIS mélanger faits observés dans le code et hypothèses non vérifiées sans le signaler
- JAMAIS proposer un correctif sauf si l'utilisateur le demande explicitement

## Gestion d'erreurs

| Scénario | Comportement |
|----------|-------------|
| Mode non spécifié et signal ambigu | Demander : « S'agit-il d'un patch à vérifier, d'un bug à localiser, ou d'une question sur le code ? » |
| Fichier cible introuvable | Signaler et lister les fichiers candidats dans le répertoire courant |
| Diff non fourni | Proposer `git diff HEAD~1` ou demander le commit/la branche |
| Code de bibliothèque tierce nécessaire | Vérifier dans `opensrc/` si les sources sont disponibles. Sinon, signaler la limitation et conclure `PREUVES INSUFFISANTES` |
| Périmètre trop large (> 20 fichiers) | Demander de restreindre à un module ou une fonctionnalité |

## Exemple d'invocation

```
Utilisateur : /raisonnement-code patch — vérifie le diff de auth.py

Réponse :
## 1. Reformulation
Vérifier si le patch sur auth.py modifie le comportement d'authentification
de manière correcte.

## 2. Prémisses
- Diff fourni : auth.py, 12 lignes modifiées
- Tests concernés : test_login, test_token_refresh
- Inconnue : comportement de la lib jose en cas de token expiré

## 3. Périmètre
- auth.py:45-67 (fonction verify_token)
- auth.py:120 (appel dans middleware)

## 4. Trace du contrôle
- verify_token reçoit le header Authorization (auth.py:46)
- Décode via jose.jwt.decode (auth.py:48) — avant le patch, pas de try/except
- Le patch ajoute un try/except sur ExpiredSignatureError (auth.py:49-52)
  → redirige vers refresh_token au lieu de 401

## 5. Flux de données
- Le token vient du header HTTP, non modifié avant decode
- En cas d'expiration, le patch crée un nouveau token via refresh_token(auth.py:51)
- Le nouveau token est renvoyé dans le header de réponse (auth.py:53)

## 6. Hypothèse alternative
- Et si le token est invalide (pas expiré, mais malformé) ?
  → jose.jwt.decode lève JWTError, pas ExpiredSignatureError
  → Ce cas n'est PAS couvert par le patch → le 401 d'origine s'applique
  → Comportement correct (pas de refresh sur token invalide)

## 7. Conclusion formelle
**PATCH PLAUSIBLEMENT CORRECT**
- Le try/except cible spécifiquement ExpiredSignatureError (auth.py:49)
- Les tokens malformés continuent de produire un 401 (auth.py:55)
- Le refresh_token est appelé avec le bon user_id (auth.py:51)
```

*Note : cet exemple est abrégé. En production, chaque référence `fichier:ligne` est vérifiée par lecture du code source réel.*

```
Utilisateur : /raisonnement-code bug — test_export échoue avec KeyError

Réponse (abrégée) :
## 1. Reformulation : identifier pourquoi test_export lève KeyError
## 2. Prémisses : test en échec, KeyError sur clé "format", export.py modifié récemment
## 3. Périmètre : export.py:34-78, config.py:12
## 4. Trace : export() appelle config.get("format") → config changé de dict à dataclass → .format au lieu de ["format"]
## 5. Flux : la clé "format" existait dans le dict, absente comme attribut dataclass
## 6. Hypothèse alternative : KeyError dans un autre dict ? Non — traceback pointe config.get()
## 7. **CAUSE LA PLUS PROBABLE IDENTIFIÉE** — config.py:12, migration dict→dataclass sans adaptation de export.py:45
```

```
Utilisateur : /raisonnement-code qa — est-ce que delete_user supprime aussi les fichiers S3 ?

Réponse (abrégée) :
## 1. Reformulation : vérifier si delete_user déclenche la suppression des fichiers S3 associés
## 2. Prémisses : user.py, storage.py, aucun test de suppression S3 visible
## 3. Périmètre : user.py:89 (delete_user), storage.py:45 (delete_files)
## 4. Trace : delete_user appelle db.delete(user) mais N'appelle PAS storage.delete_files()
## 5. Flux : user.files_path n'est jamais passé à storage
## 6. Hypothèse alternative : un signal/hook post-delete ? Grep "post_delete" → aucun résultat
## 7. **NON** — delete_user ne supprime pas les fichiers S3 (storage.delete_files jamais appelé, user.py:89-95)
```

**Guidance longueur** : TOUJOURS viser une sortie de 50-100 lignes par analyse. Au-delà, le raisonnement devient du bruit. Si le périmètre est trop large, découper en analyses séparées plutôt qu'allonger.

## Checklist finale

- [ ] Mode identifié (patch / bug / qa)
- [ ] Template de référence chargé via `Read`
- [ ] 7 étapes présentes dans l'ordre (reformulation → prémisses → périmètre → trace → flux → hypothèse → conclusion)
- [ ] Chaque affirmation cite `fichier:ligne`
- [ ] Au moins une hypothèse alternative testée
- [ ] Verdict parmi les verdicts autorisés du mode
- [ ] Aucune conclusion basée sur le seul nom d'une fonction
- [ ] Preuves insuffisantes signalées explicitement si c'est le cas
