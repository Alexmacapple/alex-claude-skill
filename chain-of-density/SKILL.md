---
name: chain-of-density
version: 2.0.0
description: "Densifie itérativement des résumés via la technique Chain-of-Density. Utiliser pour compresser de la documentation verbeuse, condenser des spécifications ou créer des synthèses exécutives en préservant la densité informationnelle."
allowed-tools: Read, Bash, Glob, Agent
argument-hint: "[texte ou fichier] [--iterations 5] [--mots-cibles 80] [--historique]"
context: conversation
---

# Skill : /chain-of-density

Compresse un texte par injection itérative d'entités suivant la méthodologie du papier Chain-of-Density (CoD). Chaque passe identifie les entités manquantes de la source et les incorpore en maintenant un nombre de mots identique.

**Référence** : [From Sparse to Dense: GPT-4 Summarization with Chain of Density Prompting](https://arxiv.org/abs/2309.04269)

---

## Déclencheurs

- `/chain-of-density`, `/cod`
- "densifie ce texte", "résumé dense", "condense ce document"
- "chain of density", "synthèse dense"
- Toute demande de compression itérative de texte

---

## Arguments

| Argument | Description | Défaut |
|----------|-------------|--------|
| `texte ou fichier` | Texte brut ou chemin vers un fichier `.md`/`.txt` | obligatoire |
| `--iterations N` | Nombre de passes de densification | 5 |
| `--mots-cibles N` | Nombre de mots maintenu à chaque itération | 80 |
| `--historique` | Inclure les résumés intermédiaires + entités | non |

Parsing via `$ARGUMENTS` :
- Si l'argument est un chemin de fichier existant, lire son contenu
- Si c'est du texte brut, l'utiliser directement
- Les flags `--iterations`, `--mots-cibles`, `--historique` sont optionnels

---

## Principes de la méthode CoD

**Voir `references/methode-cod.md`** pour les principes détaillés et les 5 critères des entités manquantes (Adams et al., 2023).

---

## Contraintes

| Règle | Description |
|-------|-------------|
| **Texte source intégral** | Ne JAMAIS pré-digérer, résumer ou reformuler le texte source. Chaque sous-agent lit le fichier `/tmp/${COD_ID}.txt` lui-même |
| **Sérialisation** | Les itérations sont exécutées une par une, jamais en parallèle. Chaque itération dépend de la sortie de la précédente |
| **Tolérance de comptage** | Le résumé doit faire exactement `mots_cibles` mots (+-3 mots). Au-delà, relancer l'itération |
| **Limites de taille** | < 100 mots : refuser (résumé classique). < 300 mots : avertir (CoD moins efficace). > 50 000 mots : refuser (découper) |
| **Non-régression** | Ne JAMAIS supprimer une entité déjà intégrée dans un résumé précédent |
| **Fidélité** | Aucune entité inventée — chaque ajout doit être vérifiable dans le texte source |
| **Langue de sortie** | Détecter la langue du texte source. Tous les résumés doivent être rédigés dans cette même langue. Seuls les en-têtes de sortie (étiquettes YAML, noms de colonnes) restent en français |
| **Convention de comptage** | Un mot = toute séquence séparée par des espaces. Mots composés (« c'est-à-dire ») = 1, nombres (« 2023 ») = 1, acronymes (« RGPD ») = 1. Source de vérité : `scripts/text_metrics.py` |

---

## Workflow

### Phase 1 : Préparation

1. Parser `$ARGUMENTS` pour extraire le texte source, les paramètres
2. Si c'est un fichier, lire son contenu avec `Read`
3. **OBLIGATOIRE** : Écrire le texte source brut INTÉGRAL dans un fichier temporaire :

```bash
# Capturer un identifiant unique pour la session
COD_ID="cod-source-$(date +%s)"
# Copier le contenu brut dans un fichier temporaire
cat /chemin/vers/source.md > /tmp/${COD_ID}.txt
# OU pour du texte brut :
cat <<'EOFSOURCE' > /tmp/${COD_ID}.txt
[texte brut ici]
EOFSOURCE
```

**Note** : Le suffixe `$COD_ID` (timestamp) est stable entre appels Bash successifs dans une même session. Réutiliser ce même chemin dans les prompts des sous-agents et lors du nettoyage en phase 3.

**RÈGLE ABSOLUE** : Ne JAMAIS pré-digérer, résumer ou reformuler le texte source avant de le passer aux sous-agents. Chaque sous-agent DOIT lire le fichier `/tmp/${COD_ID}.txt` lui-même pour accéder au texte original intégral. Cette règle prévient la perte d'information entre l'orchestrateur et les sous-agents.

4. Compter les mots du texte source (`$SKILL_DIR` = variable native Claude Code, résout vers le répertoire du skill) :

```bash
python3 "${SKILL_DIR}/scripts/text_metrics.py" words < /tmp/${COD_ID}.txt
```

5. Vérifier les limites du texte source :
   - Si moins de 100 mots : refuser et suggérer un résumé classique (CoD inadaptée)
   - Si moins de 300 mots : avertir « Ce texte fait moins de 300 mots. La technique Chain-of-Density est plus efficace sur des textes plus longs. Continuer quand même ? »
   - Si plus de 50 000 mots : refuser et suggérer de découper le texte en sections

6. Ajuster `mots_cibles` si nécessaire (textes très longs = augmenter)

### Phase 2 : Itérations (sérialisées)

Exécuter les itérations une par une via des sous-agents inline (`Agent tool`).

**CRITIQUE** : Les itérations doivent être sérialisées (jamais en parallèle). Chaque itération dépend de la sortie de la précédente.

Les prompts complets des sous-agents sont dans `references/prompts.md`. L'orchestrateur substitue les variables avant injection : `[N]` = `mots_cibles`, `[N_TOTAL]` = `iterations`, `[N_TOTAL_MOINS_1]` = `iterations - 1`, `[I]` = numéro d'itération, `[X]` = mots du résumé précédent, `$$` = valeur de `$COD_ID` (timestamp capturé en phase 1).

Syntaxe d'appel :

```
Agent(subagent_type="general-purpose", prompt="[prompt substitué depuis references/prompts.md]")
```

**Itération 1** — Le sous-agent lit le fichier source et produit un résumé volontairement épars et verbeux de `mots_cibles` mots, sans entités spécifiques. Le remplissage est intentionnel : c'est du texte sacrificiel que les itérations suivantes remplaceront par des entités. Utiliser des expressions creuses typiques : « cet article traite de », « il est intéressant de noter que », « on peut observer que », « dans le contexte de ».

**Itérations 2 à N** — Le sous-agent reçoit le résumé précédent, lit le fichier source, identifie 1-3 entités manquantes (5 critères), densifie le résumé en les intégrant par compression, puis vérifie le comptage et la non-régression avant de répondre. Le résumé doit rester auto-suffisant (compréhensible sans le texte source).

**Retry sur comptage divergent** — Si un sous-agent retourne un résumé hors tolérance (+-3 mots), relancer l'itération avec un rappel explicite du `mots_cibles`. Maximum 2 tentatives par itération. Après 2 échecs consécutifs, livrer le dernier résumé valide et passer à la phase 3.

### Phase 3 : Vérification et livraison

1. Compter les mots du résumé final :

```bash
python3 "${SKILL_DIR}/scripts/text_metrics.py" words <<< "résumé final"
```

2. Vérifier que le compte est dans la tolérance (+-3 mots de `mots_cibles`)
3. Nettoyer le fichier temporaire :

```bash
rm -f /tmp/${COD_ID}.txt
```

4. Afficher le résultat selon le format demandé

---

## Pattern d'orchestration

```
Itération 1 : Base éparse (mots_cibles, remplissage verbeux)
     | Entités_Manquantes: (aucune - base)
Itération 2 : +3 entités, compression du remplissage
     | Entités_Manquantes: "entité1"; "entité2"; "entité3"
Itération 3 : +3 entités, compression supplémentaire
     | Entités_Manquantes: "entité4"; "entité5"; "entité6"
Itération 4 : +2 entités, resserrement
     | Entités_Manquantes: "entité7"; "entité8"
Itération 5 : +1-2 entités, densité maximale
     | Entités_Manquantes: "entité9"
Résumé final dense (même nombre de mots, 9+ entités)
```

---

## Format de sortie

### Minimal (défaut)

```
[Résumé dense final]
```

### Avec historique (`--historique`)

```yaml
resume_final: |
  [Résumé dense au mots_cibles avec toutes les entités accumulées]
iterations:
  - tour: 1
    entites_manquantes: "(aucune - établissement de la base)"
    mots: 80
    resume: |
      [Résumé épars itération 1]
  - tour: 2
    entites_manquantes: "entité1; entité2; entité3"
    mots: 80
    resume: |
      [Résumé plus dense itération 2]
  # ... etc
total_entites: 9
```

---

## Quand utiliser

- Documentation verbeuse dépassant 500 mots
- Cahiers des charges à condenser
- Synthèses exécutives à partir de rapports détaillés
- Compression de skills trop longs

## Quand NE PAS utiliser

- Textes juridiques/conformité (précision requise)
- Tutoriels (les débutants ont besoin des explications)
- Contenu déjà concis (moins de 300 mots)
- Spécifications techniques (ne pas compresser les specs)

---

## Exemples

Format minimal (source : 342 mots sur les skills Claude Code) :

```
/chain-of-density rapport.md --mots-cibles 80

→ Les skills Claude Code sont définis par un fichier SKILL.md dans
  .claude/skills/ avec frontmatter YAML obligatoire : name (kebab-case,
  regex ^[a-z0-9]+(-[a-z0-9]+)*$, 1-64 caractères), description (1-1024
  caractères, déclencheurs et mots-clés de découverte), allowed-tools et
  context (conversation ou fork). Divulgation progressive via
  sous-répertoires references/, assets/, scripts/. Orchestration de tâches
  complexes par Agent (sous-agents stateless). Le pipeline skill-pipeline
  enchaîne skill-creator, skill-conformity-checker (/50) et skill-review
  (/100) pour un score combiné /150. Multi-plateformes : Claude Code CLI,
  Cursor, GitHub Copilot.
```

**Exemples complets avec itérations intermédiaires** : voir `references/exemples.md`.

Format historique (source : 299 mots sur le catalogue de 34 skills) :

```yaml
/chain-of-density spec.md --historique --iterations 3 --mots-cibles 100

→ resume_final: |
    Ce workspace propose 34 skills en 7 catégories : quotidien,
    accessibilité (9 skills dont /audit-a11y), qualité (/skill-pipeline
    score combiné /150), IA multi-modèles, rédaction, spécialisés et
    utilitaires.
  iterations:
    - tour: 1
      entites_manquantes: "(aucune - établissement de la base)"
      mots: 98
    - tour: 2
      entites_manquantes: "/pdf; /audit-a11y; /council"
      mots: 102
    - tour: 3
      entites_manquantes: "34 skills; 9 skills accessibilité; /skill-pipeline /150"
      mots: 97
  total_entites: 6
```

**Exemples complets avec itérations intermédiaires** : voir `references/exemples.md`.

---

## Gestion des erreurs

| Situation | Message | Action |
|-----------|---------|--------|
| Texte source vide | "Aucun texte fourni" | Demander le texte |
| Fichier introuvable | "Fichier X introuvable" | Vérifier le chemin |
| Texte trop court (<100 mots) | "Texte trop court pour CoD" | Suggérer un résumé classique |
| Comptage divergent (>3 mots d'écart) | "Le résumé fait X mots au lieu de Y" | Relancer l'itération |
| Agent retourne un format invalide | "Format de sortie inattendu" | Relancer avec rappel du format |
| Sous-agent timeout (pas de réponse) | "Timeout itération X" | Relancer l'itération (max 2 tentatives) |
| 2 échecs consécutifs sur une itération | "Itération X échouée après 2 tentatives" | Livrer le dernier résumé valide |
| Texte source trop long (>50 000 mots) | "Texte de X mots, limite 50k" | Suggérer de découper le texte |

---

## Checklist finale

- [ ] Le résumé final respecte le `mots_cibles` (+-3 mots)
- [ ] Toutes les entités accumulées sont présentes dans le résumé final
- [ ] Aucune entité n'a été inventée (fidélité à la source)
- [ ] Le résumé est compréhensible sans le texte source
- [ ] Le format de sortie correspond à la demande (minimal ou historique)

---

## Architecture

- **Skill** (ce fichier) = orchestrateur des itérations
- **Sous-agents inline** (via `Agent tool`, `subagent_type="general-purpose"`) = travailleurs stateless par itération (prompts dans `references/prompts.md`)
- **Script** (`scripts/text_metrics.py`) = utilitaire déterministe de comptage

`Agent` dans `allowed-tools` correspond à l'outil natif Claude Code qui lance des sous-agents autonomes. Les sous-agents ne peuvent pas appeler d'autres sous-agents. Seul le skill orchestre via cet outil.
