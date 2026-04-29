---
name: readme-causal
description: "Génère un README structuré en 4 mouvements causaux (Anamèse, Étiologie, Ossature causale, Résidu) depuis un dépôt git, en mode inférence depuis code + git log + README existant. Utiliser quand l'auteur veut documenter le POURQUOI d'un projet et pas seulement le QUOI/COMMENT. Déclencheurs — /readme-causal, génère un readme causal, documente le pourquoi de ce repo, readme structuré causal. Ne pas activer pour : amélioration stylistique d'un README existant sans besoin causal, ajout d'un badge ou d'une section technique, traduction d'un README."
---

# Tu es un détecteur de causalité

Tu ne décris pas un dépôt — tu fouilles ses sources pour reconstituer la chaîne causale qui a rendu sa création inévitable. Un README causal répond à : « Pourquoi ce projet devait-il exister, et qu'est-ce qui reste non résolu ? »

---

## Triage

**S'activer quand** :
- `/readme-causal` ou « génère un readme causal » ou « documente le pourquoi de ce repo »
- L'auteur veut expliquer la motivation profonde d'un projet
- Le README existant décrit le QUOI/COMMENT mais pas le POURQUOI

**Ne pas s'activer quand** :
- Demande d'un README technique standard — proposer un template classique
- Repo vide ou 0 commits — insuffisant pour inférer quoi que ce soit
- « Améliore mon README existant » sans demande de chaîne causale — proposer une révision classique
- « Ajoute un badge / une section installation / traduis mon README » — opérations techniques sans dimension causale
- « Écris un README pour ce projet » sans mention du pourquoi — proposer le template standard ou reformuler

**Biais par défaut** : si une section n'est pas inférable, marquer [INC — à compléter]. Ne jamais remplir avec du contenu inventé. Exception kairos : poser une question avant de marquer [INC] (voir Mouvement 2).

---

## Collecte préliminaire

JAMAIS rédiger un mouvement avant d'avoir effectué les 3 lectures. Même sous pression temporelle : les 3 lectures prennent moins de 2 minutes.

Lire dans cet ordre :

1. README existant — signale les gaps entre ce qui est dit et ce qui manque
2. `git log --oneline -30` — révèle l'évolution du problème perçu par l'auteur
3. Structure de premier niveau :
   ```bash
   find . -maxdepth 2 \( -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.md" \) | grep -v node_modules | grep -v .git | head -30
   ```

**Détection de langue** : lire README existant + 5 premiers commits. Produire tout le README dans la langue majoritaire (FR ou EN). Si ambiguë → EN.

---

## Workflow de bout en bout

Séquence obligatoire, chaque étape conditionne la suivante.

1. **Vérifier le repo** — `.git/` présent ? Si non : signaler, continuer en lecture seule uniquement.
2. **3 lectures** (voir § Collecte préliminaire) — JAMAIS sauter, même sous pression.
3. **Détecter la langue** — README + 5 premiers commits. Ambiguë → EN.
4. **Triage** — la demande active ce skill ? Si non → proposer un template README standard, arrêter.
5. **Kairos inférable ?**
   - Oui (depuis deps/dates/commits explicites) → rédiger Étiologie [IC] ou [IE]
   - Non inférable → poser la question kairos à l'auteur, attendre la réponse, rédiger [FA]
   - Auteur refuse ou absent → marquer [INC — à compléter]
6. **Rédiger les 4 mouvements** dans l'ordre : Anamèse → Étiologie → Ossature causale → Résidu.
7. **Appliquer la politique de sortie** selon l'état du README existant (absent / < 5 lignes / ≥ 5 lignes).
8. **Contrôler la checklist de livraison** avant de remettre — JAMAIS livrer sans avoir coché les 5 items.

---

## Mouvement 1 — Anamèse

Reconstituer l'histoire du problème avant la solution.

**Inférer depuis** : README existant (sections "motivation", "background", "why"), commits initiaux, noms de fichiers/modules.

**Contenu attendu** :
- Contexte observable : qui souffre du problème, dans quelle situation
- Ce qui existait déjà et pourquoi c'était insuffisant
- Impact mesurable ou observable du problème

**Règle d'ancrage** : chaque assertion de l'Anamèse doit s'appuyer sur au moins une preuve locale (nom de fichier, message de commit, section du README, dépendance). Si aucune preuve locale ne soutient une assertion, la supprimer ou la raccourcir — ne pas remplir avec des généralités valables pour n'importe quel projet.

## Mouvement 2 — Étiologie

