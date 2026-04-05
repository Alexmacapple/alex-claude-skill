# Angles morts de l'ingénierie

Catégories de problèmes que les ingénieurs manquent systématiquement lors de la conception, l'implémentation et la revue. Pour chaque catégorie : ce que c'est, pourquoi c'est manqué, les questions clés pour le faire émerger, et des exemples concrets.

---

## 1. Sécurité

### Pourquoi c'est manqué

La sécurité est invisible quand elle fonctionne. Les ingénieurs optimisent pour la fonctionnalité — « est-ce que ça fait le truc ? » — et les échecs de sécurité ne se manifestent que dans des conditions adverses que les tests normaux ne simulent pas. La pensée sécurité exige de supposer une intention malveillante, ce qui est psychologiquement contre-nature pour les constructeurs.

### Questions clés

| Domaine | Question |
|------|----------|
| Authentification | « Que se passe-t-il si le JWT est expiré mais que la requête est déjà en vol ? » |
| Autorisation | « L'utilisateur A peut-il accéder aux ressources de l'utilisateur B en changeant l'ID dans l'URL ? » |
| Validation d'entrée | « Que se passe-t-il si ce champ contient 10 Mo de données ? Du SQL ? Du JavaScript ? Des caractères de contrôle Unicode ? » |
| Exposition de données | « Quels champs de cette réponse API l'utilisateur demandeur ne devrait-il PAS voir ? » |
| Secrets | « Si cette ligne de log est capturée, contient-elle quelque chose de sensible ? » |
| CSRF/SSRF | « Cet endpoint peut-il être déclenché par une page malveillante visitée par l'utilisateur ? » |
| Limitation de débit | « Quel est le coût si quelqu'un appelle cet endpoint 10 000 fois par seconde ? » |
| Dépendance | « Quand a eu lieu le dernier audit de sécurité de cette dépendance ? A-t-elle des CVE connues ? » |

### Erreurs courantes

- **Broken Object-Level Authorization (BOLA) :** La vulnérabilité API n1. L'endpoint vérifie l'authentification mais pas si l'utilisateur authentifié possède la ressource demandée. Chaque endpoint qui prend un ID d'entité doit vérifier la propriété.
- **Assignation de masse :** Accepter tous les champs du corps de requête et les passer à l'ORM. L'utilisateur envoie `{"role": "admin"}` dans une mise à jour de profil.
- **Messages d'erreur verbeux :** Traces de pile, erreurs SQL ou chemins internes dans les réponses API de production.
- **Références directes non sécurisées :** IDs entiers séquentiels permettant l'énumération. L'utilisateur itère `/api/factures/1`, `/api/factures/2`, etc.
- **En-têtes de sécurité manquants :** Pas de CSP, pas de HSTS, pas de X-Frame-Options dans les réponses.

---

## 2. Scalabilité

### Pourquoi c'est manqué

Les systèmes qui fonctionnent à l'échelle actuelle semblent corrects. Les ingénieurs testent avec de petits jeux de données et une faible concurrence. Le modèle mental « ça fonctionne » est formé à l'échelle de développement et rarement mis à jour. Les échecs de scalabilité sont non linéaires — une requête qui prend 50 ms avec 1 000 lignes prend 30 secondes avec 1 000 000.

### Questions clés

| Domaine | Question |
|------|----------|
| Croissance des données | « Que se passe-t-il avec cette requête quand la table a 10 M de lignes ? 100 M ? » |
| Trafic | « Si le trafic augmente de 10x, quel composant casse en premier ? » |
| Stockage | « Combien de stockage ça consomme par utilisateur par mois ? Quelle est la projection ? » |
| Cardinalité | « Combien de valeurs distinctes cette colonne/index/clé de cache aura-t-elle ? » |
| Fan-out | « Combien d'appels en aval une seule action utilisateur déclenche-t-elle ? » |
| Coût | « Quel est le coût cloud de ça à 100x l'utilisation actuelle ? » |
| Points chauds | « Y a-t-il une seule ligne, clé ou partition qui reçoit un trafic disproportionné ? » |

### Erreurs courantes

