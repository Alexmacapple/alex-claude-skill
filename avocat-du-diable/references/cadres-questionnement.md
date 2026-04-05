# Cadres de questionnement

Matériel de référence pour l'analyse critique structurée de décisions logicielles, de code, de plans et d'architecture.

---

## 1. Analyse pré-mortem (Gary Klein)

### Ce que c'est

Un pré-mortem suppose que le projet/la décision a déjà échoué et remonte aux causes. Contrairement au post-mortem (qui survient après l'échec), le pré-mortem exploite la rétrospective prospective — la découverte psychologique selon laquelle les gens sont 30 % meilleurs pour identifier les raisons d'un résultat quand ils imaginent qu'il s'est déjà produit.

### Quand l'utiliser

- Avant de livrer une fonctionnalité, une migration ou un changement architectural
- Avant de s'engager dans une direction technique difficile à inverser
- Lors de la revue d'un plan qui « semble correct » mais n'a pas été mis à l'épreuve
- Avant tout déploiement avec migration de données ou changements de schéma

### Processus étape par étape

1. **Cadrer l'échec.** Énoncer : « Nous sommes six mois dans le futur. Cette [fonctionnalité/migration/décision] a été livrée et a causé un incident grave. L'équipe est en salle de crise. »
2. **Générer des scénarios d'échec indépendamment.** Chaque participant (ou chaque passe d'analyse) écrit des scénarios de défaillance spécifiques — pas des risques vagues, mais des récits : « La migration a tourné pendant 47 minutes, a dépassé la fenêtre de maintenance, et a laissé la base de données dans un état incohérent parce que... »
3. **Identifier les échecs les plus plausibles.** Classer par probabilité x impact. Se concentrer sur les échecs à la fois plausibles et qui seraient embarrassants rétrospectivement (« on aurait dû voir ça venir »).
4. **Remonter chaque échec à sa cause racine dans le plan actuel.** Quelle hypothèse, quel test manquant, quel cas non géré aurait causé cet échec ?
5. **Déterminer les actions préventives.** Pour chaque échec plausible : qu'ajouter, changer ou tester pour le prévenir ?

### Exemples de questions pour le contexte logiciel

| Scénario | Question pré-mortem |
|----------|-------------------|
| Nouvel endpoint API | « Cet endpoint a causé une panne de production. Le pager de l'ingénieur d'astreinte a sonné à 3h du matin. Que s'est-il passé ? » |
| Migration de base de données | « La migration a échoué à mi-chemin en production. Qu'est-ce qui différait en prod et qu'on n'avait pas anticipé ? » |
| Lancement de fonctionnalité | « Les utilisateurs sont furieux. Les tickets support ont triplé. Qu'avons-nous mal compris sur leur usage réel ? » |
| Mise à jour de dépendance | « La mise à jour a cassé la production silencieusement — pas d'erreurs, juste un comportement incorrect. Qu'est-ce qui a changé que nos tests ne couvraient pas ? » |
| Optimisation de performance | « L'optimisation a empiré les choses sous charge réelle. Qu'avons-nous raté des patterns de trafic en production ? » |

### Insight clé

La puissance du pré-mortem est qu'il donne aux gens la permission de voix des préoccupations qu'ils supprimeraient autrement. En revue de code, cela se traduit par : « Je ne dis pas que c'est faux, je dis que SI ça échouait, voici comment ça échouerait. »

---

## 2. Inversion (Charlie Munger)

### Ce que c'est

Au lieu de demander « comment réussir ? », demander « qu'est-ce qui garantirait l'échec ? » puis s'assurer qu'aucune de ces conditions n'existe. Le principe de Munger : « Inversez, toujours inversez. » Beaucoup de problèmes sont plus faciles à résoudre à l'envers qu'à l'endroit.

### Quand l'utiliser

- Pour évaluer si une conception est robuste
- Pour revoir les critères d'acceptation — sont-ils suffisants ?
- Pour évaluer la préparation opérationnelle
- Quand un plan semble solide mais qu'on ne peut pas articuler de préoccupation spécifique

### Processus en trois étapes

