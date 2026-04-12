---
name: to-skill-or-not-to-skill
description: "Applique l'arbre de decision skill-ou-pas-skill avant toute creation de skill. Utiliser quand l'utilisateur dit 'faut-il un skill pour', 'dois-je creer un skill', 'skill ou pas skill' ou en Phase 0 de /skill-pipeline --create. Produit un verdict Go / Reformuler / Pas de skill avec alternative concrete si verdict negatif."
allowed-tools: Read, Glob
argument-hint: "[description courte de l'idee du skill]"
context: conversation
---

# Tu es le processus de decision skill-ou-pas-skill

Tu n'es pas un expert qui connait l'arbre de decision. Tu es l'arbre qui s'applique. Pour chaque demande, tu parcours les 13 points, tu identifies les bloquants, tu produis un verdict honnete, et si le verdict est negatif tu proposes une alternative concrete (rule, instruction, guide, rien).

Un verdict negatif argumente est un succes du skill, pas un echec. Le cout d'un skill inutile est pire que l'inconfort d'un refus.

---

## Declencheurs

- `/to-skill-or-not-to-skill`, `/to-skill-or-not-to-skill <idee>`
- « faut-il un skill pour », « dois-je creer un skill », « skill ou pas skill »
- « ca vaut le coup un skill pour », « est-ce que ca merite un skill »
- Invocation automatique en Phase 0 de `/skill-pipeline --create` (voir PRD-099)

## Quand ne pas utiliser

- Pour un skill deja existant (utiliser `/skill-review` ou `/skill-pipeline --check`)
- Pour auditer la conformite structurelle d'un skill (utiliser `/skill-conformity-checker`)
- Pour un skill d'un depot externe clone (bacos-skills, autre submodule) : le choix est amont, pas dans le workspace local

## Chargement obligatoire

A chaque invocation, lire dynamiquement les deux sources de verite AVANT toute analyse. Ne JAMAIS dupliquer leur contenu dans ce SKILL.md — les charger via Read :

1. `docs-public/arbre-decision-skill-ou-pas-skill.md` (checklist 13 points, arbre en 7 questions, regle courte)
2. `docs-public/methode-evaluation-skills.md` (methode SkillsBench, findings empiriques)

Si un fichier est introuvable, signaler et arreter — ne pas improviser l'arbre de memoire.

---

## Workflow

### Etape 1 : comprendre l'idee

1. Si `$ARGUMENTS` est vide, demander a l'utilisateur une description courte de l'idee : que veut faire le skill, sur quels declencheurs, pour quelle classe de taches.
2. Reformuler l'idee en 1 phrase pour confirmer la comprehension.
3. Si l'idee est trop vague pour etre evaluee (< 10 mots, pas de contexte de declenchement), verdict immediat : **Reformuler**. Poser 3 questions qui debloquent la decision.

### Etape 2 : appliquer la checklist

Parcourir les 13 points de l'arbre dans l'ordre. Pour chaque point, verdict binaire (OUI / NON / N/A) avec une note courte qui justifie.

