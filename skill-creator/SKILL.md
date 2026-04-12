---
name: skill-creator
description: "Guide de creation de skills efficaces. Utiliser quand l'utilisateur veut creer ou mettre a jour un skill Claude (connaissances specialisees, workflows, integrations). Declencheurs : cree un skill, nouveau skill, skill-creator."
license: Complete terms in LICENSE.txt
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
argument-hint: "[nom du skill à créer ou mettre à jour]"
---

# Skill : /skill-creator

Guide de création de skills efficaces pour Claude Code.

## Déclencheurs

- "/skill-creator", "crée un skill", "nouveau skill"
- "aide-moi à créer un skill", "mettre à jour un skill"
- Toute demande de création ou modification d'un skill Claude

## Principes et conception

Pour concevoir un skill efficace, consulter [references/skill-design-guide.md](references/skill-design-guide.md) qui couvre :

- **Nature des skills** — Paquets modulaires étendant Claude avec connaissances spécialisées, workflows et outils
- **Concision** — La fenêtre de contexte est un bien commun ; n'ajouter que ce que Claude ne sait pas
- **Degrés de liberté** — Adapter la spécificité à la fragilité de la tâche
- **Anatomie** — Structure SKILL.md + ressources (`scripts/`, `references/`, `assets/`)
- **Divulgation progressive** — Système de chargement à 3 niveaux (métadonnées, corps, ressources)

Règle clé : ne PAS créer de fichiers auxiliaires superflus (README.md, CHANGELOG.md, etc.). Maintenir le SKILL.md sous 500 lignes et externaliser en références si nécessaire.

## Variables disponibles

- `$ARGUMENTS` — Texte passé après le nom du skill (ex : `/skill-creator mon-skill` → `$ARGUMENTS` = `mon-skill`). Correspond au champ `argument-hint` du frontmatter.

## Processus de création d'un skill

La création d'un skill suit ces étapes :

1. Comprendre le skill avec des exemples concrets
2. Planifier les contenus réutilisables (scripts, références, assets)
3. Initialiser le skill (exécuter init_skill.py)
4. Éditer le skill (implémenter les ressources et écrire le SKILL.md)
5. Packager le skill (exécuter package_skill.py)
6. Itérer en fonction de l'usage réel

Suivre ces étapes dans l'ordre, ne sauter que s'il y a une raison claire pour laquelle elles ne s'appliquent pas.

### Étape 1 : Comprendre le skill avec des exemples concrets

Si `$ARGUMENTS` est fourni (voir section Variables disponibles), l'utiliser comme nom du skill cible. Sinon, demander à l'utilisateur quel skill il souhaite créer ou mettre à jour.

Sauter cette étape uniquement quand les patterns d'utilisation du skill sont déjà clairement compris. Elle reste utile même pour un skill existant.

Pour créer un skill efficace, comprendre clairement des exemples concrets d'utilisation. Cette compréhension peut venir d'exemples directs de l'utilisateur ou d'exemples générés validés par retour utilisateur.

Par exemple, pour un skill image-editor, les questions pertinentes incluent :

- « Quelles fonctionnalités le skill image-editor doit-il supporter ? Édition, rotation, autre chose ? »
- « Pouvez-vous donner des exemples d'utilisation de ce skill ? »
- « J'imagine des utilisateurs demandant « Supprime les yeux rouges de cette image » ou « Tourne cette image ». Y a-t-il d'autres usages que vous imaginez ? »
- « Que dirait un utilisateur pour déclencher ce skill ? »

Pour ne pas submerger l'utilisateur, éviter de poser trop de questions en un seul message. Commencer par les questions les plus importantes et compléter selon les besoins.

Conclure cette étape quand le périmètre fonctionnel du skill est clair.

### Étape 2 : Planifier les contenus réutilisables

Pour transformer les exemples concrets en un skill efficace, analyser chaque exemple en :

1. Considérant comment exécuter l'exemple depuis zéro
2. Identifiant quels scripts, références et assets seraient utiles pour des exécutions répétées

Exemple : Pour un skill `pdf-editor` traitant des requêtes comme « Aide-moi à tourner ce PDF », l'analyse montre :

1. La rotation d'un PDF nécessite de réécrire le même code à chaque fois
2. Un script `scripts/rotate_pdf.py` serait utile à stocker dans le skill

Exemple : Pour un skill `frontend-webapp-builder` traitant des requêtes comme « Construis-moi une app todo » ou « Construis-moi un tableau de bord pour suivre mes pas », l'analyse montre :