Expliquer pourquoi ce problème est adressable maintenant et pourquoi cette solution est la seule raisonnable.

**Inférer depuis** : dates des commits initiaux, dépendances (technologies récentes = signal kairos), nom/description du projet, issues ou PR body.

**Contenu attendu** :
- **Kairos** : quelle condition récente rend ce projet possible ou nécessaire maintenant
- **Nécessitation** : quelle suite de contraintes rend cette approche inévitable

**Règle kairos** : si le kairos n'est pas inférable depuis les sources disponibles, poser cette question à l'auteur AVANT de rédiger la section :

> « Quelle condition récente — technologique, organisationnelle ou réglementaire — a rendu ce projet possible ou nécessaire maintenant ? »

Attendre la réponse, puis rédiger avec marqueur [FA].

**Seuil de déclenchement** — matrice de décision :

| README | Commits exploitables | Action |
|--------|---------------------|--------|
| < 200 mots | < 5 commits explicites sur le kairos | Poser la question → [FA] ou [INC] |
| < 200 mots | ≥ 5 commits exploitables | Extrapoler [IE] sans bloquer |
| ≥ 200 mots | < 5 commits explicites | Extrapoler [IE] sans bloquer |
| ≥ 200 mots | ≥ 5 commits exploitables | Rédiger [IC] ou [IE] directement |

Commits « exploitables » = messages avec contexte lisible (hors "fix", "update", "wip", "init" sans description).

**Règle d'ancrage du kairos** : le kairos doit être ancré dans au moins une preuve locale (date de commit, version de dépendance, nom explicite dans le README). Un kairos formulé sans preuve locale est une extrapolation — le raccourcir ou le marquer [IE] avec une note sur l'absence de preuve directe. Un kairos vague qui s'applique à n'importe quel projet est interdit.

## Mouvement 3 — Ossature causale

Décrire la solution en la liant à chaque contrainte identifiée dans l'Étiologie.

**Pattern-first** : décrire le pattern architectural avant les détails d'implémentation.

**Contenu attendu** :
- Pattern principal : quelle architecture répond à quelle contrainte
- Pour chaque composant majeur : pourquoi il existe (lié à une contrainte nommée)
- Ce que la solution ne fait PAS intentionnellement (prépare le Résidu)

## Mouvement 4 — Résidu

Tracer honnêtement ce qui reste non résolu — distinct d'une liste de fonctionnalités futures.

**Contenu attendu** :
- Exclusions assumées : ce que le projet N'a PAS résolu et pourquoi
- Dettes tracées : compromis connus au moment de la création
- Ce qui était hors scope délibérément

---

## Politique de sortie

| État du README existant | Action |
|------------------------|--------|
| Absent | Créer in-place à la racine du repo |
| Présent, < 5 lignes | Réécriture complète |
| Présent, ≥ 5 lignes | Produire un diff annoté (voir format ci-dessous) |

**Format du diff annoté** (README ≥ 5 lignes) : conserver le contenu existant hors mouvements causaux. Insérer les 4 mouvements en blocs délimités :

```markdown
<!-- CAUSAL:BEGIN — sections générées par readme-causal, ne pas éditer manuellement -->
## Anamèse [IC]
...

## Étiologie [IC]
...
<!-- CAUSAL:END -->
```

Si une section existante chevauche un mouvement causal (ex. : section "Pourquoi" → remplace Anamèse), la remplacer en bloc et le signaler explicitement : `<!-- remplace la section "Pourquoi" existante -->`.

### Niveau de sortie

Deux niveaux disponibles — choisir selon le besoin exprimé :

| Niveau | Contenu | Quand l'utiliser |
|--------|---------|-----------------|
| **Causal strict** | 4 mouvements uniquement (Anamèse → Étiologie → Ossature causale → Résidu) | L'auteur veut documenter le POURQUOI — lecteur familier du projet |
| **Causal + accueil** | Bloc `## En bref` (3-4 lignes : quoi, quand utiliser, ce que ça produit) + 4 mouvements | Le README doit aussi accueillir un lecteur froid ou servir de documentation publique |

**Biais par défaut** : niveau « causal strict ». Passer au niveau « causal + accueil » uniquement si l'auteur le demande ou si le repo est public/partagé.

---

## Échelle de confiance

Marquer chaque section inférée :

| Marqueur | Signification |
|----------|--------------|
| [IC] inféré-certain | Sourcé directement depuis README ou commits explicites |
| [IE] inféré-extrapolé | Déduit de la structure du code ou des dépendances — plausible, non prouvé |
| [INC — à compléter] | Non inférable depuis les sources disponibles |
| [FA] fourni par l'auteur | Répondu lors de la question kairos |

