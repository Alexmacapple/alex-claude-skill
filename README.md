# Skills Claude Code — Alex

Collection de 11 skills personnels pour Claude Code. Chaque skill est un workflow structuré invocable par slash command.

## Installation

Copier le dossier du skill souhaité dans `.claude/skills/` de votre projet ou de votre répertoire personnel `~/.claude/skills/` :

```bash
# Un seul skill
cp -r avocat-du-diable ~/.claude/skills/

# Tous les skills
cp -r */ ~/.claude/skills/
```

Redémarrer la session Claude Code pour que les skills soient détectés.

## Les skills

### /avocat-du-diable — Revue critique structurée

Revue critique qui force le steel-man avant la critique, applique des cadres de questionnement (pré-mortem, inversion, socratique), et rend un verdict actionnable (Livrer / Livrer avec modifications / Repenser).

```
/avocat-du-diable — révise le plan de migration dans infra/postgres-upgrade.md
```

**3 fichiers de référence** : cadres de questionnement (Klein, Munger, de Bono), angles morts ingénierie (11 catégories), angles morts IA (12 schémas de défaillance).

---

### /chain-of-density — Densification itérative de résumés

Compresse un texte par injection itérative d'entités manquantes selon la méthode Chain-of-Density (arXiv 2309.04269). Chaque passe identifie les entités absentes de la source et les incorpore en maintenant un nombre de mots identique.

```
/chain-of-density document.md
/chain-of-density document.md --iterations 5 --mots-cibles 80
```

Inclut un script `text_metrics.py` pour mesurer la densité informationnelle et les références complètes du papier.

---

### /connu-inconnu — Matrice de Rumsfeld

Cartographie les certitudes, incertitudes, biais et angles morts d'un projet selon les 4 quadrants : Ancrage (connus connus), Brouillard (connus inconnus), Déni (inconnus connus), Abîme (inconnus inconnus).

```
/connu-inconnu — Créer un portail de demande de titre de séjour
```

Verdict : Prêt / Prêt sous conditions / Pas prêt.

---

### /gherkin — Spécification comportementale

Cristallise des comportements métier en scénarios Gherkin structurés en français. Le LLM EST le processus de spécification comportementale.

```
/gherkin — spécifie le parcours d'inscription utilisateur
```

---

### /humanizer — Humanisation de texte IA

Humanise du texte généré par IA pour le rendre indétectable par 24 détecteurs (GPTZero, ZeroGPT, etc.). Analyse statistique, remplacement de 500+ termes, scoring de détection.

```
/humanizer — humanise ce paragraphe
```

---

### /meta-prompt-concept — Prompts incarnés

Génère des prompts où le LLM EST le concept plutôt qu'un expert DU concept. « Tu es un expert en X » produit du générique. « Tu ES X » produit du structurel.

```
/meta-prompt-concept — incarne le concept de dette technique
```

---

### /prd — Création et gestion de PRD

Crée et gère des Product Requirements Documents avec workflow standardisé : numérotation automatique, template structuré (vision, problème, solution, options, décision, plan, métriques, risques), validation croisée optionnelle (connu-inconnu + avocat-du-diable), backlog centralisé.

```
/prd "système de notifications push"
/prd --list
```

---

### /pedagogie-neuro — Neuropédagogie pour slides

Applique 26 règles de neuropédagogie pour concevoir ou améliorer un contenu pédagogique. Transforme un contenu informatif en expérience d'apprentissage ancrée.

```
/pedagogie-neuro — améliore ces slides de formation
```

---

### /prompt-image — Raffinement de prompts image

Pipeline de raffinement progressif pour prompts de génération d'image. Transforme une idée brute en prompt optimisé, contraint par un style guide et adapté au générateur cible.

```
/prompt-image — un paysage de montagne enneigé au coucher du soleil
```

---

### /lexique-precis — Exploration lexicale pour prompts IA

Transforme un mot vague en palette de graines sémantiques multilingues. 3 mouvements : cartographie des registres (courant, soutenu, technique, étranger, savant), pépites rares, graines de prompts actionnables. Chaque terme est classé `[attesté]` ou `[construction proposée]`.

```
/lexique-precis "analyser"
/lexique-precis "prendre de la hauteur"
```

Dictionnaires archivés dans `dictionnaires/` pour calibrer les futures explorations (boucle cumulative).

---

### /raisonnement-code — Revue de code semi-formelle

Revue de code basée sur le papier Meta « Agentic Code Reasoning » (arXiv 2603.01896v2, 2026). 3 modes : patch (vérification de correctif), bug (localisation de cause racine), qa (question sur le comportement du code). Chaque affirmation cite `fichier:ligne`.

```
/raisonnement-code patch — vérifie le diff de auth.py
/raisonnement-code bug — test_export échoue avec KeyError
/raisonnement-code qa — est-ce que delete_user supprime les fichiers S3 ?
```

**3 templates de référence** alignés sur les appendices A, B et D du papier : prémisses numérotées, claims formels, format d'exploration agentic.

---

## Architecture

Chaque skill suit la même structure :

```
nom-du-skill/
├── SKILL.md              # Le skill (frontmatter YAML + instructions)
└── references/           # Fichiers de référence chargés à la demande
    ├── template-*.md
    └── ...
```

Le `SKILL.md` contient le frontmatter (name, description, triggers, allowed-tools) et les instructions. Les fichiers dans `references/` sont chargés via `Read` pendant l'exécution — pas au démarrage.

## Conventions

- Langue : français (accents obligatoires)
- Nommage : kebab-case
- Concept incarné : chaque skill commence par « Tu ES... » pas « Tu es un expert en... »
- Garde-fous : règles JAMAIS/TOUJOURS pour encadrer le comportement du LLM
- Checklist finale : points de vérification en fin de skill

## Licence

Usage personnel. Ces skills sont conçus pour le workflow d'Alex et peuvent nécessiter une adaptation pour d'autres contextes.

---

*Auteur : Alex — avril 2026*
