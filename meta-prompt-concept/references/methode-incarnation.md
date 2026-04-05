# Méthode d'incarnation des concepts

Méthode pour transformer un concept métier en prompt où le LLM EST le concept.

**Principe** : "Tu es un expert en X" décrit un rôle et produit du générique.
"Tu es X" incarne le processus et produit du structurel.

---

## Les 5 phases de cristallisation

### Phase 1 : Extraction de l'essence

Identifier ce que le concept FAIT, pas ce qu'il EST sur Wikipédia.

- Question clé : "Si ce concept était un processus autonome, quelles
  étapes exécuterait-il naturellement ?"
- Livrable : une phrase "Tu es [processus], pas [rôle]."
- Test : la phrase d'identité doit tenir en 2 lignes maximum.
  Si elle en prend plus, l'essence n'est pas trouvée.

### Phase 2 : Découpage en mouvements naturels

Chaque concept a des phases intrinsèques. Les identifier, les nommer,
les ordonner. Typiquement 3 à 5 mouvements.

- Pas d'étapes artificielles — les mouvements doivent émerger du concept
- Chaque mouvement a un nom court (1 mot) et une action claire (1 ligne)
- Test de naturalité : un praticien du domaine reconnaîtrait-il ces phases
  comme le déroulement naturel de son travail ?
- Si un mouvement nécessite plus de 3 lignes d'explication, il est
  trop large — le découper.

### Phase 3 : Régulation

Le prompt doit savoir quand s'activer et quand ne pas s'activer.

Construire obligatoirement :
- **Un triage** — quand appliquer le processus complet vs répondre
  directement. Minimum 2 catégories + 1 clause de sécurité.
- **Une clause de biais par défaut** — en cas de doute, vers quel
  comportement pencher. Toujours explicite, jamais implicite.
- **Des limites** — ce que le concept ne couvre PAS.

### Phase 4 : Instrumentation

Ajouter les outils de rigueur au prompt produit :

- **Échelle de certitude/qualité** — adaptée au domaine du concept.
  Toujours 4 niveaux avec symboles visuels distincts.
- **Format de sortie double** :
  - Mode complet (par défaut) — chaque mouvement visible
  - Mode compact (sur demande) — verdict + niveau + réserve principale
  - Les deux en blocs ~~~ pour que le LLM les traite comme templates
- **Détection du hedging** — identifier les formulations évasives
  spécifiques au domaine que le LLM doit surveiller dans ses propres
  sorties. Minimum 2 exemples concrets.
- **Clause d'accès** — chaque prompt produit DOIT inclure une mention
  explicite de ses limites d'accès (web, documents, bases de données).

### Phase 5 : Ancrage par l'exemple

Un exemple complet qui démontre le processus de bout en bout.

- Choisir un cas ni trivial ni extrême
- Montrer CHAQUE mouvement appliqué
- Inclure le mode complet ET le mode compact
- Le résultat doit être auto-suffisant

---

## Les 4 obligatoires

Chaque prompt incarné doit contenir ces 4 éléments. Si l'un manque,
le prompt est incomplet :

1. **Triage** avec clause de biais par défaut
2. **Détection du hedging** avec min 2 exemples spécifiques au domaine
3. **Clause d'accès** aux sources (web, documents, limites)
4. **Mode compact** documenté dans le format ET illustré dans l'exemple

---

## Règles de densité

- Incarnation, pas simulation. "Tu es X" = instruction d'architecture.
- Mouvements, pas étapes. Dynamique naturelle, pas procédure rigide.
- Densité maximale : si une phrase est supprimable sans perte, la supprimer.
- Héritage : chaque prompt produit hérite automatiquement des 4 obligatoires.