1. **Définir l'objectif opposé.** Si l'objectif est « un pipeline de traitement de données fiable », l'inverse est « perte ou corruption de données garantie ».
2. **Énumérer les façons d'atteindre l'inverse.** Être exhaustif et spécifique :
   - « Ne jamais valider les schémas d'entrée »
   - « Ignorer les échecs partiels et continuer le traitement »
   - « Pas de clés d'idempotence sur les écritures »
   - « Déployer sans capacité de rollback »
   - « Aucun monitoring sur la profondeur de file ou le retard de traitement »
3. **Vérifier le plan actuel contre chaque point.** Pour chaque condition garantissant l'échec, vérifier que le plan la prévient activement. Tout manque est une constatation.

### Exemples d'application

**Inversion appliquée à un système d'authentification :**

| « Pour garantir une faille de sécurité, nous ferions... » | Vérification |
|-----------------------------------------------|-------|
| Stocker les mots de passe en clair | Bcrypt/argon2 avec sel ? |
| Ne jamais expirer les sessions | TTL de token + rotation de rafraîchissement ? |
| Renvoyer des erreurs différentes pour « utilisateur non trouvé » vs « mauvais mot de passe » | Messages d'erreur uniformes ? |
| Autoriser les tentatives de connexion illimitées | Limitation de débit + verrouillage ? |
| Envoyer les tokens dans les paramètres d'URL | En-têtes uniquement, pas de journalisation ? |
| Faire confiance aux revendications de rôle côté client | Autorisation côté serveur à chaque requête ? |

**Inversion appliquée au déploiement :**

| « Pour garantir un déploiement raté, nous ferions... » | Vérification |
|--------------------------------------------------|-------|
| Déployer vendredi à 17h sans plan de rollback | Fenêtres de déploiement + runbook de rollback ? |
| Exécuter des migrations irréversibles | Migrations rétrocompatibles ? |
| Sauter le déploiement canari/progressif | Déploiement progressif ? |
| N'avoir aucun moyen de vérifier le succès post-déploiement | Vérifications de santé + tests smoke ? |
| Dépendre d'étapes manuelles non documentées | Pipeline automatisé ? |

### Exemples de questions

- « Si on voulait garantir la corruption de données dans ce pipeline, que ferait-on ? Maintenant — l'une de ces conditions est-elle présente ? »
- « Quel est le moyen le plus rapide pour qu'un initié malveillant exploite ceci ? Le prévenons-nous ? »
- « Si on voulait que les utilisateurs abandonnent cette fonctionnalité par frustration, à quoi ressemblerait l'UX ? La nôtre y ressemble-t-elle ? »
- « Qu'est-ce qui rendrait ce système impossible à débugger en production ? »

---

## 3. Questionnement socratique (six types)

### Ce que c'est

Le questionnement socratique est une méthode disciplinée d'exploration de la pensée à travers six catégories de questions. Il n'affirme pas — il révèle les lacunes, les hypothèses et les contradictions en posant les bonnes questions dans l'ordre.

### Quand l'utiliser

- Lors d'une revue de code ou de conception
- Pour évaluer une proposition technique
- Quand quelqu'un (y compris soi-même) est confiant dans une approche
- Pour faire émerger les hypothèses implicites

### Les six types

#### 3.1 Questions de clarification

**Objectif :** S'assurer que l'affirmation ou la décision est bien définie. Les énoncés vagues cachent de la complexité.

| Question | Quand l'utiliser |
|----------|-------------|
| « Que voulez-vous dire exactement par [terme] ? » | Quand du jargon ou des termes ambigus sont utilisés (« scalable », « robuste », « simple ») |
| « Pouvez-vous donner un exemple concret de comment ça fonctionnerait ? » | Quand la description est abstraite |
| « Quelle est l'action utilisateur spécifique qui déclenche ce chemin de code ? » | Lors de la revue de logique métier |
| « À quoi ressemble le « terminé » pour ceci ? Quel est le test d'acceptation ? » | Quand le périmètre est flou |
| « Quand vous dites « gérer les erreurs gracieusement », que voit l'utilisateur ? » | Quand la gestion d'erreur est décrite mais non spécifiée |

#### 3.2 Sonder les hypothèses

**Objectif :** Faire émerger et tester les croyances prises pour acquises. La plupart des défauts de conception viennent d'hypothèses non testées.

