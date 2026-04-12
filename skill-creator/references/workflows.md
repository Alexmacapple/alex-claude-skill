# Patterns de workflows

## Workflows séquentiels

Pour les tâches complexes, décomposer les opérations en étapes séquentielles claires. Il est souvent utile de donner à Claude une vue d'ensemble du processus au début du SKILL.md :

```markdown
Le remplissage d'un formulaire PDF suit ces étapes :

1. Analyser le formulaire (exécuter analyze_form.py)
2. Créer le mapping des champs (éditer fields.json)
3. Valider le mapping (exécuter validate_fields.py)
4. Remplir le formulaire (exécuter fill_form.py)
5. Vérifier la sortie (exécuter verify_output.py)
```

## Workflows conditionnels

Pour les tâches avec logique de branchement, guider Claude à travers les points de décision :

```markdown
1. Déterminer le type de modification :
   **Création de nouveau contenu ?** → Suivre le « Workflow de création » ci-dessous
   **Édition de contenu existant ?** → Suivre le « Workflow d'édition » ci-dessous

2. Workflow de création : [étapes]
3. Workflow d'édition : [étapes]
```
