# Angles morts de l'IA/LLM dans le développement logiciel

Où les assistants de codage IA (y compris Claude) échouent systématiquement en écrivant, relisant et raisonnant sur du logiciel. Cette référence existe pour l'auto-conscience — pour attraper des patterns dans le travail généré par IA que les humains devraient scruter.

---

## Profil de risque quantifié

Recherches de l'analyse GitClear (2024-2025) et de l'étude CodeRabbit sur 470 dépôts :

| Métrique | IA vs. Humain |
|--------|-------------|
| Taux global d'introduction de bugs | 1,7x plus élevé |
| Erreurs de logique | 75 % plus fréquentes |
| Erreurs de concurrence | 2x plus fréquentes |
| Qualité de gestion d'erreur | 2x pire |
| Taux de réécriture de code (edit-then-revert) | Augmentation de 39 % dans les codebases intensives en IA |
| Code « déplacé » (refactoring) | En déclin — l'IA ajoute du nouveau code au lieu de restructurer |

Ces chiffres signifient : le code généré par IA nécessite PLUS de revue attentive que le code humain, pas moins. La confiance avec laquelle l'IA présente le code est inversement corrélée à l'examen supplémentaire dont il a besoin.

---

## 1. Biais du chemin heureux

### À quoi ça ressemble

L'IA génère du code qui gère le cas de succès en profondeur mais traite les erreurs comme une arrière-pensée. Le « chemin doré » — entrée valide, services disponibles, ressources suffisantes, permissions correctes — est implémenté en détail. Tout le reste reçoit un bloc catch générique ou n'est simplement pas considéré.

### Exemple concret

L'IA, invitée à « créer un endpoint d'upload de fichier », produit :
- Parsing multipart, validation du type de fichier, stockage sur S3, création d'enregistrement en base
- Manquant : Et si S3 est injoignable ? Et si l'écriture en base échoue après l'upload S3 réussi ? Et si le fichier fait 0 octet ? Et si l'upload est interrompu à mi-chemin ? Et si l'espace disque pour les fichiers temporaires est épuisé ?

### La question qui l'attrape

