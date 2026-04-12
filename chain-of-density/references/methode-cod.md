# Principes de la méthode Chain-of-Density

**Référence** : Adams et al., 2023 — « From Sparse to Dense: GPT-4 Summarization with Chain of Density Prompting »

- Chaque itération **ajoute** 1-3 entités et **compresse** le texte existant pour maintenir un nombre de mots constant
- Ne jamais supprimer d'entités déjà intégrées — seulement ajouter et compresser
- Le résumé doit rester auto-suffisant (compréhensible sans le texte source)

## Critères des entités manquantes (5 critères du paper)

| Critère | Description |
|---------|-------------|
| **Pertinente** | Centrale au propos du texte, pas périphérique |
| **Spécifique** | Nom propre, chiffre, terme technique, date, lieu — pas une notion vague |
| **Nouvelle** | Absente du résumé précédent (vérifier explicitement) |
| **Fidèle** | Présente telle quelle dans le texte source (pas de reformulation inventive) |
| **Anywhere** | Peut provenir de n'importe quelle partie du texte source (début, milieu, fin) |