- **Requêtes N+1 :** Récupérer une liste puis requêter chaque élément individuellement. Fonctionne avec 10 éléments, catastrophique avec 10 000.
- **Requêtes non bornées :** `SELECT * FROM table` sans LIMIT. Fonctionne en dev (100 lignes), OOM en production (10 M lignes).
- **Pagination manquante :** Endpoints qui retournent tous les résultats. Correct jusqu'à ce que le jeu de données grossisse.
- **Scans de table complets masqués par les petites données :** Index manquant sur une colonne de filtre. Invisible jusqu'à ce que la table grossisse.
- **Cache stampede :** Le cache expire, 1 000 requêtes concurrentes manquent toutes le cache et frappent la base de données simultanément.
- **Algorithmes linéaires sur données croissantes :** Boucles O(n) qui deviennent O(n^2) quand imbriquées ou appliquées à des collections croissantes.

---

## 3. Cycle de vie des données

### Pourquoi c'est manqué

Les ingénieurs se concentrent sur la création et la lecture des données. Le cycle de vie complet — création, transformation, archivage, suppression, conformité — est rarement considéré en amont. La suppression de données est particulièrement négligée parce qu'elle n'a pas de valeur immédiate côté utilisateur.

### Questions clés

| Domaine | Question |
|------|----------|
| Création | « Qu'est-ce qui valide ces données au point d'entrée ? Et si les règles de validation changent ? » |
| Rétention | « Combien de temps garde-t-on ça ? Y a-t-il une exigence légale ou métier ? » |
| Suppression | « Si un utilisateur demande la suppression de son compte, que se passe-t-il avec ses données dans toutes les tables ? » |
| Cascade | « Si cet enregistrement est supprimé, qu'est-ce qui le référence ? Les clés étrangères cascadent-elles ou orphelinent-elles ? » |
| DCP | « Quels champs dans cette table sont des données à caractère personnel ? Peuvent-ils être pseudonymisés ? » |
| Sauvegarde | « Si on restaure depuis une sauvegarde, ces données ont-elles des dépendances de cohérence avec d'autres systèmes ? » |
| Migration | « Si le schéma change, que se passe-t-il avec les données existantes ? Un remplissage rétroactif est-il nécessaire ? » |
| Export | « L'utilisateur peut-il exporter ses données ? Dans quel format ? » |

### Erreurs courantes

- **Enregistrements orphelins :** Parent supprimé, enfants restent avec des clés étrangères pendantes ou sans FK du tout.
- **Incohérence de suppression logique :** Certaines requêtes filtrent `deleted_at IS NULL`, d'autres non. Les données supprimées fuient dans les résultats.
- **DCP dans les logs :** La journalisation structurée capture les corps de requête contenant email, téléphone, adresse.
- **Pas de politique de rétention :** Les tables grossissent indéfiniment. Les anciennes données ne sont jamais archivées ni purgées.
- **Lacunes du droit à l'effacement RGPD :** Utilisateur supprimé de la table `users` mais ses données persistent dans `audit_log`, `analytics_events`, `email_log`, les CSV exportés et les intégrations tierces.
- **Confusion de données temporelles :** État « actuel » mélangé avec l'état historique. Pas de distinction claire entre « enregistrement actif » et « instantané au temps T ».

---

## 4. Points d'intégration

### Pourquoi c'est manqué

Les ingénieurs testent leur propre code, pas la frontière entre leur code et les systèmes externes. Les intégrations fonctionnent en dev (où le système externe est mocké ou toujours disponible) et échouent en production (où il est instable, lent ou retourne des réponses inattendues).

### Questions clés

| Domaine | Question |
|------|----------|
| Disponibilité | « Que se passe-t-il quand cette dépendance est en panne pendant 30 minutes ? 4 heures ? » |
| Latence | « Et si cet appel API prenait 30 secondes au lieu de 200 ms ? » |
| Forme de réponse | « Et si la réponse incluait des champs inattendus ? Ou s'il manquait des champs attendus ? » |
| Versioning | « Que se passe-t-il si l'API tierce change sans préavis ? » |
| Limites de débit | « Cette intégration a-t-elle des limites de débit ? Que se passe-t-il quand on les atteint ? » |
| Sécurité de retry | « Cette opération est-elle idempotente ? Que se passe-t-il si on réessaie et que la première tentative a en fait réussi ? » |
| Rayon d'explosion | « Si cette intégration échoue, quoi d'autre casse ? Peut-on dégrader gracieusement ? » |
| Authentification | « Quand le token API expire-t-il ? Qu'est-ce qui le rafraîchit ? Et si le rafraîchissement échoue ? » |

### Erreurs courantes