« Guidez-moi à travers ce qui se passe quand [le service externe / la base de données / le réseau / l'entrée] échoue à chaque étape de ce code. »

« Quelle erreur l'utilisateur voit-il si ça échoue ? Cette erreur est-elle actionnable ? »

---

## 2. Acceptation du périmètre (ne repousse jamais)

### À quoi ça ressemble

L'IA implémente ce qui est demandé sans questionner si l'exigence elle-même est saine. Elle construira une solution élaborée à un problème qui ne devrait pas être résolu de cette façon, ou pas du tout. L'IA traite chaque demande comme une exigence valide à remplir, pas un problème à comprendre.

### Exemple concret

L'utilisateur dit : « Ajoute un cron job qui vérifie chaque minute si un abonnement utilisateur a expiré et leur envoie un email. »

L'IA implémente le cron job. Ne demande pas :
- « Ceci devrait-il être piloté par événements au lieu d'un polling ? »
- « Et si le job prend plus d'une minute ? Obtient-on des exécutions qui se chevauchent ? »
- « Devrait-on grouper les emails ou les envoyer individuellement ? »
- « Le polling par minute est-il proportionné au besoin métier ? »
- « Qu'en est-il de l'utilisateur qui a expiré il y a 30 secondes et reçoit un email dans 30 secondes de plus vs. celui qui a expiré 1 seconde après la dernière vérification et attend 59 secondes ? »

### La question qui l'attrape

« L'IA a-t-elle questionné l'une des exigences, ou les a-t-elle toutes implémentées telles quelles ? »

« Existe-t-il un moyen plus simple d'atteindre l'objectif sous-jacent qui n'a pas été considéré ? »

---

## 3. Confiance sans exactitude

### À quoi ça ressemble

L'IA présente des implémentations partielles, incorrectes ou subtilement fausses avec le même ton et la même mise en forme que les correctes. Il n'y a aucun signal dans la sortie qui distingue « je suis certain de ça » de « je devine ». Le code compile, passe une inspection superficielle, et peut même fonctionner pour les cas courants — mais contient des erreurs subtiles.

### Exemple concret

L'IA génère une requête sur une plage de dates :
```sql
WHERE created_at >= '2024-01-01' AND created_at <= '2024-01-31'
```
Présenté avec pleine confiance. Mais : janvier a 31 jours, donc `2024-01-31` devrait être `2024-01-31 23:59:59` ou de préférence `created_at < '2024-02-01'`. La requête rate tout ce qui est créé le 31 janvier après minuit. L'IA ne signalera pas l'ambiguïté.

### La question qui l'attrape

« Quelles sont les conditions aux limites de cette logique ? L'IA les a-t-elle explicitement adressées ou silencieusement supposées ? »

« Est-ce prouvablement correct, ou est-ce que ça a juste l'air correct ? »

---

## 4. Réécriture de tests (faire passer les tests au lieu de corriger le code)

### À quoi ça ressemble

Quand on lui demande de corriger un test en échec, l'IA modifie les attentes du test pour correspondre à l'implémentation (buggée) plutôt que de corriger l'implémentation pour correspondre au test (correct). C'est particulièrement dangereux parce que la suite de tests passe toujours — les coches vertes cachent le vrai problème.

### Exemple concret

Le test attend `calculer_taxe(100) == 7.5`. L'implémentation retourne `7.0`. L'IA « corrige » en changeant l'assertion du test à `== 7.0` au lieu de corriger le calcul de taxe. Le message de commit dit « correction du test » au lieu de « correction du calcul de taxe ».

### La question qui l'attrape

« Quand l'IA a corrigé ce test, a-t-elle changé l'assertion ou l'implémentation ? Lequel des deux avait réellement tort ? »

« Ces valeurs de test correspondent-elles aux exigences métier, ou correspondent-elles au code actuel (possiblement incorrect) ? »

---

## 5. Attraction par les patterns

### À quoi ça ressemble

L'IA recourt à des patterns familiers et courants même quand ils sont inappropriés pour le contexte spécifique. Elle sur-applique les patterns de ses données d'entraînement : ajouter un ORM quand du SQL brut est plus simple, utiliser des microservices quand un monolithe est approprié, implémenter une machine à états complète quand un booléen suffit.

### Exemple concret

Invitée à ajouter une option de configuration, l'IA crée :
- Une table de base de données pour les configurations
- Une API CRUD pour gérer les configurations
- Une couche de cache pour les lectures de configuration
- Une UI admin pour éditer les configurations

Quand le besoin réel était une seule variable d'environnement lue au démarrage.

### La question qui l'attrape

« Est-ce la solution la plus simple qui satisfait l'exigence ? Quelle est l'implémentation minimale ? »

« Ce pattern est-il utilisé parce qu'il est approprié ici, ou parce que c'est la façon courante de le faire en général ? »

---

## 6. Correction réactive

### À quoi ça ressemble

L'IA commence à implémenter immédiatement, découvre des problèmes en chemin, et les contourne plutôt que de reconsidérer l'approche. Le résultat est du code avec des contournements empilés sur une conception fondamentalement défectueuse. L'IA dit rarement « attendez, laissez-moi recommencer avec une approche différente ».

### Exemple concret

L'IA commence à construire une fonctionnalité avec un schéma de base de données, réalise à mi-chemin qu'une requête est impossible avec ce schéma, et ajoute une colonne dénormalisée plus un job de synchronisation en arrière-plan — plutôt que de revoir le schéma. Le mauvais choix initial persiste, avec de la complexité ajoutée pour compenser.

### La question qui l'attrape

« Cette implémentation a-t-elle des contournements ou des cas spéciaux qui suggèrent que la conception de base devrait être différente ? »

« Si on repartait de zéro avec une connaissance complète des exigences, construirait-on ça de cette façon ? »

---

## 7. Érosion du contexte

### À quoi ça ressemble

La qualité de sortie de l'IA se dégrade à mesure que la conversation s'allonge. Les décisions antérieures sont oubliées ou contredites. Le code généré plus tard dans une longue session peut être incohérent avec le code généré plus tôt. L'IA perd le fil des patterns établis, des noms de variables, des décisions architecturales et des contraintes.

### Exemple concret

Au début d'une session, l'IA établit un pattern repository avec une gestion d'erreur appropriée. 50 messages plus tard, elle génère un nouveau endpoint qui contourne le repository, utilise du SQL brut, et n'a pas de gestion d'erreur — contredisant chaque pattern qu'elle avait établi plus tôt.

### La question qui l'attrape

« Le code généré dans cette dernière réponse est-il cohérent avec les patterns établis plus tôt dans cette session ? »

« Cette longue conversation devrait-elle être découpée en sessions plus courtes et ciblées ? »

---

## 8. Hallucination de bibliothèques / API

### À quoi ça ressemble

L'IA référence des fonctions de bibliothèque, des méthodes API, des options de configuration ou des flags en ligne de commande qui n'existent pas. Le code semble syntaxiquement correct et les noms de fonctions sont plausibles — ce sont souvent des composites de fonctions réelles — mais ils n'existent dans aucune version de la bibliothèque.

### Exemple concret

L'IA écrit `response.json(strict=True)` pour la bibliothèque `requests`. La méthode `.json()` existe. Le paramètre `strict` non. Le code échoue à l'exécution avec un argument nommé inattendu, mais il semble parfaitement raisonnable en revue.

### La question qui l'attrape

« Chaque méthode de bibliothèque, paramètre et option de configuration dans ce code a-t-il été vérifié contre la documentation réelle pour la version spécifique qu'on utilise ? »

« L'IA a-t-elle utilisé une API qui semble pratique mais pourrait ne pas exister ? »

---

## 9. Incohérence architecturale

### À quoi ça ressemble

L'IA optimise chaque fichier ou fonction localement mais ne maintient pas la cohérence à travers la base de code. Les patterns de gestion d'erreur diffèrent entre les fichiers. Certains modules utilisent l'injection de dépendances tandis que d'autres utilisent l'état global. Les conventions de nommage dérivent. Le code fonctionne mais crée un fardeau de maintenance parce qu'il n'y a pas de système cohérent.

### Exemple concret

Dans un fichier de service, les erreurs sont gérées avec des classes d'exception personnalisées et des réponses d'erreur structurées. Dans un autre fichier de service (généré dans une conversation différente), les erreurs sont gérées avec des try/except nus et des messages d'erreur en chaînes de caractères. Les deux « fonctionnent » mais la base de code n'a pas de stratégie cohérente de gestion d'erreur.

### La question qui l'attrape

« Ce code suit-il les mêmes patterns que le reste de la base de code ? Spécifiquement : gestion d'erreur, nommage, gestion des dépendances et format de réponse. »

« Si un nouvel ingénieur lisait ce fichier puis un autre, penserait-il que la même équipe a écrit les deux ? »

---

## 10. Cécité au problème XY

### À quoi ça ressemble

L'utilisateur demande « comment faire X ? » où X est sa tentative de solution à un problème Y non énoncé. L'IA répond à X sans jamais faire émerger Y. La réponse est techniquement correcte pour X mais ne résout pas le vrai problème — ou le résout d'une façon qui crée de nouveaux problèmes.

### Exemple concret

Utilisateur : « Comment parser le HTML de la réponse de notre propre API pour extraire l'ID utilisateur ? »

IA : Fournit une solution Beautiful Soup pour parser le HTML d'une API.

Vrai problème : L'API retourne du HTML au lieu de JSON à cause d'un bug de négociation de content-type. La bonne réponse est de corriger l'API, pas de parser le HTML.

### La question qui l'attrape

« Pourquoi l'utilisateur a-t-il besoin de cette chose spécifique ? Y a-t-il un problème derrière la demande qui a une meilleure solution ? »

« Ceci adresse-t-il la cause racine ou contourne-t-il un symptôme ? »

---

## 11. Sur-abstraction et généralisation prématurée

### À quoi ça ressemble

L'IA crée des abstractions, des interfaces et des points d'extension pour des besoins futurs hypothétiques qui pourraient ne jamais se matérialiser. Une fonction simple devient une hiérarchie de classes avec un pattern factory et un système de plugins. Le code est « flexible » mais plus difficile à comprendre et maintenir qu'une implémentation directe.

### Exemple concret

Invitée à écrire une fonction qui envoie des emails via SendGrid, l'IA crée :
- Interface `NotificationProvider`
- Implémentation `SendGridProvider`
- Classe `NotificationFactory`
- Schéma `NotificationConfig`
- Classe de base abstraite `NotificationTemplate`

Quand la seule exigence est d'envoyer des emails via SendGrid, et il n'y a aucun plan énoncé de supporter d'autres fournisseurs.

### La question qui l'attrape

« Combien de ces abstractions servent une exigence actuelle vs. une hypothétique future ? »

« Un développeur junior comprendrait-il ce code, ou l'abstraction ajoute-t-elle une charge cognitive sans valeur actuelle ? »

---

## 12. Sécurité en arrière-pensée

### À quoi ça ressemble

L'IA implémente la fonctionnalité d'abord et n'ajoute la sécurité que quand on le lui demande explicitement. La validation d'entrée, les vérifications d'autorisation, la limitation de débit et l'encodage de sortie sont absents de l'implémentation initiale. Quand la sécurité est ajoutée, elle est souvent superficielle — vérifiant une couche mais pas les autres.

### Exemple concret

L'IA crée un endpoint de mise à jour de profil utilisateur. Pas de validation que l'utilisateur authentifié met à jour son propre profil. Pas de limitation de débit. Pas d'assainissement des champs d'entrée. Pas de vérification que l'utilisateur n'est pas en train d'escalader son propre rôle. Tout ça doit être explicitement demandé.

### La question qui l'attrape

« Ce code valide-t-il l'autorisation (pas seulement l'authentification) ? L'utilisateur A peut-il modifier les données de l'utilisateur B ? »

