# Guide de conception de skills

## Nature des skills

Les skills sont des paquets modulaires et autonomes qui étendent les capacités de Claude en fournissant des connaissances spécialisées, des workflows et des outils. Ce sont des guides d'intégration pour des domaines ou tâches spécifiques — ils transforment Claude d'un agent généraliste en un agent spécialisé équipé de connaissances procédurales qu'aucun modèle ne peut posséder entièrement.

### Ce que fournissent les skills

1. **Workflows spécialisés** — Procédures multi-étapes pour des domaines spécifiques
2. **Intégrations d'outils** — Instructions pour travailler avec des formats de fichiers ou des APIs
3. **Expertise métier** — Connaissances spécifiques à une entreprise, schémas, logique métier
4. **Ressources embarquées** — Scripts, références et assets pour les tâches complexes et répétitives

## Concision

La fenêtre de contexte est un bien commun. Les skills partagent la fenêtre de contexte avec tout ce dont Claude a besoin : prompt système, historique de conversation, métadonnées des autres skills et la requête utilisateur.

**Hypothèse par défaut : Claude est déjà très intelligent.** N'ajouter que le contexte que Claude ne possède pas déjà. Questionner chaque information : « Claude a-t-il vraiment besoin de cette explication ? » et « Ce paragraphe justifie-t-il son coût en tokens ? »

Préférer des exemples concis aux explications verbeuses.

## Degrés de liberté

Adapter le niveau de spécificité à la fragilité et la variabilité de la tâche :

**Liberté élevée (instructions textuelles)** : Quand plusieurs approches sont valides, les décisions dépendent du contexte, ou des heuristiques guident l'approche.

**Liberté moyenne (pseudocode ou scripts paramétrés)** : Quand un pattern préféré existe, une certaine variation est acceptable, ou la configuration affecte le comportement.

**Liberté faible (scripts spécifiques, peu de paramètres)** : Quand les opérations sont fragiles, la cohérence est critique, ou une séquence précise doit être suivie.

Imaginer Claude explorant un chemin : un pont étroit avec des falaises nécessite des garde-fous précis (liberté faible), tandis qu'un champ ouvert permet de nombreuses routes (liberté élevée).

## Anatomie d'un skill

Chaque skill se compose d'un fichier SKILL.md obligatoire et de ressources optionnelles :

```
skill-name/
+-- SKILL.md (obligatoire)
|   +-- Frontmatter YAML (obligatoire)
|   |   +-- name: (obligatoire)
|   |   +-- description: (obligatoire)
|   |   +-- compatibility: (optionnel, rarement nécessaire)
|   +-- Instructions Markdown (obligatoire)
+-- Ressources embarquées (optionnel)
    +-- scripts/          - Code exécutable (Python/Bash/etc.)
    +-- references/       - Documentation chargée dans le contexte selon besoin
    +-- assets/           - Fichiers utilisés en sortie (templates, icônes, polices, etc.)
```

### SKILL.md (obligatoire)

Chaque SKILL.md se compose de :

- **Frontmatter** (YAML) : Contient les champs `name` et `description` (obligatoires), plus des champs optionnels comme `license`, `metadata` et `compatibility`. Seuls `name` et `description` sont lus par Claude pour déterminer quand le skill se déclenche — être clair et exhaustif sur ce que fait le skill et quand l'utiliser. Le champ `compatibility` sert à noter les prérequis d'environnement mais la plupart des skills n'en ont pas besoin.
- **Corps** (Markdown) : Instructions et guide d'utilisation du skill. Chargé uniquement APRÈS le déclenchement du skill.

### Ressources embarquées (optionnel)

#### Scripts (`scripts/`)

Code exécutable (Python/Bash/etc.) pour les tâches nécessitant une fiabilité déterministe ou étant réécrites de façon répétitive.

- **Quand inclure** : Quand le même code est réécrit de façon répétitive ou qu'une fiabilité déterministe est nécessaire
- **Exemple** : `scripts/rotate_pdf.py` pour la rotation de PDF
- **Avantages** : Économe en tokens, déterministe, exécutable sans chargement dans le contexte
- **Note** : Les scripts peuvent quand même nécessiter une lecture par Claude pour du patching ou des ajustements spécifiques à l'environnement

#### Références (`references/`)

Documentation et matériel de référence destinés à être chargés dans le contexte selon les besoins.