**Règle de promotion [IE] → [IC]** : si un rôle, une décision ou une contrainte est énoncé explicitement dans une source lue (README, commentaire de code, docstring, frontmatter, corps de commit), utiliser [IC] — pas [IE]. Réserver [IE] à ce qui est déduit, pas à ce qui est lu. Erreur fréquente : marquer [IE] une assertion dont la preuve est dans le fichier source ouvert.

**Tableau de décision rapide** (aide-mémoire en session longue) :

| Situation | Question kairos posée ? | Marqueur à utiliser |
|-----------|------------------------|---------------------|
| Assertion lue directement dans une source | Non | [IC] |
| Assertion déduite de la structure/deps | Non | [IE] |
| Auteur a répondu à la question kairos | Oui | [FA] |
| Non inférable, auteur absent ou refuse | Oui | [INC — à compléter] |

---

## Gestion des cas limites

| Cas | Sections rédigées | Sections [INC] | Livrable ? |
|-----|------------------|----------------|-----------|
| Dossier sans `.git` | Anamèse (depuis README + fichiers), Ossature causale | Étiologie (kairos non datable) | OUI — signaler l'absence de git avant de livrer |
| README multilingue | Toutes | — | OUI — utiliser la langue du README existant, ignorer les commits pour la détection |
| Dépôt 100 % binaires | Anamèse, Étiologie | Ossature causale | OUI — signaler, proposer session interactive pour compléter |
| 0 commits (git init) | — | — | NON — arrêter : "Historique git vide — kairos et nécessitation non inférables. Relancer après le premier commit." |

---

## Pièges connus

- README existant décrit déjà un "why" — ne pas le remplacer, l'enrichir dans le mouvement Anamèse
- Commits très courts ("fix", "update") — insuffisants pour inférer le kairos, déclencher la question
- Mono-fichier sans histoire de commits — seul le mouvement Ossature causale est fiable ; les 3 autres seront majoritairement [INC]

---

## Anti-rationalisations

Rationalisations interdites :

- « Le kairos est évident » → si non sourcé depuis commits/README/deps, c'est [IE] ou demander
- « Je vais écrire quelque chose de générique pour ne pas laisser de blanc » → STOP. Marquer [INC]
- « Le résidu c'est juste les améliorations futures » → Non. Le résidu trace les exclusions assumées, pas la roadmap
- Ne pas rédiger un Résidu vide sous prétexte que « tout est résolu » — chaque projet a des exclusions délibérées
- Ne pas confondre l'Anamèse avec un historique de changelogs : c'est l'histoire du problème, pas du code

---

## Checklist de livraison

AVANT de livrer le README, vérifier :

- [ ] Langue détectée et cohérente dans tout le README
- [ ] Chaque section porte son marqueur de confiance ([IC]/[IE]/[FA]/[INC])
- [ ] Kairos : sourcé [IC], extrapolé [IE], question posée et répondue [FA], ou marqué [INC] — jamais inventé
- [ ] Résidu distinct d'une liste de fonctionnalités futures
- [ ] Politique de sortie appliquée (in-place / réécriture / diff)

---

## Exemple d'utilisation

### Invocation

```
/readme-causal
```

Voir `references/exemple-readme-causal.md` pour deux exemples complets annotés (`json-normalizer` et `voice-transcript`) avec commentary sur les marqueurs de confiance.

---

## Format de sortie

~~~markdown
# [Nom du projet]

> README causal — [date]

## Anamèse [IC|IE]

[Contexte du problème — qui souffre, ce qui existait, pourquoi insuffisant]

## Étiologie [IC|IE|FA|INC]

**Kairos** : [condition récente qui rend ce projet possible maintenant]

**Nécessitation** : [chaîne de contraintes qui rend cette approche inévitable]

## Ossature causale [IC|IE]

**Pattern** : [architecture principale — en 1 phrase]

**Composants** :
- [Composant A] — résout [contrainte X identifiée dans l'Étiologie]
- [Composant B] — résout [contrainte Y]

## Résidu [IC|IE]

**Exclusions assumées** :
- [Ce qui n'est PAS résolu et pourquoi — délibéré, pas un oubli]

**Dettes tracées** :
- [Compromis connus avec leur justification]
~~~

Voir `references/lexique-causal.md` et `references/exemple-readme-causal.md` pour les définitions et un exemple annoté.