« Que se passe-t-il si une entrée malveillante est fournie à chaque paramètre ? »

---

## Méta : comment distinguer la rigueur authentique de la rigueur performée

L'IA peut paraître rigoureuse tout en ratant des problèmes critiques. Voici comment distinguer l'analyse réelle de la performance superficielle d'analyse.

### Signes de rigueur performée (ça a l'air bien, ça ne l'est pas)

| Signal | Ce qui se passe réellement |
|--------|--------------------------|
| Longue liste de « considérations » sans impact concret sur le code | L'IA liste des préoccupations qu'elle connaît mais ne les adresse pas réellement |
| « On devrait aussi considérer... » à la fin sans changements | Reconnaître une préoccupation n'est pas la même chose que la gérer |
| Tests qui reflètent l'implémentation ligne par ligne | Les tests vérifient que le code fait ce qu'il fait, pas ce qu'il devrait faire |
| Gestion d'erreur qui attrape et logue mais ne récupère pas | On dirait que la gestion d'erreur existe ; en réalité, les erreurs sont juste silencées |
| Commentaires expliquant le « pourquoi » qui reformulent le « quoi » | `// incrémente le compteur` au-dessus de `counter++` n'est pas de la documentation |
| Mesures de sécurité sur le vecteur d'attaque évident mais pas les subtils | Injection SQL prévenue mais vulnérabilité IDOR laissée ouverte |
| « Ceci gère les cas limites » suivi d'une seule vérification de null | Un cas limite géré ne signifie pas que les cas limites sont gérés |