- **Timeout mal configuré :** Timeout HTTP par défaut de 30 s ou infini. Une dépendance lente bloque les threads, causant une cascade vers l'indisponibilité totale du système.
- **Pas de disjoncteur (circuit breaker) :** La dépendance en échec est appelée de façon répétée, consommant des ressources et ralentissant tout.
- **Hypothèses sur la livraison de webhooks :** Supposer que les webhooks arrivent une fois, dans l'ordre, et promptement. En réalité : doublons, hors-ordre, retardés de plusieurs heures.
- **Couplage de schéma :** Désérialiser toute la réponse dans un type strict. Tout ajout de champ ou changement de type dans l'API externe cause des échecs.
- **Pas de fallback :** Pas de réponse en cache/par défaut quand l'intégration est indisponible. La fonctionnalité devient complètement non fonctionnelle.

---

## 5. Modes de défaillance

### Pourquoi c'est manqué

Les ingénieurs pensent en termes de chemins de succès. La gestion des échecs est ajoutée après coup — souvent juste `catch (e) { log(e) }` — sans considérer la taxonomie des échecs et les réponses appropriées pour chacun.

### Questions clés

| Domaine | Question |
|------|----------|
| Échec partiel | « Et si l'étape 3 sur 5 échoue ? Dans quel état est le système ? » |
| Comportement de retry | « Si c'est réessayé, le résultat est-il identique ? Ou obtient-on des doublons ? » |
| Propagation d'erreur | « Cette erreur remonte-t-elle clairement, ou est-elle avalée pour resurgir comme un symptôme déroutant ailleurs ? » |
| Messages empoisonnés | « Et si un message dans la file est malformé ? Bloque-t-il tout le traitement ? » |
| Épuisement de ressources | « Que se passe-t-il quand le disque est plein ? La mémoire épuisée ? Le pool de connexions vidé ? » |
| Défaillance en cascade | « Si ce composant échoue, quels autres composants échouent en conséquence ? » |
| Récupération | « Après résolution de la défaillance, le système s'auto-répare-t-il ou nécessite-t-il une intervention manuelle ? » |

### Erreurs courantes

- **État incohérent suite à des opérations partielles :** Processus multi-étapes (créer commande, débiter paiement, envoyer email) échoue à l'étape 2. La commande existe, le paiement n'a pas eu lieu, mais il n'y a pas de logique de compensation.
- **Tempêtes de retry :** Le service A réessaie les appels échoués au service B. Le service B échouait à cause d'une surcharge. Les retries empirent les choses. Le backoff exponentiel avec gigue est manquant.
- **Échecs silencieux :** Exception capturée et loguée mais non propagée. Le système semble sain tout en produisant des résultats incorrects.
- **Inutilité des messages d'erreur :** `"Une erreur s'est produite"` sans contexte sur ce qui a échoué, pourquoi, ou ce que l'utilisateur peut faire.
- **Négligence de la file de messages morts :** Les messages échoués vont dans une file de messages morts que personne ne surveille. Les données sont silencieusement perdues.

---

## 6. Concurrence

### Pourquoi c'est manqué

Les développeurs écrivent et testent le code séquentiellement. Les bugs de concurrence sont non déterministes — ils dépendent du timing, de la charge et de l'ordonnancement. Une condition de course qui survient 1 fois sur 10 000 passe tous les tests et ne se manifeste qu'en production sous charge.

### Questions clés

| Domaine | Question |
|------|----------|
| Conditions de course | « Si deux utilisateurs font ça simultanément, que se passe-t-il ? » |
| Double soumission | « Si l'utilisateur clique le bouton deux fois rapidement, crée-t-on deux enregistrements ? » |
| Lecture-modification-écriture | « Entre la lecture de cette valeur et l'écriture de la mise à jour, un autre processus peut-il la changer ? » |
| Verrouillage | « Quelle est la granularité du verrou ? Tient-on les verrous pendant les I/O ? » |
| Interblocage | « Deux processus peuvent-ils chacun tenir un verrou dont l'autre a besoin ? » |
| Ordonnancement | « Ce code suppose-t-il que les événements arrivent dans l'ordre ? Et si non ? » |
| Idempotence | « Si cette opération s'exécute deux fois avec la même entrée, le résultat est-il le même ? » |

### Erreurs courantes

