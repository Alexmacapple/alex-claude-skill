# Patterns de sortie

Utiliser ces patterns quand un skill doit produire une sortie cohérente et de qualité.

## Pattern template

Fournir des templates pour le format de sortie. Ajuster le niveau de rigueur selon les besoins.

**Pour des exigences strictes (réponses API, formats de données) :**

```markdown
## Structure du rapport

TOUJOURS utiliser cette structure exacte :

# [Titre de l'analyse]

## Résumé exécutif
[Un paragraphe synthétisant les conclusions clés]

## Conclusions clés
- Conclusion 1 avec données à l'appui
- Conclusion 2 avec données à l'appui
- Conclusion 3 avec données à l'appui

## Recommandations
1. Recommandation actionnable spécifique
2. Recommandation actionnable spécifique
```

**Pour des directives souples (quand l'adaptation est utile) :**

```markdown
## Structure du rapport

Voici un format par défaut sensé, mais adapter selon le jugement :

# [Titre de l'analyse]

## Résumé exécutif
[Vue d'ensemble]

## Conclusions clés
[Adapter les sections selon les découvertes]

## Recommandations
[Adapter au contexte spécifique]

Ajuster les sections selon le type d'analyse.
```

## Pattern exemples

Pour les skills où la qualité de la sortie dépend d'exemples, fournir des paires entrée/sortie :

```markdown
## Format des messages de commit

Générer des messages de commit selon ces exemples :

**Exemple 1 :**
Entrée : Ajout de l'authentification utilisateur avec tokens JWT
Sortie :
```
feat(auth): implémentation de l'authentification JWT

Ajout du endpoint de connexion et du middleware de validation des tokens
```

**Exemple 2 :**
Entrée : Correction du bug d'affichage incorrect des dates dans les rapports
Sortie :
```
fix(reports): correction du formatage des dates dans la conversion de fuseaux

Utilisation cohérente des timestamps UTC dans la génération de rapports
```

Suivre ce style : type(portée): description brève, puis explication détaillée.
```

Les exemples aident Claude à comprendre le style et le niveau de détail attendus plus clairement que les descriptions seules.