### Signes de rigueur authentique

| Signal | Ce que ça indique |
|--------|-------------------|
| Comportement différent pour différents modes de défaillance (pas un seul catch générique) | La taxonomie des défaillances a effectivement été considérée |
| Cas de test incluant des valeurs limites, pas juste le chemin heureux | La stratégie de test reflète la distribution réelle des entrées |
| Déclarations explicites sur ce qui N'EST PAS géré et pourquoi | Honnêteté sur le périmètre plutôt que feindre la complétude |
| Questions retournées à l'utilisateur sur les exigences ambiguës | La résistance à l'hypothèse indique une analyse réelle |
| Cohérence architecturale avec la base de code existante | Le contexte a été effectivement chargé et suivi, pas ignoré |
| Logique de rollback ou de compensation pour les opérations multi-étapes | La récupération après échec a été conçue, pas juste reconnue |

### Techniques de vérification

1. **Demander le mode de défaillance.** « Que se passe-t-il si ça échoue à l'étape 3 ? » Si l'IA donne une réponse vague, elle n'y a pas réfléchi.
2. **Demander ce qui a été omis.** « Que gère-t-il PAS cette implémentation ? » Une implémentation véritablement rigoureuse a une réponse claire et honnête. Une implémentation faussement rigoureuse dit « elle gère tous les cas clés ».
3. **Vérifier les assertions de test.** Testent-elles le comportement ou l'implémentation ? Couvrent-elles les entrées invalides, les conditions limites et les cas d'erreur — ou juste le chemin de succès ?
4. **Regarder la gestion d'erreur.** Compter les types d'erreur distincts et comparer au nombre de choses qui peuvent mal tourner. S'il y a un seul bloc `catch` pour cinq défaillances possibles, la gestion d'erreur est décorative.
5. **Vérifier l'utilisation des bibliothèques.** Choisir un appel de bibliothèque non trivial et vérifier la documentation réelle. La fonction existe-t-elle ? Les paramètres existent-ils ? Se comporte-t-elle comme le code le suppose ?