1. Écrire une webapp frontend nécessite le même boilerplate HTML/React à chaque fois
2. Un template `assets/hello-world/` contenant les fichiers boilerplate serait utile

Exemple : Pour un skill `big-query` traitant des requêtes comme « Combien d'utilisateurs se sont connectés aujourd'hui ? », l'analyse montre :

1. Interroger BigQuery nécessite de redécouvrir les schémas et relations de tables à chaque fois
2. Un fichier `references/schema.md` documentant les schémas serait utile

Analyser chaque exemple concret pour établir la liste des ressources réutilisables à inclure.

### Étape 3 : Initialiser le skill

À ce stade, il est temps de créer le skill.

Sauter cette étape uniquement si le skill en cours de développement existe déjà et qu'une itération ou un packaging est nécessaire.

Pour créer un nouveau skill depuis zéro, toujours exécuter le script `init_skill.py`. Le script génère un répertoire template qui inclut automatiquement tout ce qu'un skill nécessite.

Utilisation :

```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

Le script :

- Crée le répertoire du skill au chemin spécifié
- Génère un template SKILL.md avec le frontmatter et des placeholders TODO
- Crée les répertoires de ressources : `scripts/`, `references/` et `assets/`
- Ajoute des fichiers exemples dans chaque répertoire

Après l'initialisation, personnaliser ou supprimer les fichiers générés selon les besoins.

### Étape 4 : Éditer le skill

Lors de l'édition du skill, se rappeler qu'il est créé pour qu'une autre instance de Claude l'utilise. Inclure les informations bénéfiques et non évidentes pour Claude. Considérer quelles connaissances procédurales, détails spécifiques au domaine ou assets réutilisables aideraient une autre instance de Claude.

#### Consulter les patterns de conception éprouvés

Consulter ces guides selon les besoins du skill :

- **Processus multi-étapes** : Voir references/workflows.md pour les workflows séquentiels et la logique conditionnelle
- **Formats de sortie ou standards de qualité** : Voir references/output-patterns.md pour les patterns de templates et exemples

Ces fichiers contiennent les bonnes pratiques établies pour la conception de skills.

#### Commencer par les contenus réutilisables

Pour démarrer l'implémentation, commencer par les ressources réutilisables identifiées : fichiers `scripts/`, `references/` et `assets/`. Cette étape peut nécessiter une contribution de l'utilisateur (par exemple, fournir des assets de marque ou des templates).

Les scripts ajoutés doivent être testés en les exécutant réellement. Si les scripts sont nombreux et similaires, un échantillon représentatif suffit.

Les fichiers et répertoires exemples non nécessaires doivent être supprimés.

#### Mettre à jour le SKILL.md

**Directives de rédaction :** Toujours utiliser la forme impérative/infinitive.

##### Section anti-rationalisations (obligatoire pour les skills de discipline)

Si le skill impose un processus que l'agent pourrait vouloir contourner (revue, vérification, audit, commit), ajouter une section avec :

1. **Seuil de déclenchement** : quand le skill s'applique / ne s'applique pas
2. **Excuses interdites** : 3-5 rationalisations courantes, nommées et rejetées
3. **Checklist bloquante** : transformer les "- [ ] Vérifier X" en "AVANT de conclure, VÉRIFIER X. Si NON, STOP"

Ne PAS ajouter cette section aux skills mécaniques (conversion, transfert, pipeline déterministe).

Référence : `~/.claude/skills/skill-review/references/pressure-scenarios.md` pour les 5 scénarios de pression types.

##### Frontmatter

Rédiger le frontmatter YAML avec `name` et `description` :

- `name` : Le nom du skill
- `description` : Mécanisme principal de déclenchement du skill. Aide Claude à comprendre quand l'utiliser.
  - Inclure à la fois ce que fait le skill et les déclencheurs/contextes spécifiques.
  - Inclure toutes les informations « quand utiliser » ici — pas dans le corps. Le corps n'est chargé qu'après le déclenchement, donc les sections « Quand utiliser ce skill » dans le corps ne sont pas utiles à Claude.
  - Exemple de description pour un skill `docx` : « Création, édition et analyse de documents avec support du suivi de modifications, commentaires, préservation du formatage et extraction de texte. Utiliser quand Claude doit travailler avec des documents professionnels (.docx). »

### Étape 5 : Packager un skill

Une fois le développement terminé, le skill doit être packagé en un fichier .skill distribuable. Le processus de packaging valide automatiquement le skill d'abord :

```bash
scripts/package_skill.py <path/to/skill-folder>
```

Spécification optionnelle du répertoire de sortie :

```bash
scripts/package_skill.py <path/to/skill-folder> ./dist
```

Le script de packaging :

1. **Valide** le skill automatiquement, vérifiant :

   - Format du frontmatter YAML et champs obligatoires
   - Conventions de nommage et structure du répertoire
   - Complétude et qualité de la description
   - Organisation des fichiers et références aux ressources

2. **Package** le skill si la validation passe, créant un fichier .skill nommé d'après le skill (ex: `my-skill.skill`) qui inclut tous les fichiers et maintient la structure de répertoire. Le fichier .skill est un zip avec extension .skill.

Si la validation échoue, le script signale les erreurs et s'arrête sans créer de package. Corriger les erreurs et relancer la commande.

### Étape 6 : Itérer

Après avoir testé le skill, l'utilisateur peut demander des améliorations. Cela arrive souvent juste après l'utilisation, avec le contexte frais de la performance du skill.

**Workflow d'itération :**

1. Utiliser le skill sur des tâches réelles
2. Repérer les difficultés ou inefficacités
3. Identifier comment le SKILL.md ou les ressources embarquées doivent être mis à jour
4. Implémenter les changements et tester à nouveau

## Gestion des erreurs

| Scénario | Comportement |
|----------|-------------|
| Script `init_skill.py` introuvable | Signaler l'erreur et indiquer le chemin attendu (`scripts/init_skill.py`) |
| Nom de skill invalide (espaces, majuscules) | Proposer la version kebab-case et demander confirmation |
| Répertoire de destination inexistant | Créer le répertoire parent ou demander le bon chemin |
| Skill déjà existant au même chemin | Demander confirmation avant d'écraser ou proposer un autre nom |
| Validation du packaging échoue | Afficher les erreurs et proposer les corrections |

## Contraintes

- TOUJOURS exécuter `init_skill.py` pour créer un nouveau skill (pas de création manuelle)
- TOUJOURS tester les scripts ajoutés en les exécutant réellement
- TOUJOURS inclure les informations « quand utiliser » dans la description, pas dans le corps
- JAMAIS créer de fichiers auxiliaires superflus (README.md, CHANGELOG.md, etc.)
- JAMAIS dépasser 500 lignes dans le SKILL.md (découper en références)
- JAMAIS dupliquer l'information entre le SKILL.md et les fichiers de références
- TOUJOURS inclure une section anti-rationalisations dans les skills de discipline (revue, vérification, audit, commit). Voir étape 4 "Section anti-rationalisations"

## Exemples d'utilisation

```text
Utilisateur : /skill-creator pdf-processor

