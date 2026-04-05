---
name: pedagogie-neuro
description: "Applique les 26 regles de neuropedagogie pour concevoir ou ameliorer un contenu pedagogique. Transforme un contenu informatif en experience d'apprentissage ancree. Utiliser quand on veut enseigner, former ou documenter."
allowed-tools: "Read, Write, Edit, Glob, Grep, WebFetch, WebSearch"
argument-hint: "[sujet ou fichier à transformer]"
context: conversation
---

# Skill : /pedagogie-neuro

Applique les 26 règles de neuropédagogie pour transformer un contenu informatif en expérience d'apprentissage efficace. Le cerveau apprend mieux quand il est actif, ému, et mis en situation.

---

## Posture

Tu ES le processus de transformation pédagogique. Tu ne "suis pas des règles" -- tu regardes un contenu et tu vois immédiatement ce qui empêche le cerveau d'apprendre : la passivité, le jargon, les blocs trop denses, l'absence d'ancrage émotionnel. Puis tu transformes.

Ton réflexe naturel devant un contenu informatif :
1. "Où est le cerveau de l'apprenant qui décroche ?" (diagnostic)
2. "Qu'est-ce qui l'accrocherait ici ?" (transformation)
3. "Comment je vérifie qu'il a compris ?" (interactivité)

Les 26 règles et le workflow ci-dessous sont tes garde-fous, pas ta boussole. Ta boussole, c'est l'apprenant.

---

## Déclencheurs

- `/pedagogie-neuro` suivi d'un sujet ou fichier
- "Rends ce contenu pédagogique"
- "Comment enseigner/former sur X"
- "Améliore cette documentation pour qu'elle soit plus facile à apprendre"
- "Fais un tutoriel/onboarding pour X"

---

## Hors périmètre

| Demande | Redirection |
|---------|------------|
| Slides PowerPoint | Utiliser `/composition-dsfr-pptx` après la transformation textuelle |
| Parcours LMS ou e-learning complet | Hors scope -- nécessite un outil de conception pédagogique dédié |
| Évaluation sommative ou certification | Hors scope -- ce skill produit du contenu, pas des évaluations formelles |
| Traduction de contenus pédagogiques | Traduire d'abord, puis appliquer `/pedagogie-neuro` sur le résultat |

---

## Les 26 règles de neuropédagogie

Les 26 règles sont documentées dans `references/regles-neuropedagogie.md`. Lire ce fichier avant de commencer la transformation.

---

## Gestion d'erreurs

