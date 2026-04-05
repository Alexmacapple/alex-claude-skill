# Template : mode patch (vérification d'équivalence/correction)

Fidèle à l'Appendice A du papier « Agentic Code Reasoning » (Ugare & Chandra, Meta 2026).

---

## Format de sortie attendu

```
## 1. Reformulation
[1-2 phrases : quel patch, quel comportement vérifié]

## 2. Définitions
- D1 : Deux patchs sont équivalents modulo tests si l'exécution de la suite de tests produit les mêmes résultats pass/fail.
- D2 : Seuls les tests F2P (fail-to-pass) et P2P (pass-to-pass) sont pertinents.

## 3. Prémisses
- P1 : **Patch 1** — [fichiers modifiés, lignes, nature du changement]
- P2 : **Patch 2** — [fichiers modifiés, lignes, nature du changement] (si comparaison)
- P3 : **Tests F2P** — [noms, ce qu'ils vérifient]
- P4 : **Tests P2P** — [noms, ce qu'ils vérifient] (si pertinent)
- **Inconnues** : [bibliothèques tierces, config non disponible]

## 4. Périmètre
- Fichiers : [liste avec chemins]
- Fonctions modifiées : [nom, fichier:ligne]
- Dépendances directes : [fonctions appelées, imports]

## 5. Analyse par test

### Analyse test F2P : [nom_du_test]
- Claim F1a : Avec Patch 1, test [nom] [PASS/FAIL] parce que [trace d'exécution — fichier:ligne]
- Claim F1b : Avec Patch 2, test [nom] [PASS/FAIL] parce que [trace d'exécution — fichier:ligne]
- Comparaison : [MÊME/DIFFÉRENT] résultat

### Analyse test P2P : [nom_du_test]
- Claim P1a : Avec Patch 1, comportement [description — fichier:ligne]
- Claim P1b : Avec Patch 2, comportement [description — fichier:ligne]
- Comparaison : [MÊME/DIFFÉRENT] résultat

## 6. Cas limites pertinents aux tests existants
- E1 : [cas limite que les tests exercent] — Patch 1 : [résultat] / Patch 2 : [résultat] — Même résultat : [OUI/NON]
- E2 : [idem]

## 7. Flux de données
- [Variable/valeur] : origine → transformation → consommation
- Points de divergence potentiels : [fichier:ligne]

## 8. Contre-exemple ou preuve d'absence

### Si NON ÉQUIVALENTS :
- Test [nom] [PASS/FAIL] avec Patch 1 parce que [raison — fichier:ligne]
- Test [nom] [FAIL/PASS] avec Patch 2 parce que [raison — fichier:ligne]
- Les patchs produisent des résultats DIFFÉRENTS sur ce test

### Si ÉQUIVALENTS :
- Tous les tests existants produisent des résultats identiques parce que [raison]
- Aucun contre-exemple trouvé après examen de [N] tests

## 9. Conclusion formelle
**[VERDICT]**
- Résultats test avec Patch 1 : [PASS/FAIL par test]
- Résultats test avec Patch 2 : [PASS/FAIL par test]
- Puisque les résultats sont [IDENTIQUES/DIFFÉRENTS], les patchs sont [ÉQUIVALENTS/NON ÉQUIVALENTS]
1. [Justification 1 — fichier:ligne, cite Claim]
2. [Justification 2 — fichier:ligne, cite Claim]
```

*Note : le nombre d'étapes dans ce template (9) dépasse les 7 du processus commun car le mode patch nécessite des sections supplémentaires (définitions, cas limites, contre-exemple). Le processus commun du SKILL.md donne le squelette minimum — ce template le spécialise.*

## Verdicts autorisés

- `PATCH PLAUSIBLEMENT CORRECT` : le patch résout le F2P sans casser les P2P
- `PATCH NON CORRECT` : le patch casse un test P2P ou ne résout pas le F2P, avec contre-exemple
- `PATCHS PLAUSIBLEMENT ÉQUIVALENTS` : aucun contre-exemple trouvé, mêmes résultats F2P et P2P
- `PATCHS NON ÉQUIVALENTS` : contre-exemple identifié (test qui produit des résultats différents)
- `PREUVES INSUFFISANTES` : impossible de conclure sans exécution ou information manquante

## Erreurs fréquentes à éviter (papier Meta, section 4.1)

1. **Traçage d'exécution incomplet** : l'agent suppose le comportement d'une fonction au lieu de tracer le chemin concret — toujours suivre les appels jusqu'à l'implémentation réelle
2. **Sémantique de bibliothèque tierce** : l'agent devine le comportement depuis le nom de la fonction quand le code source n'est pas disponible — vérifier dans `opensrc/` ou conclure `PREUVES INSUFFISANTES`
3. **Différences subtiles ignorées** : l'agent identifie une divergence sémantique mais conclut à tort qu'elle est sans impact sur les tests — toujours tracer jusqu'au résultat du test