Claude :
> Étape 1 : Quel périmètre fonctionnel pour le skill pdf-processor ?
>   - Extraction de texte, rotation, fusion, formulaires ?
> Étape 2 : Ressources identifiées :
>   - scripts/rotate_pdf.py, scripts/merge_pdf.py
>   - references/api_pdfplumber.md
> Étape 3 : Initialisation...
>   scripts/init_skill.py pdf-processor --path .claude/skills/pdf-processor
> Étape 4 : Implémentation des scripts et rédaction du SKILL.md
> Étape 5 : Packaging...
>   scripts/package_skill.py .claude/skills/pdf-processor
```

```text
Utilisateur : mets à jour le skill /transfer pour ajouter le support rsync

Claude :
> Skill existant détecté : .claude/skills/transfer/SKILL.md
> Étapes 1-2 : Analyse de l'ajout rsync...
> Étape 4 : Mise à jour du SKILL.md et ajout du workflow rsync
> Test de la commande rsync...
> Skill mis à jour avec succès.
```

```text
Utilisateur : /skill-creator Mon Super Skill!

Claude :
> Nom invalide détecté : "Mon Super Skill!" contient des espaces et
> des caractères spéciaux.
> Proposition : mon-super-skill (kebab-case)
> Confirmez-vous ce nom ?
```

## Checklist finale

- [ ] Exemples concrets d'utilisation compris (étape 1)
- [ ] Ressources réutilisables identifiées et implémentées (étape 2)
- [ ] Skill initialisé via `init_skill.py` (étape 3, si nouveau)
- [ ] SKILL.md rédigé avec frontmatter complet (étape 4)
- [ ] Scripts testés et fonctionnels (étape 4)
- [ ] Skill sous 500 lignes, références externalisées si nécessaire
- [ ] Aucun fichier auxiliaire superflu (README.md, etc.)