- **Vérifier-puis-agir sans verrouillage :** `if not exists(email): create_user(email)` — deux requêtes concurrentes passent toutes les deux la vérification, toutes les deux créent l'utilisateur.
- **Mises à jour perdues :** Deux requêtes lisent solde=100, les deux ajoutent 50, les deux écrivent 150. Attendu : 200. Utiliser le verrouillage optimiste (colonne de version) ou `UPDATE ... SET solde = solde + 50`.
- **Double soumission sur les formulaires :** L'utilisateur clique « Soumettre » deux fois. Deux enregistrements identiques créés. Pas de clé d'idempotence, pas de garde côté client.
- **Dérive de compteur :** `count = get_count(); set_count(count + 1)` au lieu d'un `INCREMENT` atomique. Sous concurrence, les compteurs dérivent vers le bas.
- **Épuisement du pool de connexions :** Transactions longues ou connexions fuiteuses vident le pool. Les nouvelles requêtes s'empilent et timeout.

---

## 7. Écarts d'environnement

### Pourquoi c'est manqué

« Ça marche sur ma machine » est l'expression canonique de cet angle mort. Les environnements de développement diffèrent de la production de façons invisibles jusqu'à ce qu'elles causent des échecs : OS différent, limites de ressources différentes, topologie réseau différente, volume de données différent.

### Questions clés

| Domaine | Question |
|------|----------|
| Configuration | « Quelles valeurs de config diffèrent entre dev, staging et production ? » |
| Volume de données | « Le dev a 100 lignes. La production en a 10 M. A-t-on testé avec des données à l'échelle de la production ? » |
| Réseau | « Ceci suppose-t-il une latence localhost ? Qu'en est-il des appels cross-région en prod ? » |
| Permissions | « Le compte de service prod a-t-il les mêmes permissions que l'utilisateur dev ? » |
| Secrets | « Comment les secrets sont-ils gérés en production ? Sont-ils les mêmes qu'en dev ? » |
| Limites de ressources | « Quelles sont les limites mémoire/CPU/disque en production ? A-t-on testé à ces limites ? » |
| Dépendances | « Toutes les versions de dépendances sont-elles épinglées ? Un tag `latest` pourrait-il différer entre environnements ? » |
| Feature flags | « Quels flags sont activés en prod qui ne le sont pas en dev, ou vice versa ? » |

### Erreurs courantes

- **Différences de fuseau horaire :** La machine dev est en UTC, la production est en UTC, mais le serveur de base de données a été configuré dans un fuseau différent par le défaut du fournisseur cloud.
- **Hypothèses sur le système de fichiers :** Le code écrit dans `/tmp` en supposant un espace illimité. Le conteneur de production a un tmpfs de 512 Mo.
- **Résolution DNS :** Le dev local résout les noms de service instantanément. Le DNS de production a des TTL, du cache et des échecs occasionnels.
- **SSL/TLS en production uniquement :** Le dev utilise HTTP. Le premier déploiement en production échoue parce que l'application ne fait pas confiance au CA, ou les redirections cassent.
- **Variables d'environnement manquantes :** L'app démarre bien en dev (valeurs par défaut utilisées). La production n'a pas de valeurs par défaut et crashe au démarrage — ou pire, utilise silencieusement de mauvaises valeurs.

---

## 8. Observabilité

### Pourquoi c'est manqué

L'observabilité n'est pas une fonctionnalité que les utilisateurs voient. Elle a zéro valeur côté utilisateur jusqu'à ce que quelque chose casse — et là c'est la chose la plus importante. Les ingénieurs sous pression de temps la dépriorisent parce qu'elle n'apparaît pas dans les démos.

### Questions clés

| Domaine | Question |
|------|----------|
| Débogage | « Si ça échoue en production à 3h du matin, quelles informations l'ingénieur d'astreinte a-t-il ? » |
| Journalisation | « Les messages de log sont-ils structurés ? Incluent-ils des IDs de corrélation, des IDs utilisateur et du contexte ? » |
| Métriques | « Quelles métriques nous disent que ce système est sain ? Quel seuil signifie « malsain » ? » |
| Alertes | « Quelles alertes se déclenchent si ça casse ? Sont-elles actionnables ou juste du bruit ? » |
| Traçage | « Peut-on tracer une requête utilisateur à travers tous les services qu'elle traverse ? » |
| Tableaux de bord | « Y a-t-il un tableau de bord pour cette fonctionnalité ? Quelqu'un le regarde-t-il réellement ? » |
| Coût | « Connaît-on le coût par requête de cette opération ? Peut-on détecter des anomalies de coût ? » |

### Erreurs courantes

