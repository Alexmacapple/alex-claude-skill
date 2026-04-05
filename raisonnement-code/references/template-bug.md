# Template : mode bug (localisation de la cause racine)

Fidèle à l'Appendice B du papier « Agentic Code Reasoning » (Ugare & Chandra, Meta 2026).

---

## Format de sortie attendu

```
## 1. Reformulation
[1-2 phrases : quel bug, quel symptôme observé]

## 2. Phase 1 — Sémantique du test (prémisses formelles)
- T1 : Le test [nom] appelle [méthode(args)] et attend [comportement] — fichier:ligne
- T2 : Le test asserte [condition] — fichier:ligne
- T3 : Le comportement observé est [échec/exception] au lieu de [attendu]
- **Inconnues** : [stack traces absentes, config non disponible]

## 3. Phase 2 — Trace du code (format structuré)

Pour chaque appel significatif depuis le point d'entrée du test :

| Méthode | Fichier:ligne | Comportement | Pertinence |
|---------|--------------|-------------|------------|
| Class.method(args) | src/mod.py:42 | Retourne X | Appelée par T1 |
| Other.func() | src/util.py:15 | Modifie state | Dépendance de method |

Séquence d'appels complète :
- [Appel 1] : fichier:ligne → [effet]
- [Appel 2] : fichier:ligne → [effet]
- ...
- [Point de divergence] : fichier:ligne → [observé vs attendu]

## 4. Phase 3 — Analyse de divergence (claims formels)
- Claim D1 : À [fichier:ligne], [code] produit [comportement] qui contredit la prémisse T[N] parce que [raison]
- Claim D2 : À [fichier:ligne], [code] produit [comportement] qui contredit la prémisse T[N] parce que [raison]

## 5. Flux de données
- [Variable critique] : créée à fichier:ligne, modifiée à fichier:ligne, lue à fichier:ligne
- Point de corruption : [où la valeur diverge de l'attendu]

## 6. Hypothèses concurrentes
- **Hypothèse A** : [zone 1 est la cause] — soutenue par Claim D[N]
- **Hypothèse B** : [zone 2 est la cause] — soutenue par Claim D[N]
- Différenciation : [quel élément départage les deux]

## 7. Conclusion formelle
**[VERDICT]**

Classement des causes probables :
1. [Zone la plus probable — fichier:ligne — soutenue par Claims D1, D2]
2. [Zone secondaire — fichier:ligne — soutenue par Claim D3]
```

*Note : les 4 phases du papier (sémantique du test, trace du code, analyse de divergence, classement) sont intégrées dans nos 7 étapes avec les claims numérotés citant les prémisses.*

## Format d'exploration structuré (pendant la navigation agentic)

Quand le skill explore le dépôt pour localiser le bug, utiliser ce format à chaque fichier lu :

```
### Lecture de [fichier]

HYPOTHÈSE H[N] : [ce qu'on s'attend à trouver et pourquoi ce fichier peut contenir le bug]
EVIDENCE : [ce qui, depuis le test ou les fichiers précédents, soutient cette hypothèse]
CONFIANCE : [haute/moyenne/basse]

### Observations de [fichier]
- O1 : [observation clé avec numéro de ligne]
- O2 : [observation supplémentaire]

### Mise à jour des hypothèses
- H[N] : [CONFIRMÉE | RÉFUTÉE | AFFINÉE] — [explication]

### Non résolu
- [Questions restantes]
- [Autres fichiers/fonctions à examiner]

### Prochaine action
[Pourquoi lire un autre fichier OU pourquoi on a assez de preuves pour conclure]
```

## Verdicts autorisés

- `CAUSE LA PLUS PROBABLE IDENTIFIÉE` : une zone explique le symptôme avec preuve de code (Claims)
- `PLUSIEURS CAUSES PLAUSIBLES` : 2+ zones sans départage possible sans exécution
- `PREUVES INSUFFISANTES` : le code disponible ne permet pas de conclure

## Erreurs fréquentes à éviter (papier Meta, section 4.2)

1. **Bugs par indirection** : le bug est dans une classe non directement invoquée par le test (ex. classe de configuration) — toujours tracer les appels interprocéduraux
2. **Bugs multi-fichiers** : toutes les localisations doivent être identifiées, pas juste la première trouvée
3. **Bugs domaine-spécifique** : signaler quand la résolution nécessite une expertise métier non disponible dans le code
4. **Bugs à régions multiples** : quand le ground truth contient plus de 5 régions à corriger, le classement Top-5 ne suffit pas — signaler la complexité et proposer un découpage