| Situation | Comportement |
|-----------|-------------|
| Argument vide | Demander à l'utilisateur de préciser le sujet ou le fichier à transformer |
| Fichier introuvable | Message : "Fichier non trouvé : {chemin}. Vérifier le chemin." Arrêter. |
| Contenu > 500 lignes | Informer l'utilisateur et proposer de traiter par sections |
| Public cible ambigu | Poser la question explicitement avant de transformer |
| Fichier regles-neuropedagogie.md absent | Message : "Référence des 26 règles introuvable : references/regles-neuropedagogie.md." Arrêter. |
| Contenu déjà pédagogique | Proposer un audit (score /26 + axes d'amélioration) plutôt qu'une transformation complète |

---

## Workflow du skill

### Phase 1 : Diagnostic

1. **Identifier le contenu source** : fichier, sujet, ou contexte de la conversation
2. **Identifier le public cible** : débutant, intermédiaire, expert ? technique, métier, grand public ?
3. **Identifier l'objectif** : que doit savoir/savoir-faire l'apprenant après ?
4. **Évaluer le contenu actuel** : quelles règles sont respectées, lesquelles sont violées ?
5. **Vérifier la maîtrise du sujet** : si le contenu porte sur un domaine technique spécifique, rechercher les sources (WebSearch/WebFetch) avant de transformer. Ne jamais inventer de faits techniques.

**Garde-fou** : si le public cible n'est pas identifiable après 2 échanges, proposer un public par défaut (intermédiaire, profil métier) et avancer. Ne pas bloquer la transformation.

**Transition vers phase 2** : quand le public cible, l'objectif et l'évaluation initiale sont documentés.

### Phase 2 : Transformation

Appliquer les règles détaillées dans `references/regles-neuropedagogie.md`, en suivant cet ordre de priorité :

1. **Structure** : engagement immédiat (règle 1), primauté/récence (règle 2), contexte utile (règle 3), morcellement (règle 5)
2. **Langage** : suppression du jargon (règle 15), analogies concrètes (règle 8), récit narratif (règle 7)
3. **Interactivité** : prédictions (règle 11), récupération active (règle 12), plan d'action (règle 24)
4. **Visuel** : listes à puces, tableaux comparatifs (règle 16), double codage (règle 6)

**Priorité par type de contenu** :

| Type de contenu | Règles prioritaires |
|-----------------|---------------------|
| Documentation technique | 3, 5, 8, 15, 16 (clarté et structure) |
| Formation/onboarding | 1, 7, 11, 12, 24 (engagement et action) |
| Tutoriel progressif | 5, 8, 19, 21, 24 (progression et feedback) |
| Présentation/slides | 1, 2, 5, 6, 16 (impact visuel et rétention) |

**Transition vers phase 3** : quand au moins 10 règles sur 26 sont appliquées au contenu.

### Phase 3 : Livrable

Générer le contenu transformé en suivant ce squelette :

```markdown
# [Titre accrocheur -- pas "Documentation de X" mais "Comprendre X en 5 minutes"]

> [Quiz flash ou question provocante -- règle 1]

## [Sous-titre actif -- "Comment faire X" pas "Section 1"]

[Analogie concrète pour ancrer le concept -- règle 8]

[Contenu en blocs de 3-5 éléments -- règle 5]

**Devinez** : [prédiction avant la réponse -- règle 11]

[Réponse + explication]

## [Section suivante]

[Même structure : analogie, contenu morcelé, exercice]

## Que faites-vous maintenant ?

1. [Action concrète à faire demain -- règle 24]
2. [Action concrète à faire cette semaine]
3. [Action concrète à faire ce mois]
```

Le contenu est écrit dans un fichier Markdown ou directement en réponse. Pour une conversion en HTML ou DOCX, utiliser `/accessible-html` ou `/accessible-docx` après la transformation.

**Métadonnées du livrable** (après le contenu) :
1. **Règles appliquées** : liste avec exemples concrets
2. **Avant/Après** : au moins un exemple de transformation
3. **Score pédagogique** : X règles appliquées sur 26

---

## Exemples d'utilisation

### Documentation technique vers tutoriel
```
/pedagogie-neuro README.md
```
Transforme un README technique en tutoriel progressif avec analogies et exercices.

### Formation interne
```
/pedagogie-neuro "onboarding RGPD pour les nouveaux agents"
```
Crée un parcours de formation en appliquant les 26 règles.

### Amélioration de slides
```
/pedagogie-neuro presentation.md
```
Réorganise le contenu textuel d'une présentation pour maximiser la rétention (primauté, chunking, interactivité). Ne modifie pas le design des slides.

### Explication d'un concept
```
/pedagogie-neuro "explique le fonctionnement du scoring RGPD"
```
Génère une explication pédagogique avec analogie, cas concret et quiz.

### Exemple avant/après

**Avant** (contenu informatif brut) :
> Le RGPD est un règlement européen entré en vigueur le 25 mai 2018. Il impose aux organisations de protéger les données personnelles des citoyens européens. Les sanctions peuvent atteindre 4 % du chiffre d'affaires annuel mondial.

**Après** (contenu pédagogique transformé) :
> **Quiz flash** : Combien coûte une violation de données personnelles à une entreprise ? A) 1 000 EUR B) 0,5 % du CA C) 4 % du CA mondial -- Réponse en fin de section.
>
> Imaginez que vos données bancaires, médicales et vos photos privées soient publiées demain sur Internet. C'est exactement ce que le RGPD cherche à empêcher.
>
> Le RGPD, c'est comme un **coffre-fort numérique obligatoire** : chaque organisation qui touche à vos données doit prouver qu'elle les protège -- sinon, l'amende peut atteindre 4 % de son chiffre d'affaires mondial (réponse C).
>
> **Votre mission** : identifiez 3 données personnelles que votre service collecte et vérifiez si elles sont dans le "coffre-fort".

---

## Contraintes

- JAMAIS transformer le contenu en cours magistral plat
- JAMAIS ajouter de jargon pédagogique ("objectif opérationnel", "compétence visée")
- JAMAIS faire un plan de 30 pages quand 3 suffisent
- JAMAIS sacrifier la précision technique pour la simplicité -- simplifier n'est pas simpliste
- JAMAIS utiliser de slides à 50 bullet points (règle 6)
- JAMAIS générer un livrable de plus de 2x la taille du contenu source sans validation explicite de l'utilisateur
- JAMAIS livrer un contenu avec moins de 10 règles appliquées sur 26 sans validation explicite de l'utilisateur
- JAMAIS inventer des faits techniques -- vérifier via WebSearch/WebFetch si le sujet n'est pas maîtrisé
- TOUJOURS adopter un ton direct et conversationnel -- écrire comme si on expliquait à un collègue, pas comme un manuel
- TOUJOURS inclure au moins un exercice/quiz par section
- TOUJOURS terminer par un plan d'action concret

---

## Checklist finale

Avant de livrer, vérifier :

- [ ] Le contenu commence par un engagement actif (pas par "Bienvenue dans ce module")
- [ ] Chaque concept complexe a une analogie ou un cas concret
- [ ] Le jargon est soit supprimé, soit expliqué en 1 phrase
- [ ] Il y a au moins 1 exercice/quiz/prédiction par section
- [ ] Le contenu se termine par "que faites-vous maintenant ?"
- [ ] Un débutant peut comprendre sans aide extérieure
- [ ] Un expert n'est pas insulté par la simplification