- **Logger et prier :** La journalisation existe mais personne ne l'interroge. Pas d'alertes, pas de tableaux de bord, pas de runbooks.
- **Corrélation de requêtes manquante :** Aucun moyen de tracer une seule requête utilisateur à travers plusieurs services et appels de base de données.
- **Explosion de cardinalité de métriques :** Métriques taguées avec l'ID utilisateur ou l'ID de requête. Le système de monitoring est submergé.
- **Fatigue d'alertes :** Trop d'alertes non actionnables. L'astreinte les ignore toutes. Les vraies alertes se perdent dans le bruit.
- **Pas de métriques métier :** Les métriques techniques (CPU, mémoire, latence) existent mais personne ne suit les métriques métier (commandes par minute, taux de conversion). Une défaillance métier avec une infrastructure saine passe inaperçue.

---

## 9. Déploiement

### Pourquoi c'est manqué

Le déploiement est traité comme « pousser le code, c'est en ligne ». La période de transition — où ancien et nouveau code coexistent, où les migrations s'exécutent, où les caches contiennent d'anciennes données — est rarement considérée. Les ingénieurs pensent en termes d'« avant » et « après », pas de « pendant ».

### Questions clés

| Domaine | Question |
|------|----------|
| Rollback | « Peut-on annuler ce déploiement en moins de 5 minutes ? Qu'est-ce qui casse si on le fait ? » |
| Migration | « Cette migration est-elle rétrocompatible ? L'ancien code peut-il fonctionner avec le nouveau schéma ? » |
| Requêtes en vol | « Que se passe-t-il avec les requêtes qui ont commencé avant le déploiement et finissent après ? » |
| Invalidation de cache | « Les valeurs en cache ont-elles encore du sens après ce déploiement ? » |
| Feature flags | « Cette fonctionnalité peut-elle être désactivée sans déploiement ? » |
| Zéro temps d'arrêt | « Y a-t-il un moment pendant le déploiement où le service est indisponible ? » |
| Ordre de dépendances | « Ce déploiement nécessite-t-il qu'un autre service soit déployé d'abord ? » |

### Erreurs courantes

- **Migrations non réversibles :** Colonne renommée ou supprimée. Le rollback vers la version précédente du code échoue parce que l'ancien code attend l'ancienne colonne.
- **Changements d'API cassants sans versioning :** Frontend déployé avant le backend (ou vice versa). Brève période où client et serveur ne sont pas d'accord sur le contrat API.
- **Caches périmés :** Le déploiement change le format de réponse. Le cache CDN/navigateur/application sert l'ancien format. Les utilisateurs voient une UI cassée jusqu'à l'expiration du cache.
- **Perte de session blue/green :** L'utilisateur est sur l'ancienne instance avec un état de session. Le trafic bascule vers la nouvelle instance. Session perdue.
- **Migration de base de données sous charge :** La migration verrouille une table pour ALTER. Toutes les requêtes vers cette table s'empilent et timeout. L'application semble en panne.

---

## 10. Multi-tenancy

### Pourquoi c'est manqué

Le multi-tenancy est une contrainte architecturale qui touche tout mais n'est possédée par aucune fonctionnalité unique. Chaque fonctionnalité individuelle fonctionne correctement en isolation. Les défaillances n'apparaissent que quand les tenants interagissent — via des ressources partagées, des fuites de données ou des voisins bruyants.

### Questions clés

| Domaine | Question |
|------|----------|
| Isolation des données | « Si je retire le token d'auth et substitue un ID de tenant différent, vois-je leurs données ? » |
| Filtrage de requêtes | « Chaque requête de cette fonctionnalité filtre-t-elle par tenant ? Y compris les jointures, sous-requêtes et agrégations ? » |
| Équité des ressources | « L'utilisation d'un tenant peut-elle dégrader la performance pour tous les autres ? » |
| Configuration | « C'est codé en dur pour un tenant, ou configurable par tenant ? » |
| Tâches de fond | « Les tâches de fond définissent-elles le contexte de tenant ? Et si une tâche traite plusieurs tenants ? » |
| Cache | « Les clés de cache sont-elles namespacées par tenant ? Le cache du tenant A peut-il retourner les données du tenant B ? » |
| Journalisation | « Si on recherche dans les logs par ID de tenant, obtient-on exactement et uniquement leur activité ? » |

### Erreurs courantes

- **Filtre de tenant manquant dans les nouvelles requêtes :** Chaque nouvelle requête doit inclure `tenant_id`. Un filtre manqué = fuite de données cross-tenant.
- **Caches globaux :** Clé de cache `user:123` sans préfixe de tenant. Deux tenants avec l'ID utilisateur 123 obtiennent les données en cache de l'autre.
- **Limites de débit partagées :** Limite de débit appliquée globalement. Le pic légitime d'un tenant bloque tous les autres.
- **Config spécifique au tenant en dur :** Feature flag ou règle métier codée en dur dans un if-statement au lieu de la configuration de tenant.
- **Fuite de contexte dans les tâches de fond :** La tâche traite le tenant A, puis le tenant B, mais le contexte de tenant de A persiste dans le traitement de B.

