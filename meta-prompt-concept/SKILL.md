---
name: meta-prompt-concept
version: 1.0.0
description: "Génère des prompts incarnés où le LLM EST le concept (pas un expert DU concept). Utiliser quand l'utilisateur demande un prompt concept, incarner un concept ou générer un méta-prompt. Do NOT use for: prompts classiques ou system prompts génériques."
allowed-tools: Read, Write, Edit, Bash, Agent
argument-hint: "[concept à incarner] [--compact] [--sans-evaluation]"
context: conversation
---

# Skill : /meta-prompt-concept

Génère des prompts où le LLM EST le concept plutôt qu'un expert DU concept.
Transforme un concept métier, une discipline ou un mode de raisonnement en
prompt structuré avec mouvements naturels, triage, détection du hedging et
échelle de certitude.

**Principe** : "Tu es un expert en X" produit du générique. "Tu es X" produit
du structurel. Ce skill applique systématiquement la seconde approche.

**Inspiration** : Concept d'incarnation des concepts métiers + méthode de
structuration itérative.

---

## Déclencheurs

- `/meta-prompt-concept`, `/concept`, `/incarnation`
- "crée un prompt concept pour X"
- "incarne le concept de X"
- "cristallise X en prompt"
- "génère un meta-prompt pour X"

---

## Arguments

| Argument | Description | Défaut |
|----------|-------------|--------|
| `concept` | Le concept à incarner (texte libre) | obligatoire |
| `--compact` | Produire la version compacte (~200 mots) en plus | non |
| `--sans-evaluation` | Désactiver la méta-évaluation du prompt produit | non |

---

## Triage d'entrée

Avant de lancer la cristallisation, vérifier que le concept est incarnable :

| Type | Action |
|------|--------|
| **Incarnable** — processus avec phases naturelles identifiables (discipline, fonction métier, mode de raisonnement) | Lancer les 5 phases |
| **Outil ou tâche** — opération unitaire sans processus répétable ("convertis ce CSV", "trie cette liste") | Refuser poliment, suggérer un prompt classique |
| **Trop abstrait** — impossible d'identifier 3 mouvements naturels ("la vérité", "l'intelligence") | Demander un ancrage concret (cas d'usage) |

> En cas de doute : demander un cas d'usage concret.
> Un concept sans contexte d'application produit un prompt creux.

---

## Contraintes

| Règle | Description |
|-------|-------------|
| **Incarnation, pas simulation** | "Tu es [concept]" = instruction d'architecture, pas métaphore |
| **Mouvements, pas étapes** | Dynamique naturelle, pas procédure rigide |
| **4 obligatoires** | Chaque prompt produit DOIT inclure : triage + hedging + clause d'accès + mode compact |
| **Densité maximale** | Si une phrase est supprimable sans perte fonctionnelle, la supprimer |
| **Héritage** | Chaque prompt produit hérite : clause d'accès aux sources, mode compact, échelle 4 niveaux, détection hedging |
| **Échelle à 4 niveaux** | Toujours avec symboles visuels distincts, adaptés au domaine du concept |

---

## Workflow

### Phase 1 : Validation

1. Parser les arguments (concept + flags)
2. Appliquer le triage d'entrée (incarnable / outil / abstrait)
3. Si non incarnable : expliquer pourquoi et s'arrêter
4. Si incarnable : lire `references/methode-incarnation.md`

### Phase 2 : Cristallisation (sous-agent)

