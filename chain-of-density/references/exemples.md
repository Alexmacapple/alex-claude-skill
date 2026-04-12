# Exemples Chain-of-Density

Exemples concrets d'entrées/sorties pour les deux formats de livraison. Tous les comptages de mots ont été vérifiés avec `scripts/text_metrics.py`.

---

## Exemple 1 : format minimal (défaut)

**Commande** : `/chain-of-density source.md`

**Source** (342 mots) :

> Les skills Claude Code sont des fichiers Markdown structurés qui étendent les capacités de l'assistant. Chaque skill est défini par un fichier SKILL.md placé dans un sous-répertoire de .claude/skills/. Le frontmatter YAML contient les métadonnées obligatoires : name (1-64 caractères, format kebab-case avec regex ^[a-z0-9]+(-[a-z0-9]+)*$), description (1-1024 caractères, doit inclure les déclencheurs « Utiliser quand... » et les mots-clés de découverte pour l'invocation automatique), et allowed-tools (liste des outils autorisés comme Read, Bash, Glob, Agent). Les champs optionnels incluent context (conversation ou fork), argument-hint pour guider l'utilisateur, et version pour le suivi sémantique. Le corps du fichier Markdown contient les instructions complètes : déclencheurs, arguments, workflow détaillé, format de sortie, gestion des erreurs et exemples. La divulgation progressive est encouragée via des sous-répertoires references/ pour les données volumineuses, assets/ pour les ressources statiques, et scripts/ pour les utilitaires. Les skills peuvent orchestrer des sous-agents via l'outil Agent (subagent_type="general-purpose") pour paralléliser ou sérialiser des tâches complexes. Chaque sous-agent est stateless et reçoit un prompt complet incluant toutes les instructions nécessaires. Le skill skill-creator d'Anthropic fournit un guide officiel de création avec bonnes pratiques : nommer les fichiers en kebab-case, limiter la description à 1024 caractères, utiliser le champ context approprié (conversation pour les chaînages d'outils, fork pour les tâches isolées). La validation structurelle se fait via skill-conformity-checker (score /50) qui vérifie la présence des champs obligatoires, le format du frontmatter et la cohérence des sections. L'évaluation sémantique se fait via skill-review (score /100) qui analyse la clarté des instructions, la robustesse des garde-fous, la qualité des exemples et l'adéquation du workflow. Le pipeline complet skill-pipeline enchaîne les trois étapes : création, validation structurelle et évaluation sémantique, avec un score combiné /150. Les skills sont multi-plateformes et fonctionnent dans Claude Code CLI, Cursor et GitHub Copilot.

**Itération 1** (éparse, 82 mots) :

```
Entites_Manquantes: (aucune - établissement de la base éparse)

Resume_Dense:
Ce document technique présente les exigences et les bonnes pratiques
relatives à la création et à la configuration de composants extensibles au
sein d'un système d'assistant intelligent. Il décrit les caractéristiques
des fichiers de définition requis, les règles de formatage applicables aux
divers champs et les valeurs autorisées pour chacun d'entre eux. Le
document examine également les différents processus de validation et
d'évaluation de la qualité, les possibilités d'organisation modulaire du
contenu, ainsi que les options d'intégration avec plusieurs environnements
de développement.
```

**Itération 2** (+3 entités, 77 mots) :

```
Entites_Manquantes: "SKILL.md"; "kebab-case"; "allowed-tools"

Resume_Dense:
Les skills sont définis dans un fichier SKILL.md placé dans un
sous-répertoire de .claude/skills/, avec un frontmatter YAML contenant les
métadonnées obligatoires : name en format kebab-case, description incluant
les déclencheurs, et allowed-tools listant les outils autorisés. Le
document présente les règles de formatage applicables aux divers champs,
les processus de validation et d'évaluation de la qualité, les
possibilités d'organisation modulaire du contenu via des sous-répertoires
dédiés, ainsi que les options d'intégration avec plusieurs environnements
de développement.
```