---

## 11. Cas limites

### Pourquoi c'est manqué

Les cas limites sont, par définition, pas le cas commun. Les ingénieurs construisent pour l'utilisateur typique sur le chemin typique. Mais les cas limites sont là où les bugs se cachent, où les données se corrompent, et où vivent les vulnérabilités de sécurité. Les bords de l'espace d'entrée sont aussi là où les attaquants opèrent.

### Questions clés

| Domaine | Question |
|------|----------|
| État vide | « À quoi ça ressemble avec zéro donnée ? Premier utilisateur, liste vide, pas d'historique ? » |
| Limites | « Que se passe-t-il au maximum ? Au minimum ? Exactement zéro ? Valeurs négatives ? » |
| Unicode | « Que se passe-t-il avec des emojis, du texte RTL ou des caractères hors ASCII ? » |
| Fuseau horaire | « Que se passe-t-il à minuit ? À minuit dans différents fuseaux ? Lors des transitions heure d'été ? » |
| Précision | « Utilise-t-on des flottants pour de l'argent ? Que se passe-t-il avec les arrondis sur des millions de transactions ? » |
| Nulls | « Lesquels de ces champs peuvent être null en pratique, même si le schéma dit NOT NULL ? » |
| Ordonnancement | « Et si la liste est vide ? Un seul élément ? Déjà triée ? Triée à l'envers ? » |

### Erreurs courantes

- **Panique sur état vide :** La fonctionnalité marche magnifiquement avec des données. Sans données : écran blanc, erreurs undefined, ou « Aucun résultat trouvé » trompeur quand l'utilisateur n'a pas encore cherché.
- **Dépassement d'entier / précision flottante :** `0.1 + 0.2 !== 0.3` en IEEE 754. Les calculs de devises dérivent. Utiliser des centimes entiers ou des types décimaux.
- **Datetime sans fuseau horaire :** Stocker `datetime` sans info de fuseau. Comparer des horodatages de sources différentes produit des résultats faux autour du changement d'heure.
- **Hypothèses sur les noms et textes :** Le champ nom rejette O'Brien (apostrophe non échappée), Muller (umlaut) ou (espace de largeur nulle). La longueur max de 50 rejette les noms longs légitimes.
- **Erreur de décalage dans la pagination :** La page 1 montre les éléments 1-10, la page 2 montre les éléments 10-19 (élément 10 dupliqué) ou les éléments 12-21 (élément 11 manquant).
- **Secondes intercalaires, années bissextiles, heure d'été :** `29 février` casse la validation de date. `2h du matin lors de la transition d'heure d'été` n'existe pas (ou existe deux fois). La logique de planification échoue.
- **Charge maximale :** Upload de fichier sans limite de taille. L'utilisateur uploade un fichier de 5 Go. Le serveur manque de mémoire.

---

## Référence rapide : la question qui attrape chaque angle mort

| Angle mort | Question la plus révélatrice |
|------------|-------------------------------|
| Sécurité | « L'utilisateur A peut-il accéder aux données de l'utilisateur B en manipulant la requête ? » |
| Scalabilité | « Que se passe-t-il à 100x l'échelle actuelle ? » |
| Cycle de vie des données | « Si on supprime cet utilisateur, que se passe-t-il avec ses données partout ? » |
| Intégration | « Que se passe-t-il quand cette dépendance est en panne pendant une heure ? » |
| Modes de défaillance | « Si l'étape 3 sur 5 échoue, dans quel état est le système ? » |
| Concurrence | « Si deux utilisateurs font ça au même instant, que se passe-t-il ? » |
| Environnement | « Qu'est-ce qui diffère en production qu'on ne teste pas ? » |
| Observabilité | « L'ingénieur d'astreinte peut-il débugger ça à 3h du matin avec les outils disponibles ? » |
| Déploiement | « Peut-on annuler ça en 5 minutes sans perte de données ? » |
| Multi-tenancy | « Chaque requête filtre-t-elle par tenant, y compris cette nouvelle ? » |
| Cas limites | « À quoi ça ressemble avec zéro donnée ? Le maximum de données ? De l'Unicode ? » |