- **Quand inclure** : Pour la documentation que Claude doit consulter pendant le travail
- **Exemples** : `references/finance.md` pour les schémas financiers, `references/policies.md` pour les politiques d'entreprise, `references/api_docs.md` pour les spécifications API
- **Cas d'usage** : Schémas de base de données, documentation API, connaissances métier, politiques d'entreprise, guides de workflow détaillés
- **Avantages** : Maintient le SKILL.md léger, chargé uniquement quand Claude détermine que c'est nécessaire
- **Bonne pratique** : Si les fichiers sont volumineux (>10k mots), inclure des patterns de recherche grep dans le SKILL.md
- **Éviter la duplication** : L'information doit vivre soit dans le SKILL.md soit dans les fichiers de références, pas les deux. Préférer les fichiers de références pour les informations détaillées.

#### Assets (`assets/`)

Fichiers non destinés à être chargés dans le contexte, mais utilisés dans la sortie produite par Claude.

- **Quand inclure** : Quand le skill nécessite des fichiers utilisés dans la sortie finale
- **Exemples** : `assets/logo.png`, `assets/slides.pptx`, `assets/frontend-template/`, `assets/font.ttf`
- **Cas d'usage** : Templates, images, icônes, code boilerplate, polices, documents types à copier ou modifier
- **Avantages** : Sépare les ressources de sortie de la documentation, permet à Claude d'utiliser les fichiers sans les charger dans le contexte

### Ce qu'il ne faut PAS inclure

Un skill ne doit contenir que les fichiers essentiels à sa fonctionnalité. Ne PAS créer de documentation ou fichiers auxiliaires superflus : README.md, INSTALLATION_GUIDE.md, QUICK_REFERENCE.md, CHANGELOG.md, etc.

## Divulgation progressive

Les skills utilisent un système de chargement à trois niveaux :

1. **Métadonnées (name + description)** — Toujours dans le contexte (~100 mots)
2. **Corps du SKILL.md** — Au déclenchement du skill (<5k mots)
3. **Ressources embarquées** — Selon les besoins de Claude (illimité car les scripts peuvent être exécutés sans lecture dans le contexte)

### Patterns de divulgation

Maintenir le corps du SKILL.md à l'essentiel et sous 500 lignes. Découper le contenu en fichiers séparés quand on approche cette limite. Lors du découpage, référencer les fichiers depuis le SKILL.md et décrire clairement quand les lire.

**Principe clé :** Quand un skill supporte plusieurs variations, ne garder que le workflow principal et le guide de sélection dans le SKILL.md. Déplacer les détails spécifiques aux variantes dans des fichiers de références séparés.

**Pattern 1 : Guide de haut niveau avec références**

```markdown
## Traitement PDF

### Démarrage rapide

Extraire le texte avec pdfplumber :
[exemple de code]

### Fonctionnalités avancées

- **Formulaires** : Voir [FORMS.md](FORMS.md) pour le guide complet
- **Référence API** : Voir [REFERENCE.md](REFERENCE.md) pour toutes les méthodes
```

Claude charge FORMS.md ou REFERENCE.md uniquement quand c'est nécessaire.

**Pattern 2 : Organisation par domaine**

Pour les skills couvrant plusieurs domaines, organiser par domaine pour éviter de charger du contexte non pertinent :

```
bigquery-skill/
+-- SKILL.md (vue d'ensemble et navigation)
+-- reference/
    +-- finance.md (revenus, métriques de facturation)
    +-- sales.md (opportunités, pipeline)
    +-- product.md (utilisation API, fonctionnalités)
```

De même, pour les skills supportant plusieurs frameworks :

```
cloud-deploy/
+-- SKILL.md (workflow + sélection du provider)
+-- references/
    +-- aws.md (patterns de déploiement AWS)
    +-- gcp.md (patterns de déploiement GCP)
    +-- azure.md (patterns de déploiement Azure)
```

**Pattern 3 : Détails conditionnels**

```markdown
## Traitement DOCX

### Création de documents

Utiliser docx-js pour les nouveaux documents. Voir [DOCX-JS.md](DOCX-JS.md).

### Édition de documents

Pour les éditions simples, modifier le XML directement.

**Pour le suivi de modifications** : Voir [REDLINING.md](REDLINING.md)
**Pour les détails OOXML** : Voir [OOXML.md](OOXML.md)
```

**Directives importantes :**

- **Éviter les références profondément imbriquées** — Garder les références à un seul niveau de profondeur depuis le SKILL.md.
- **Structurer les fichiers de référence longs** — Pour les fichiers de plus de 100 lignes, inclure une table des matières en haut.