*(itérations 3-4 omises pour la concision — progression graduelle d'entités)*

**Itération 5** (dense, 79 mots) :

```
Entites_Manquantes: "skill-pipeline /150"; "multi-plateformes"

Resume_Dense:
Les skills Claude Code sont définis par un fichier SKILL.md dans
.claude/skills/ avec frontmatter YAML obligatoire : name (kebab-case,
regex ^[a-z0-9]+(-[a-z0-9]+)*$, 1-64 caractères), description (1-1024
caractères, déclencheurs « Utiliser quand... » et mots-clés de
découverte), allowed-tools et context (conversation ou fork). Divulgation
progressive via sous-répertoires references/, assets/, scripts/.
Orchestration de tâches complexes par Agent (sous-agents stateless). Le
pipeline skill-pipeline enchaîne skill-creator, skill-conformity-checker
(/50) et skill-review (/100) pour un score combiné /150. Multi-plateformes :
Claude Code CLI, Cursor, GitHub Copilot.
```

---

## Exemple 2 : format `--historique`

**Commande** : `/chain-of-density catalogue-skills.md --historique --iterations 3 --mots-cibles 100`

**Source** (299 mots) :

> Le workspace Claude propose un catalogue de 34 skills organisés en 7 catégories thématiques. La première catégorie, les outils du quotidien, comprend 5 skills essentiels : /pdf pour la conversion de fichiers Markdown en PDF avec des templates CSS préconfigurés, /prd pour la création et la gestion de documents de spécification produit avec un workflow standardisé, /playbook pour la génération de scripts bash destinés aux tâches d'administration système nécessitant des privilèges élevés, /transfer pour le transfert bidirectionnel de fichiers entre machines via SSH avec rsync ou scp, et /browse pour l'automatisation des interactions avec les navigateurs web. La deuxième catégorie regroupe 9 skills dédiés à l'accessibilité web. Le skill principal /audit-a11y réalise des audits WCAG 2.2 avec axe-core et génère un rapport de conformité détaillé. Le skill /a11y-loop automatise une boucle scan-fix-verify jusqu'à convergence des corrections. Le skill /audit-rgaa cible spécifiquement le référentiel français RGAA 4.1.2 avec ses 106 critères répartis en 13 thématiques, produisant des fiches de non-conformité et un taux de conformité pour le secteur public. La troisième catégorie concerne la qualité des skills eux-mêmes avec /skill-creator pour le guide de création Anthropic, /skill-conformity-checker pour la validation structurelle sur 50, /skill-review pour l'évaluation sémantique sur 100, et /skill-pipeline qui orchestre les trois avec un score combiné sur 150. La quatrième catégorie exploite l'intelligence artificielle multi-modèles : /council orchestre des délibérations entre 16 fournisseurs, /synthese-multi-llm coordonne 4 LLM avec des rôles distincts (Extracteur, Critique, Architecte, Validateur), et /ralph-council combine la technique Ralph Wiggum avec une supervision multi-modèles. Les trois dernières catégories couvrent la rédaction (/humanizer avec 24 détecteurs de patterns IA et /parcoursup optimisé contre GPTZero), les skills spécialisés (/fiches-articles, /decodeur pour la théorie de l'esprit, /nano-rwd pour le responsive, /ocr-pdf-to-word) et les utilitaires (/learn pour analyser l'historique, /checkpoint pour sauvegarder le contexte, /context-refactor pour éliminer les redondances).

**Sortie** :

```yaml
resume_final: |
  Ce workspace propose 34 skills en 7 catégories : quotidien (/pdf
  conversion Markdown-PDF, /prd gestion de spécifications produit,
  /playbook scripts sysadmin, /transfer transfert SSH bidirectionnel,
  /browse automatisation web), accessibilité (9 skills dont /audit-a11y
  via axe-core pour audits WCAG 2.2, /a11y-loop boucle automatisée
  scan-fix-verify, /audit-rgaa référentiel français RGAA 4.1.2 avec 106
  critères en 13 thématiques), qualité (/skill-creator guide Anthropic,
  /skill-conformity-checker /50, /skill-review /100, /skill-pipeline score
  combiné /150), IA multi-modèles (/council 16 fournisseurs en
  délibération, /synthese-multi-llm 4 LLM rôles distincts,
  /ralph-council supervision multi-modèles), rédaction (/humanizer 24
  détecteurs, /parcoursup anti-GPTZero), spécialisés (/fiches-articles,
  /decodeur, /nano-rwd, /ocr-pdf-to-word) et utilitaires (/learn,
  /checkpoint, /context-refactor).
iterations:
  - tour: 1
    entites_manquantes: "(aucune - établissement de la base)"
    mots: 98
    resume: |
      Ce document de référence présente l'ensemble des outils spécialisés
      disponibles dans un espace de travail dédié à l'assistance au
      développement. Ces outils sont organisés en plusieurs catégories
      thématiques couvrant des domaines variés. On y trouve des outils
      destinés aux tâches quotidiennes de gestion de fichiers, des outils
      de vérification de conformité aux normes d'accessibilité web, des
      outils de contrôle qualité des composants, des outils exploitant
      plusieurs modèles d'intelligence artificielle pour produire des
      analyses croisées, des outils de rédaction et de transformation de
      textes, des outils pour des cas d'usage particuliers, ainsi que des
      utilitaires de maintenance du système.
  - tour: 2
    entites_manquantes: "/pdf; /audit-a11y; /council"
    mots: 102
    resume: |
      Ce workspace propose des skills organisés en catégories thématiques.
      Les outils du quotidien incluent /pdf pour la conversion Markdown
      vers PDF avec templates CSS. L'accessibilité web est couverte par une
      suite dédiée dont /audit-a11y qui réalise des audits WCAG 2.2 avec
      axe-core et génère des rapports de conformité détaillés.
      L'intelligence artificielle multi-modèles est exploitée via /council
      qui orchestre des délibérations entre plusieurs fournisseurs pour
      obtenir des perspectives croisées. Le catalogue comprend également
      des outils de contrôle qualité des composants, des outils de
      rédaction et transformation de textes, des skills spécialisés pour
      des cas d'usage particuliers, et des utilitaires de maintenance du
      système.
  - tour: 3
    entites_manquantes: "34 skills; 9 skills accessibilité; /skill-pipeline /150"
    mots: 97
    resume: |
      Ce workspace propose 34 skills en 7 catégories : quotidien (/pdf
      conversion Markdown-PDF, /prd gestion de spécifications produit,
      /playbook scripts sysadmin, /transfer transfert SSH bidirectionnel,
      /browse automatisation web), accessibilité (9 skills dont /audit-a11y
      via axe-core pour audits WCAG 2.2, /a11y-loop boucle automatisée
      scan-fix-verify, /audit-rgaa référentiel français RGAA 4.1.2 avec
      106 critères en 13 thématiques), qualité (/skill-creator guide
      Anthropic, /skill-conformity-checker /50, /skill-review /100,
      /skill-pipeline score combiné /150), IA multi-modèles (/council 16
      fournisseurs en délibération, /synthese-multi-llm 4 LLM rôles
      distincts, /ralph-council supervision multi-modèles), rédaction
      (/humanizer 24 détecteurs, /parcoursup anti-GPTZero), spécialisés
      (/fiches-articles, /decodeur, /nano-rwd, /ocr-pdf-to-word) et
      utilitaires (/learn, /checkpoint, /context-refactor).
total_entites: 6
```

---

## Exemple 3 : cas d'erreur (texte trop court)

**Commande** : `/chain-of-density "L'IA transforme le monde du travail et crée de nouvelles opportunités."`

**Source** : 11 mots

**Sortie** :

```
Texte trop court pour la technique Chain-of-Density (11 mots, minimum 100).
Pour un texte de cette taille, un résumé classique est plus adapté.
```