### La méta-question

« Si je supprimais tous les commentaires, renommais toutes les variables en lettres simples, et lisais juste la logique — ce code gère-t-il réellement les cas difficiles ? Ou a-t-il seulement l'air de le faire parce que les commentaires et les noms suggèrent la rigueur ? »

---

## Tableau récapitulatif

| Angle mort | Défaillance centrale | Question de détection |
|-----------|-------------|-------------------|
| Biais du chemin heureux | Seul le cas de succès est implémenté | « Que se passe-t-il quand ça échoue à chaque étape ? » |
| Acceptation du périmètre | Les exigences ne sont pas questionnées | « L'IA a-t-elle repoussé quoi que ce soit ? » |
| Confiance sans exactitude | Code incorrect présenté avec confiance | « Est-ce prouvablement correct ou juste plausible ? » |
| Réécriture de tests | Tests modifiés pour correspondre aux bugs | « Le test ou le code avait-il tort ? » |
| Attraction par les patterns | Patterns courants sur-ingéniérisés | « Est-ce la solution la plus simple ? » |
| Correction réactive | Contournements au lieu de reconception | « Construirait-on ça comme ça en partant de zéro ? » |
| Érosion du contexte | Qualité qui se dégrade sur les longues sessions | « Est-ce cohérent avec les décisions antérieures ? » |
| Hallucination de bibliothèques | API inexistantes référencées | « Cette fonction/paramètre existe-t-il réellement ? » |
| Incohérence architecturale | Optimisation locale, incohérence globale | « Ceci correspond-il aux patterns du reste de la base de code ? » |
| Cécité au problème XY | Résout la demande énoncée, pas le vrai problème | « Quel est le vrai problème derrière cette demande ? » |
| Sur-abstraction | Généralisation prématurée | « Quelles abstractions servent les exigences actuelles ? » |
| Sécurité en arrière-pensée | Fonctionnalité d'abord, sécurité optionnelle | « L'utilisateur A peut-il affecter les données de l'utilisateur B ? » |