| Question | Quand l'utiliser |
|----------|-------------|
| « Que supposons-nous sur les données d'entrée qui pourrait ne pas tenir ? » | Traitement de données, endpoints API |
| « Supposons-nous que ce service tiers sera toujours disponible ? » | Points d'intégration |
| « Et si l'utilisateur ne suit pas le flux attendu ? » | Décisions UI/UX |
| « Supposons-nous que les données tiennent en mémoire ? » | Pipelines de traitement |
| « Et si cette table grossit de 100x ? Le plan de requête tient-il encore ? » | Conception de base de données |
| « Supposons-nous que les déploiements se font sans requêtes en vol ? » | Plans de migration/déploiement |
| « Y a-t-il une hypothèse ici sur l'ordre ou le timing ? » | Systèmes distribués, traitement d'événements |

#### 3.3 Sonder les preuves / le raisonnement

**Objectif :** Examiner la base d'une affirmation. « Comment sait-on que c'est vrai ? »

| Question | Quand l'utiliser |
|----------|-------------|
| « Quelles données soutiennent ce choix de conception ? » | Quand un choix est présenté comme évident |
| « Ce pattern a-t-il été testé dans des conditions proches de la production ? » | Affirmations de performance |
| « D'où vient l'exigence de [X] ? Peut-on la vérifier ? » | Quand on construit sur des exigences supposées |
| « Quelle est la preuve que les utilisateurs ont réellement besoin de ça ? » | Décisions de fonctionnalités |
| « Comment sait-on que l'implémentation actuelle est réellement le goulot d'étranglement ? » | Efforts d'optimisation |

#### 3.4 Questionner les perspectives / points de vue

**Objectif :** Considérer des angles alternatifs. Que penserait quelqu'un avec un rôle, un contexte ou une expertise différente ?

| Question | Quand l'utiliser |
|----------|-------------|
| « Comment l'ingénieur d'astreinte vivrait-il ça à 3h du matin ? » | Préparation opérationnelle |
| « Que penserait un nouveau membre de l'équipe en lisant ce code ? » | Clarté du code |
| « À quoi ça ressemble du point de vue de l'attaquant ? » | Revue de sécurité |
| « Que dirait le DBA de ce pattern de requêtes ? » | Utilisation de la base de données |
| « Si on héritait de cette base de code, qu'est-ce qui nous frustrerait ? » | Qualité du code |
| « De quoi l'équipe support client aurait-elle besoin quand ça casse ? » | Gestion d'erreur, observabilité |

#### 3.5 Sonder les implications / conséquences

**Objectif :** Suivre la décision jusqu'à sa conclusion logique. Que se passe-t-il ensuite ? Et après ?

| Question | Quand l'utiliser |
|----------|-------------|
| « Si on fait ça, à quoi ça nous engage en termes de maintenance ? » | Décisions architecturales |
| « Quel est le chemin de migration si cette approche ne passe pas à l'échelle ? » | Choix technologiques |
| « Si ça réussit massivement, qu'est-ce qui casse en premier ? » | Planification de capacité |
| « Qu'est-ce qui devient plus difficile à changer après qu'on aura livré ? » | Évaluation de réversibilité |
| « Quelles autres équipes ou systèmes sont affectés par ce changement ? » | Rayon d'explosion |
| « Si on ajoute cette colonne maintenant, à quoi ressemble la migration dans 2 ans ? » | Conception de schéma |

#### 3.6 Méta-questions (questions sur la question)

**Objectif :** Examiner le cadrage lui-même. Résout-on le bon problème ?

| Question | Quand l'utiliser |
|----------|-------------|
| « Pourquoi est-ce la question qu'on se pose ? Y a-t-il un meilleur cadrage ? » | Quand on est bloqué ou qu'on tourne en rond |
| « Résout-on le symptôme ou la cause racine ? » | Corrections de bugs, contournements |
| « Est-ce réellement notre problème à résoudre, ou devrait-il être géré ailleurs ? » | Décisions de périmètre/frontière |
| « Que ferait-on si on ne pouvait absolument pas utiliser cette approche ? » | Quand on est fixé sur une seule solution |
| « Optimisons-nous la bonne métrique ? » | Décisions de performance/business |

---

## 4. Steel-manning

### Ce que c'est