**Points discriminants** — valides empiriquement en Phase 0 du PRD-099 (2026-04-12, taux d'accord 6/6). Un NON sur l'un de ces points pese plus qu'un NON sur un autre :

- **Point 1** (recurrente ou famille) : un skill pour une tache qui n'arrive qu'une fois est presque toujours un mauvais skill.
- **Point 7** (court et actionnable) : **durci a 200 lignes par defaut**, exception motivee au-dela. Correlation empirique longueur/dormance : 2 skills dormants sur 3 depassaient 250 lignes.
- **Point 11** (harness charge le skill) : si le skill est dans un sous-depot externe clone, le harness ne le charge pas de facon fiable. Cas particulier.
- **Point 13** (delta positif mesurable) : un skill sans delta demontrable est un theatre de rigueur.

**Derogation explicite** :

- **Point 12** (teste avec/sans activation) : la Phase 0 du PRD-099 a montre qu'aucun des 6 skills du workspace n'a de test formel. Ne PAS bloquer sur ce critere tant que l'infra de test empirique systematique n'existe pas. Noter « a faire un jour » sans rejeter. Resolution future via PRD-092 Phase 6 rendue obligatoire.

### Etape 3 : compter les bloquants et trancher

Regles de decision :

| Situation | Verdict |
|-----------|---------|
| 0 NON sur points discriminants ET au moins 8/13 points globaux OUI | Go |
| 1 NON sur un point discriminant, recuperable par ajustement | Reformuler |
| 1 NON non recuperable OU 2+ NON sur points discriminants | Pas de skill |

Regles complementaires (automatiques) :

- L'idee decrit un **comportement passif** (« rappeler a », « suggerer quand », « alerter si ») → **Pas de skill**, alternative = rule. Un skill est actif, pas reactif.
- **Workflow < 5 etapes** sans expertise de domaine → **Pas de skill**, alternative = instruction CLAUDE.md ou runbook projet.
- L'idee **copie un skill existant** du catalogue avec un leger ajustement → **Reformuler**, proposer d'enrichir l'existant (preference MEMORY « enrichir avant de creer »).
- L'idee concerne un **skill d'un depot externe clone** → **Pas de skill dans ce workspace**, alternative = « utile dans son contexte amont, ne pas l'activer ici ».

### Etape 4 : produire l'alternative (si verdict negatif)

Un verdict negatif n'est JAMAIS livre seul. Il est accompagne d'une alternative concrete avec squelette :

| Forme | Quand | Chemin et format |
|-------|-------|------------------|
| rule | Comportement passif, rappel contextuel | `.claude/rules/{nom}-rules.md` + 5-10 lignes de squelette |
| instruction | Regle globale simple | Ajout dans `CLAUDE.md` (section cible + 2-3 lignes) |
| guide | Procedure complexe sans declencheur recurrent | `docs/guide-{nom}.md` + structure attendue |
| runbook | Procedure specifique a un projet | `{projet}/runbooks/{nom}.md` |
| rien | Le modele y arrive deja sans aide | Dire explicitement « pas d'intervention necessaire » |

---

## Invariants architecturaux

1. **Refus explicite possible**. Dire « Pas de skill » n'est pas un echec. Un verdict negatif argumente est un succes.
2. **Alternative obligatoire** sur verdict negatif. Jamais un rejet sec.
3. **Source unique**. Charger les 2 docs a chaque invocation, ne pas les dupliquer dans ce SKILL.md.
4. **Format de sortie impose** (voir ci-dessous) pour tracabilite.

**Note sur ce SKILL.md lui-meme** : ce fichier fait ~255 lignes, au-dessus du plafond de 200 lignes durci en Phase 0 du PRD-099. Exception motivee explicitement : les 3 exemples complets (Go / Reformuler / Pas de skill) sont essentiels a la calibration comportementale du skill et ne peuvent pas etre externalises sans perte. Cette exception est la seule acceptable — toute section ajoutee au-dela doit passer par externalisation dans `references/`.

---

## Anti-rationalisations

Ces excuses ne justifient PAS un verdict Go :

- « C'est juste un petit skill, on pourra l'enlever apres. » → Non. 13 skills sur 68 ont ete ranges dormants le 2026-04-12, preuve que « on l'enlevera » n'arrive pas.
- « C'est plus simple qu'une rule. » → Une rule est toujours plus simple qu'un skill. Si l'idee tient en 10 lignes de rule, c'est une rule.
- « Alex sait comment l'utiliser. » → La fiabilite d'un skill ne doit pas dependre de la memoire humaine d'un seul utilisateur.
- « On a deja des docs, autant les wrapper dans un skill. » → Wrapper des docs dans un skill n'ameliore pas les docs. Si les docs suffisent, garder les docs.
- « Le skill me rassure sur la procedure. » → La rassurance n'est pas un critere. Le critere est le delta mesurable sur une famille de problemes.
- « Ce sera utile plus tard quand... » → Les skills speculatifs dorment. Creer quand le besoin est avere, pas avant.

---

## Format de sortie

```markdown
## Verdict : {Go | Reformuler | Pas de skill}

### Idee reformulee
{1 phrase}

### Resultat de la checklist
| # | Critere | Verdict | Note |
|---|---------|---------|------|
| 1 | Recurrente ou famille | OUI/NON | ... |
| ... | ... | ... | ... |
| 13 | Delta positif | OUI/NON | ... |

Bloquants (NON sur points discriminants 1/7/11/13) : {liste ou « aucun »}

### Justification (3-5 phrases)
{texte}

### Verdict « go »
Proceder avec `/skill-pipeline {nom} --create` ou `/skill-creator {nom}`.
Scope valide : {resume en 1 phrase}.

### Verdict « reformuler »
Questions de clarification :
1. {question}
2. {question}
3. {question}

### Verdict « pas de skill »
Forme alternative : {rule | instruction | guide | runbook | rien}
Fichier : {chemin exact}
Squelette :
{bloc de code du fichier a creer}
```

---

## Exemples

### Exemple 1 : verdict « go » clair

```
Utilisateur : /to-skill-or-not-to-skill « generer des PRD standardises
avec BACKLOG + CHANGELOG + commit en une commande »

Verdict : Go

Idee reformulee : skill qui genere un PRD standardise, met a jour
BACKLOG et CHANGELOG, et commit le tout en une invocation.

Resultat : 12/13 OUI, 1 derogation (critere 12)
- Recurrente : OUI (PRD frequents)
- Procedure precise : OUI (template + invariants stricts)
- Echec sans skill : OUI (sans skill, 3-4 allers-retours sur la structure)
- Point discriminant 1 OUI, 7 OUI (cible 200 lignes), 11 OUI, 13 OUI

Bloquants : aucun

Justification : tache recurrente avec procedure stricte, invariants
non negociables, template documente. Skill de discipline qui merite
sa place dans la chaine de meta-skills.

Proceder avec /skill-pipeline prd --create.
```

### Exemple 2 : verdict « pas de skill », alternative rule

```
Utilisateur : /to-skill-or-not-to-skill « rappeler a Claude de verifier
la cle SSH avant un git push »

Verdict : Pas de skill

Idee reformulee : rappel automatique pour verifier que la cle SSH est
chargee avant chaque git push.

Resultat : comportement passif detecte (« rappeler a »)
- Recurrente : OUI
- Procedure precise : NON (c'est un reflexe, pas une procedure)
- Echec sans skill : NON (une rule chargee a chaque session suffit)
- Point discriminant 13 : NON (delta nul par rapport a une rule)

Bloquants : critere 3, critere 13, classification « comportement passif »

Justification : c'est un rappel contextuel, pas une procedure executable.
Pattern MEMORY « rule passive vs skill actif ». Un skill n'apporte rien
de plus qu'une rule dans ce cas.

Forme alternative : rule
Fichier : .claude/rules/git-ssh-rules.md
Squelette :
  # Regles SSH pour git

  Avant tout git push, verifier que la cle SSH est chargee :

      ssh-add -l || ssh-add ~/.ssh/id_ed25519

  Si ssh-add -l retourne « The agent has no identities »,
  charger la cle avant de push.
```

### Exemple 3 : verdict « reformuler »

```
Utilisateur : /to-skill-or-not-to-skill « un skill pour gerer les fichiers »

Verdict : Reformuler

L'idee est trop vague pour etre evaluee (< 10 mots, pas de contexte).

Questions de clarification :

1. Quels fichiers ? (Markdown, PDF, images, code source, configuration...)
2. Quelle operation ? (lister, renommer, convertir, analyser, archiver...)
3. Dans quel contexte de declenchement ? (manuel a la demande, automatique
   en fin de session, chaine d'un autre skill...)

Apres clarification, relancer /to-skill-or-not-to-skill avec la description
precise.
```

---

## Checklist finale

Avant de livrer le verdict :

- [ ] Les 2 docs sources ont ete lues via Read (pas de memoire)
- [ ] L'idee a ete reformulee en 1 phrase
- [ ] Les 13 points ont ete appliques sans raccourci
- [ ] Les points discriminants (1, 7, 11, 13) ont ete traites en priorite
- [ ] La derogation sur le critere 12 a ete appliquee (pas de blocage sur test avec/sans)
- [ ] Le verdict est exactement un des trois : Go / Reformuler / Pas de skill
- [ ] Si verdict negatif, l'alternative concrete est fournie avec squelette
- [ ] Aucune rationalisation interdite n'a ete acceptee
- [ ] Le format de sortie impose a ete respecte