1. Lire `references/methode-incarnation.md` depuis l'orchestrateur
2. Injecter son contenu INLINE dans le prompt du sous-agent
   (le sous-agent n'a pas forcément accès à Read — ne pas compter dessus)
3. Lancer un sous-agent `general-purpose` avec le prompt de cristallisation
   depuis `references/prompts.md` (prompt substitué avec le concept
   et le contenu de la méthode injecté)

Le sous-agent exécute les 5 phases :
1. **Essence** — "Tu es [processus], pas [rôle]." 2 lignes max.
2. **Mouvements** — 3 à 5 phases naturelles. 1 mot + 1 ligne chacun.
3. **Régulation** — Triage + clause de biais par défaut + limites.
4. **Instrumentation** — Échelle 4 niveaux + format complet/compact + détection hedging + clause d'accès.
5. **Ancrage** — 1 exemple complet montrant les deux modes.

### Phase 3 : Vérification et livraison

1. Vérifier que le prompt produit contient les 4 obligatoires :
   - [ ] Triage avec clause de biais par défaut
   - [ ] Détection du hedging (min 2 exemples spécifiques au domaine)
   - [ ] Clause d'accès aux sources
   - [ ] Mode compact documenté et illustré dans l'exemple
2. Si un obligatoire manque : relancer le sous-agent avec rappel
3. Sauf si `--sans-evaluation` : produire la méta-évaluation
4. Si `--compact` : produire la version compacte (~200 mots)
5. Livrer le prompt final

**Vérification de densité** (manuelle) : relire le prompt produit et
identifier toute phrase supprimable sans perte fonctionnelle. La densité
n'est pas mesurable par script — c'est un jugement qualitatif de
l'orchestrateur.

---

## Format de sortie

### Prompt incarné (livrable principal)

```
# Tu es [nom du concept incarné]

[Phrase d'identité — 2 lignes max]

---

## Triage
[Quand s'activer / ne pas s'activer / clause de biais par défaut]

---

## Les [N] mouvements
[Mouvements naturels du concept, 3 à 5]

---

## Règles
[Contraintes + détection hedging + échelle + clause d'accès]

---

## Format de sortie
[Mode complet + mode compact, en blocs ~~~]

---

## Exemple
[Un cas concret : mode complet + mode compact]

---

*[Attribution et inspiration]*
```

### Méta-évaluation (par défaut, désactivable avec `--sans-evaluation`)

~~~
ESSENCE : [le concept incarné en 5 mots max]
MOUVEMENTS : [N] — [naturels ou forcés ?]
TRIAGE : [présent + clause de biais ? oui/non]
HEDGING : [détection incluse ? exemples spécifiques ? oui/non]
ACCÈS : [clause de limites incluse ? oui/non]
COMPACT : [mode compact dans format ET exemple ? oui/non]
DENSITÉ : [mots du prompt] — [phrase supprimable ? oui/non]
VERDICT : [prêt / à itérer] — [faiblesse principale ou "aucune"]
~~~

### Version compacte (si `--compact`)

Version ~200 mots du prompt, même contenu fonctionnel :
- Triage en 3 lignes
- Mouvements en liste à puces
- Règles fusionnées
- Pas d'exemple (renvoyer vers la version complète)

---

## Gestion des erreurs

| Situation | Message | Action |
|-----------|---------|--------|
| Concept vide | "Quel concept incarner ?" | Demander le concept |
| Concept = tâche | "X est une tâche, pas un concept" | Suggérer prompt classique |
| Concept trop abstrait | "X est trop large. Cas d'usage ?" | Demander ancrage |
| Sous-agent oublie un obligatoire | "Triage/hedging/accès/compact manquant" | Relancer avec rappel |
| 2 échecs consécutifs du sous-agent | "Cristallisation échouée" | Livrer le meilleur effort |

---

## Exemples

Voir `references/exemples.md` pour les exemples complets :
- **Doute méthodique** : incarnation du fact-checking itératif (Caulfield, 2025) — verdict : prêt
- **Questionnement du code** : incarnation de la code review — verdict : prêt
- **Empathie** : concept limite (trop abstrait sans ancrage) — verdict : à itérer

---

## Checklist finale

- [ ] Le concept est incarnable (pas une tâche, pas trop abstrait)
- [ ] Le prompt contient un triage avec clause de biais par défaut
- [ ] Le prompt contient une détection du hedging (min 2 exemples spécifiques)
- [ ] Le prompt contient une clause d'accès aux sources
- [ ] Le prompt contient un mode compact documenté ET illustré dans l'exemple
- [ ] Le prompt fait moins de 500 mots (densité maximale)
- [ ] La méta-évaluation ne gonfle pas le verdict (honnêteté)

---

## Architecture

- **Skill** (ce fichier) = orchestrateur et validation
- **Sous-agent** (via `Agent tool`, `subagent_type="general-purpose"`) = cristallisation
- **Références** :
  - `methode-incarnation.md` : les 5 phases détaillées
  - `prompts.md` : prompt du sous-agent de cristallisation
  - `exemples.md` : exemples complets avec méta-évaluation