Avant de critiquer une décision ou une approche, articuler la version la plus forte possible de pourquoi c'est raisonnable. C'est l'opposé d'un homme de paille — on construit le meilleur argument POUR l'approche, puis on évalue si la critique tient toujours.

### Pourquoi c'est important pour la calibration

- Empêche les réactions instinctives « c'est faux » qui passent à côté du contexte
- Force à comprendre les compromis que l'auteur a réellement considérés
- Rend la critique finale plus crédible et spécifique
- Détecte les cas où l'approche est en fait correcte et c'est nous qui ratons quelque chose

### Quand l'utiliser

- Avant chaque critique — ça devrait être la première étape par défaut
- Quand notre instinct dit « c'est faux » — cet instinct est souvent juste, mais le steel-man garantit que la critique est précise
- Lors de la revue de code de quelqu'un avec plus de contexte domaine que nous

### Processus étape par étape

1. **Identifier la décision.** Quel choix spécifique a été fait ? (Pas un vague « c'est mauvais » — nommer la décision exacte.)
2. **Lister les contraintes de l'auteur.** Pression temporelle, rétrocompatibilité, expertise de l'équipe, patterns existants, exigences métier.
3. **Construire le meilleur argument POUR cette approche.** « Cette approche est raisonnable parce que... »
4. **Identifier ce qui devrait être vrai pour que cette approche soit optimale.** « C'est le bon choix SI... »
5. **Maintenant évaluer :** Ces conditions sont-elles réellement vraies ? Si non, qu'est-ce qui change spécifiquement ?

### Exemple

**Décision :** Une équipe a choisi le polling au lieu des WebSockets pour les mises à jour en temps réel.

| Étape | Analyse |
|------|----------|
| Steel-man | « Le polling est plus simple à implémenter, débugger et déployer. Il fonctionne à travers tous les proxies et load balancers sans configuration spéciale. L'équipe n'a pas d'expérience WebSocket, et la fréquence de mise à jour (toutes les 30s) ne nécessite pas du vrai temps réel. Le coût opérationnel de maintenance des connexions WebSocket à l'échelle n'est pas trivial. » |
| Conditions | « C'est optimal SI une latence de mise à jour de 30s est acceptable, SI la charge de polling est gérable à l'échelle attendue, SI il n'y a pas d'exigence future pour des mises à jour sub-seconde. » |
| Évaluation | « L'exigence métier dit « quasi temps réel » que le PM a défini comme <5s. Le polling à 30s ne satisfait pas ça. De plus, au volume d'utilisateurs projeté, le polling crée 200 req/s que les WebSockets élimineraient. Le steel-man est fort sur la simplicité opérationnelle mais casse sur l'exigence de latence. » |

### Exemples de questions

- « Quel est l'argument le plus fort pour garder ça exactement tel quel ? »
- « Dans quelles conditions serait-ce l'approche idéale ? »
- « Quelles contraintes ont fait de ceci le choix pragmatique ? »
- « Si je devais défendre cette approche en revue de conception, que dirais-je ? »
- « Qu'est-ce que je rate du contexte qui rendrait ceci raisonnable ? »

---

## 5. Six chapeaux de réflexion (Edward de Bono)

### Ce que c'est

Une méthode pour examiner une décision depuis six perspectives distinctes, une à la fois. La valeur réside dans le changement de perspective délibéré — la plupart des gens restent sur un ou deux modes et ignorent le reste.

### Quand l'utiliser

- Quand une décision a été prise rapidement et semble « évidente »
- Quand un groupe est bloqué dans un seul mode de pensée (ex. ne discuter que des risques, ou que des bénéfices)
- Pour une revue structurée d'un document de décision architecturale (ADR)

### Les quatre chapeaux les plus pertinents pour la revue logicielle

#### Chapeau noir — Risques et problèmes

Le chapeau de l'avocat du diable. Qu'est-ce qui peut mal tourner ?

**Processus :** Supposer que ça va échouer. Énumérer chaque mode de défaillance, risque et faiblesse.

| Question | Focus |
|----------|-------|
| « Quel est le pire cas si ça échoue ? » | Évaluation d'impact |
| « Où est le point unique de défaillance ? » | Résilience |
| « Que se passe-t-il quand la dépendance est en panne ? » | Tolérance aux pannes |
| « Quelle est la surface d'attaque de sécurité ? » | Sécurité |
| « Où sera-ce pénible à maintenir dans un an ? » | Dette technique |

#### Chapeau blanc — Données manquantes

Que sait-on ? Que ne sait-on pas ? Que doit-on découvrir ?

**Processus :** Éliminer opinions et hypothèses. Se concentrer uniquement sur les faits, les données et les lacunes.

| Question | Focus |
|----------|-------|
| « Quelle est la latence réellement mesurée, pas celle attendue ? » | Performance réelle vs. supposée |
| « Combien d'utilisateurs vont réellement emprunter ce chemin de code ? » | Données d'utilisation |
| « A-t-on des données de production sur les taux d'erreur de cette intégration ? » | Preuves empiriques |
| « Que ne sait-on pas sur le pattern d'utilisation du client ? » | Inconnues inconnues |
| « A-t-on fait des tests de charge, ou estime-t-on ? » | Qualité des données |

#### Chapeau vert — Alternatives

Exploration créative. Que pourrait-on faire d'autre ?

**Processus :** Générer des options sans les juger. Quantité avant qualité dans cette phase.

| Question | Focus |
|----------|-------|
| « Et si on ne construisait pas ça du tout ? Quel est le contournement manuel ? » | Vérification de nécessité |
| « Quelle est une architecture complètement différente qui résout ça ? » | Perspective fraîche |
| « Que ferait [entreprise connue pour ça] ? » | Emprunt de patterns |
| « Et si on découpait ça en deux problèmes plus simples ? » | Décomposition |
| « Quelle est la version la plus simple qui serait encore utile ? » | Pensée MVP |

#### Chapeau bleu — Méta/Processus

Penser à la pensée. Pose-t-on les bonnes questions ?

**Processus :** Prendre du recul par rapport au contenu. Évaluer la qualité de l'analyse elle-même.

| Question | Focus |
|----------|-------|
| « A-t-on parlé aux gens qui vont réellement utiliser/maintenir ça ? » | Couverture des parties prenantes |
| « Passe-t-on du temps sur les zones à plus haut risque ? » | Priorisation |
| « Quelle décision prend-on réellement en ce moment ? » | Clarté du périmètre |
| « A-t-on les bonnes personnes dans cette discussion ? » | Couverture d'expertise |
| « Quels sont nos critères de décision ? Comment saura-t-on quelle option est meilleure ? » | Cadre de décision |

### Comment appliquer séquentiellement

Lors de la revue d'une décision ou d'un plan :

1. **Bleu** (2 min) : Qu'évaluons-nous ? Qu'est-ce qui compte le plus ?
2. **Blanc** (5 min) : Que savons-nous réellement ? Quelles données manquent ?
3. **Vert** (5 min) : Quelles alternatives existent ? (Lister sans juger.)
4. **Noir** (10 min) : Qu'est-ce qui peut mal tourner avec l'approche proposée ?
5. **Steel-man** (3 min) : Quel est l'argument le plus fort POUR cette approche ?
6. **Bleu** (2 min) : Compte tenu de tout ça, quelle est notre recommandation ?

---

## 6. Cinq pourquoi (application inversée)

### Ce que c'est

Les cinq pourquoi classiques remontent d'un problème à sa cause racine. En application inversée pour la revue de décision, on remonte d'une décision à sa motivation sous-jacente — révélant si la justification énoncée soutient réellement le choix.

### Quand l'utiliser

- Lors de la revue d'une décision de conception qui semble prise par convention
- Quand la justification est « c'est comme ça qu'on a toujours fait » ou « c'est la bonne pratique »
- Quand un choix technique semble déconnecté du problème réel

### Processus étape par étape

Partir de la décision et demander « pourquoi cette approche a-t-elle été choisie ? » de façon répétée :

1. **Pourquoi cette approche ?** (Justification de surface)
2. **Pourquoi est-ce important ?** (Préoccupation sous-jacente)
3. **Pourquoi est-ce la contrainte ?** (Contrainte réelle vs. supposée)
4. **Pourquoi cette contrainte ne peut-elle pas être changée ?** (Fixe vs. modifiable)
5. **Pourquoi est-ce la meilleure façon d'adresser cette préoccupation racine ?** (Alternatives)

### Exemple : « On a choisi une architecture microservices »

| Niveau | Question | Réponse |
|-------|----------|--------|
| Pourquoi 1 | « Pourquoi les microservices ? » | « On a besoin de déployabilité indépendante. » |
| Pourquoi 2 | « Pourquoi avez-vous besoin de déployabilité indépendante ? » | « Les différentes fonctionnalités ont des cadences de release différentes. » |
| Pourquoi 3 | « Pourquoi les fonctionnalités ont-elles des cadences de release différentes ? » | « L'équipe paiements livre hebdomadairement, l'équipe recherche livre quotidiennement. » |
| Pourquoi 4 | « Pourquoi ne peuvent-elles pas livrer au même rythme ? » | « Les paiements nécessitent une revue de conformité avant chaque release. » |
| Pourquoi 5 | « Existe-t-il un moyen plus simple de contrôler les releases paiements sans découper toute l'architecture ? » | « ...en fait, un feature flag + une porte d'approbation sur le pipeline CI pourrait fonctionner. » |

### Exemple : « On utilise Redis pour le cache »

| Niveau | Question | Réponse |
|-------|----------|--------|
| Pourquoi 1 | « Pourquoi Redis ? » | « On a besoin de cache pour la performance. » |
| Pourquoi 2 | « Pourquoi la performance est-elle un problème ? » | « Le tableau de bord charge lentement. » |
| Pourquoi 3 | « Pourquoi le tableau de bord charge-t-il lentement ? » | « Il fait 12 appels API au montage. » |
| Pourquoi 4 | « Pourquoi 12 appels API ? » | « Chaque widget récupère ses données indépendamment. » |
| Pourquoi 5 | « Un seul endpoint agrégé pourrait-il éliminer le besoin de cache ? » | « ...ça résoudrait la latence sans ajouter d'infrastructure. » |

### Exemples de questions pour usage général

- « Pourquoi cette bibliothèque/framework/outil a-t-il été choisi plutôt que les alternatives ? »
- « Pourquoi est-ce une exigence ferme vs. une préférence ? »
- « Pourquoi le système amont ne peut-il pas fournir ces données dans le format dont on a besoin ? »
- « Pourquoi est-ce notre responsabilité plutôt que celle de l'appelant ? »
- « Pourquoi a-t-on besoin de cette couche d'abstraction ? »

### Insight clé

Les cinq pourquoi inversés révèlent fréquemment qu'une solution complexe adresse un symptôme plutôt que le problème racine. Le cinquième « pourquoi » pointe souvent vers une intervention plus simple à un niveau différent.

---

## Guide de sélection des cadres

| Situation | Cadre principal | Cadre de soutien |
|-----------|------------------|---------------------|
| Revue d'un plan avant exécution | Pré-mortem | Inversion |
| Évaluation d'une décision technique spécifique | Cinq pourquoi (inversés) | Steel-manning |
| Revue de conception complète | Six chapeaux de réflexion | Socratique (tous types) |
| « Ça semble faux mais je ne sais pas dire pourquoi » | Inversion | Pré-mortem |
| Questionner une proposition confiante | Steel-manning d'abord | Puis socratique hypothèses |
| Explorer si on résout le bon problème | Socratique méta-questions | Cinq pourquoi (inversés) |
| Évaluer la préparation opérationnelle | Pré-mortem | Inversion |
| Revoir le code/PR de quelqu'un d'autre | Steel-manning d'abord | Socratique clarification |

---

## Combiner les cadres : séquence recommandée

Pour une revue approfondie de toute décision significative :

1. **Steel-man** — Comprendre pourquoi cette approche est raisonnable
2. **Socratique clarification** — S'assurer que la décision est bien définie
3. **Cinq pourquoi (inversés)** — Remonter à la motivation racine
4. **Inversion** — Énumérer les conditions d'échec
5. **Pré-mortem** — Narrer des scénarios d'échec spécifiques
6. **Socratique implications** — Suivre les conséquences vers l'avant

Cette séquence va de la compréhension à la remise en question — elle construit la crédibilité avant la critique, ce qui rend la critique plus efficace et plus susceptible de faire émerger de vrais problèmes plutôt que des préférences stylistiques.
