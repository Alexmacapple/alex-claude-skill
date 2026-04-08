# Historique des versions -- /prompt-image

Historique complet des commits du skill `/prompt-image`, extrait du depot `claude-workflow-perso`.

---

## v1.1.0 -- 8 avril 2026

### Nouveaux presets

| Commit | Date | Description |
|--------|------|-------------|
| `963f614` | 08/04 20:17 | Ajout preset whiteboard-sketch v2.1 et enregistrement dans le catalogue |
| `dfb70aa` | 08/04 00:38 | Nouveau preset linkedin-editorial v1.0 + backport orbital-fracture v4.4 et bio-lumina v1.1 |
| `6405b2c` | 08/04 00:00 | Nouveaux presets ligne-claire v1.0 et digital-prestige v1.0 |

### Refontes et ameliorations de presets

| Commit | Date | Description |
|--------|------|-------------|
| `af1a487` | 08/04 00:02 | Backport operationnel ligne-claire-plus v2.1 vers v2.2 |
| `e205ffd` | 07/04 23:52 | Refonte presets flat-design v2.3 et spectrum v2.4 |
| `7ea3725` | 07/04 23:07 | Ajout spectrum couleur v2.3 (palettes nommees, 8 couleurs, fonds teintes) |

### Systeme de signature et plectrum

| Commit | Date | Description |
|--------|------|-------------|
| `c1ec416` | 07/04 22:24 | tech-dark v4.3 propagation plectrum complete |
| `4a49c02` | 07/04 22:22 | Plectrum v4.2 et schema L0 v1.1 (signature, tension mechanics, strike point) |
| `0e3343b` | 07/04 22:07 | Preset tech-dark v4.1 avec signature visuelle |

### Renommages et suppressions

| Commit | Date | Description |
|--------|------|-------------|
| `51ac5a2` | 07/04 23:03 | Suppression preset fracture-bloom (fusion trop marquee entre orbital-fracture et bio-lumina) |
| `01faf5a` | 07/04 22:36 | Renommage preset tech-dark en orbital-fracture |

### Bio-lumina

| Commit | Date | Description |
|--------|------|-------------|
| `fcd5d18` | 07/04 22:50 | Nouveau preset bio-lumina v1.0 (bioluminescence organique, architecture vegetale nocturne) |
| `b998c8b` | 07/04 22:56 | Preset hybride fracture-bloom v1.0 (retire ensuite) |

### Documentation

| Commit | Date | Description |
|--------|------|-------------|
| `193ffdc` | 08/04 20:26 | Ajout guide utilisateur complet + nettoyage PRD obsolete |

---

## v1.0.0 -- 7 avril 2026

### Creation du skill

| Commit | Date | Description |
|--------|------|-------------|
| `fd0d82e` | 07/04 18:53 | Ajout skill /prompt-image v1.0 (pipeline raffinement image, SKILL.md, references, schema L0) |

### Presets initiaux et iterations

| Commit | Date | Description |
|--------|------|-------------|
| `de6c0df` | 07/04 19:32 | Ajout bibliotheque de presets et corrections post-review |
| `06fff12` | 07/04 19:38 | Ajout preset flat-design et mise a jour catalogue |
| `df3108c` | 07/04 19:41 | Enrichissement preset flat-design avec guidelines Hyperprompt |
| `b7603c2` | 07/04 19:42 | Refonte preset flat-design v2.0 avec analyse experte |
| `577cc57` | 07/04 19:48 | Refonte preset ligne-claire-plus v2.0 post-review expert |
| `bb106d4` | 07/04 19:50 | Refonte preset tech-dark v2.0 post-review expert |
| `ecab9ff` | 07/04 19:53 | Refonte preset flat-design v2.1 post-review expert |
| `c99ecc3` | 07/04 19:58 | Finition preset tech-dark v2.1 post-review expert |
| `6abc984` | 07/04 20:08 | Finition des 3 presets post-review expert (ameliorations v2.1-2.2) |

---

## Etat actuel des presets

| Preset | Version | Genre |
|--------|---------|-------|
| ligne-claire-plus | 2.2 | Ligne claire franco-belge rehaussee |
| ligne-claire | 1.0 | Ligne claire franco-belge classique |
| orbital-fracture | 4.4 | Geometrie orbitale fracturee, luminescence chirurgicale |
| bio-lumina | 1.1 | Bioluminescence organique, architecture vegetale nocturne |
| flat-design | 2.3 | Illustration vectorielle minimaliste (4-6 couleurs) |
| flat-design-spectrum | 2.4 | Flat design avec palettes etendues (8 couleurs) |
| digital-prestige | 1.0 | Illustration digitale prestige, roman graphique moderne |
| linkedin-editorial | 1.0 | Editorial warm prestige pour LinkedIn |
| whiteboard-sketch | 2.1 | Diagramme technique style tableau blanc premium |

---

## Fichiers de reference

| Fichier | Contenu |
|---------|---------|
| `SKILL.md` | Orchestrateur principal du pipeline |
| `references/methode-raffinement.md` | 4 passes de verification, arbre de decision, termes interdits |
| `references/nano-banana-2.md` | Guide Nano Banana 2 (structure 5 blocs, faiblesses, suffixes) |
| `references/qwen-image-2.md` | Guide Qwen-Image 2.0 (7 regles, capacites avancees, parametres) |
| `references/schema-style-guide.md` | Contrat JSON des style guides (schema L0 v1.1) |

---

**Depot source** : `claude-workflow-perso` (prive)
**Derniere mise a jour** : 8 avril 2026
