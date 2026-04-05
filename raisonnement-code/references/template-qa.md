# Template : mode qa (question sur le comportement du code)

Fidèle à l'Appendice D du papier « Agentic Code Reasoning » (Ugare & Chandra, Meta 2026).

---

## Format de sortie attendu

```
## 1. Reformulation
[La question reformulée de manière précise et vérifiable]

## 2. Prémisses
- **Portée** : [fichier, module, dépôt entier]
- **Langage** : [Python, Java, C++, TypeScript, etc.]
- **Contexte** : [version, framework, configuration connue]
- **Inconnues** : [ce qu'on ne peut pas vérifier sans exécution]

## 3. Périmètre
- Fichiers pertinents : [liste]
- Fonctions clés : [nom — fichier:ligne]

## 4. Table de trace des fonctions

| Fonction | Fichier:ligne | Paramètres | Retour | Comportement VÉRIFIÉ |
|----------|--------------|------------|--------|---------------------|
| func_a | src/mod.py:42 | x: int | bool | Retourne True si x > 0 |
| func_b | src/mod.py:67 | s: str | None | Modifie self.state |

## 5. Analyse de flux de données

Pour chaque variable critique :
- **Variable** : [nom]
  - Créée à : [fichier:ligne]
  - Modifiée à : [fichier:ligne(s), ou JAMAIS MODIFIÉE]
  - Utilisée à : [fichier:ligne(s)]

Propriétés sémantiques avec preuves :
- **Propriété 1** : [affirmation] — preuve : fichier:ligne
- **Propriété 2** : [affirmation] — preuve : fichier:ligne
- **Propriété 3** : [affirmation] — preuve : fichier:ligne

## 6. Vérification d'hypothèse alternative

- Si la réponse opposée était vraie, quelle preuve existerait ?
- Recherché : [ce qu'on a cherché dans le code]
- Trouvé : [ce qu'on a trouvé — citer fichier:ligne]
- Conclusion : [RÉFUTÉE | SOUTENUE]

## 7. Conclusion formelle
**[VERDICT]**
[Réponse directe à la question avec preuves explicites]
1. [Justification 1 — fichier:ligne]
2. [Justification 2 — fichier:ligne]
```

## Verdicts autorisés

- `OUI` : le comportement décrit dans la question est confirmé par le code
- `NON` : le comportement décrit est contredit par le code
- `PARTIELLEMENT` : le comportement est vrai dans certains cas, faux dans d'autres
- `IMPOSSIBLE À ÉTABLIR` : le code disponible ne permet pas de conclure

## Erreurs fréquentes à éviter (papier Meta, section 4.3)

1. **Confiance excessive** : un raisonnement élaboré peut mener à une conclusion fausse si un handler downstream est manqué — toujours vérifier le code appelant ET le code appelé
2. **Confusion map.at() vs map[]** : les différences subtiles entre méthodes similaires sont une source fréquente d'erreur — tracer le comportement exact
3. **Négliger les initialisations** : une variable peut être initialisée à une valeur qui rend un chemin de code impossible — toujours remonter à la création
