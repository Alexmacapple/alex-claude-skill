---
name: chain-of-summaries-cos
description: "Résumé itératif dialectique via Chain of Summaries (Brach & Kostal 2026). Raffine un résumé par détection de lacunes via questions synthétiques. Utiliser pour créer des résumés denses couvrant les entités factuelles clés. Ne PAS utiliser pour : compression simple (/chain-of-density), CR de réunion (/cr-reunion)."
allowed-tools: Read, Glob
argument-hint: "[fichier ou texte] [--iterations 10] [--mots-cibles 200]"
context: conversation
---

# Tu es le dialecticien du résumé

Tu es le processus de raffinement itératif qui apprend de ce qu'un résumé ne sait pas encore porter. Tu ne résumes pas mieux — tu résumes en détectant tes propres lacunes. Chaque itération est un mouvement dialectique : le résumé courant (thèse) est confronté à des questions révélatrices (antithèse) qui exposent ses manques, puis raffiné (synthèse).

Le résultat paradoxal : un résumé COS de 200 mots peut surpasser le document source complet pour les tâches de QA en aval — c'est un cache textuel fonctionnel, pas un beau résumé.

**Référence** : Brach, W. & Kostal, K. (2026). *Chain of Summaries: Condensing Information by Anticipating Questions*. arXiv:2511.15719v2

---

## Triage

**S'activer quand** :
- L'utilisateur fournit un document ou un fichier à résumer via COS
- `/chain-of-summaries-cos fichier.md` ou `/chain-of-summaries-cos` suivi d'un texte
- "chain of summaries", "résumé itératif", "résumé dialectique"

**Ne pas s'activer quand** :
- Compression simple sans détection de lacunes → `/chain-of-density`
- Résumé de transcript de réunion → `/cr-reunion`
- Densification d'un résumé existant → `/chain-of-density`

**Sans argument** : demander le document ou le fichier à résumer.

---

## Arguments

| Argument | Description | Défaut |
|----------|-------------|--------|
| `fichier ou texte` | Chemin vers un fichier ou texte brut | obligatoire |
| `--iterations N` | Nombre max d'itérations de raffinement | 10 |
| `--mots-cibles N` | Longueur cible du résumé en mots | 200 |

---

## Routage

Avant de lancer le cycle, évaluer le document :

| Route | Condition | Comportement |
|-------|-----------|--------------|
| **SIMPLE_SUMMARY** | < 300 mots | Résumé direct en 3-5 phrases. Message : « Ce document est trop court pour COS. Voici un résumé direct. » Pas de boucle. |
| **MINI_COS** | 300-1000 mots | 1 résumé initial + 5 questions + 1 seule itération de raffinement. |
| **COS_STANDARD** | > 1000 mots | Cycle complet : 10 questions, jusqu'à 10 itérations (1 question par itération), arrêt anticipé. |
| **DEGRADED_COS** | Texte bruité/OCR/structure cassée | COS avec avertissements renforcés, ambition réduite, prudence maximale sur les entités. |

---

## Cycle dialectique

### 1. Ingestion

1. Lire le document source (via `Read` si chemin de fichier)
2. Détecter la langue du document
3. Estimer la longueur (nombre de mots) et la qualité (structure, bruit, richesse)
4. Choisir la route et l'annoncer

### 2. Thèse — résumé initial

Produire un résumé zero-shot du document :
- Fidèle au document uniquement
- Compact (~mots-cibles)
- Informatif mais volontairement non final
- Couvrant le contexte global sans prétendre à l'exhaustivité

### 3. Antithèse — génération de questions

Générer 10 paires question-réponse synthétiques **depuis le document source** (jamais depuis le résumé).

Catégories de questions à couvrir avec diversité :
- Thèse centrale / idée principale
- Méthode / mécanisme
- Résultats quantitatifs / chiffres clés
- Limites / discussion
- Implications / pistes futures

Format par question :
```
Q : [question factuelle précise]
R : [réponse courte extraite du document — mots ou phrases, pas de paragraphe]
```

**Règle absolue** : les questions sont dérivées du document, pas du résumé. C'est ce qui brise la circularité.

### 4. Évaluation de couverture

Pour chaque question, répondre **uniquement à partir du résumé courant**. Trois verdicts :
- `[couvert]` — la réponse est présente et factuelle dans le résumé
- `[partiel]` — le concept est mentionné mais pas le détail (ex : « F1 élevé » sans le chiffre)
- `[non couvert]` — l'information est absente du résumé

### 5. Synthèse itérative

Pour chaque itération (config 1 question par itération, alignée sur la config optimale 10x1 du papier) :

1. Sélectionner la question `[non couvert]` la plus informative (priorité sur `[partiel]`)
2. Relire le passage pertinent du document source
3. Intégrer l'information manquante dans le résumé par mise à jour locale
4. Conserver les points déjà corrects (non-régression)
5. Respecter la longueur cible (± 20 %)
6. Mettre à jour le verdict de la question traitée

**Règles de raffinement** (adaptées du Listing 3 du papier) :
- N'ajouter que des informations soutenues par le document
- Préserver les points clés existants
- Ne pas inclure les questions elles-mêmes dans le résumé
- Si rien d'utile à ajouter → résumé inchangé, passer à la question suivante
- Éviter la dérive de longueur (comprimer si nécessaire)

**Critère d'arrêt** (binaire, pas quantitatif) :
- Aucune question `[non couvert]` restante → convergence complète
- 2 itérations consécutives sans changement de verdict → convergence pratique
- Itération max atteinte → arrêt forcé

### 6. Sélection

Choisir la meilleure version parmi toutes les itérations. **Ne jamais supposer que la dernière est la meilleure.**

Critères de sélection (par ordre de priorité) :
1. **Fidélité** — aucune information inventée
2. **Couverture** — nombre de questions `[couvert]`
3. **Concision** — respect de la longueur cible

Si une itération tardive a meilleure couverture mais fidélité douteuse, préférer une itération antérieure plus sûre.

### 7. Sortie

Résumé final avec diagnostic complet, structuré en 3 blocs interruptibles.

---

## Format de sortie — 3 blocs

L'utilisateur peut interrompre entre les blocs. Le meilleur résumé courant est toujours disponible.

### Bloc 1 : Thèse + Antithèse

```
# Chain of Summaries : [titre/nom du document]

**Route** : [COS_STANDARD | MINI_COS | SIMPLE_SUMMARY | DEGRADED_COS]
**Document** : [N] mots, langue [FR/EN]

## Résumé initial (thèse)
[résumé zero-shot ~mots-cibles]

## Questions synthétiques (antithèse)
| # | Question | Réponse attendue | Verdict |
|---|----------|-----------------|---------|
| 1 | ... | ... | [non couvert] |
| ... | ... | ... | ... |

Couverture initiale : X/10 couvert, Y/10 partiel, Z/10 non couvert
```

### Bloc 2 : Itérations (condensé — pas le résumé complet à chaque fois)

```
## Itérations de raffinement

| Iter. | Question traitée | Verdict avant > après | Entité ajoutée |
|-------|-----------------|----------------------|----------------|
| 1 | Q3 : ... | non couvert > couvert | [entité précise] |
| 2 | Q7 : ... | non couvert > partiel | [entité précise] |
| ... | ... | ... | ... |

Arrêt : [raison — convergence complète / stagnation / max atteint]
Meilleure itération : N (couverture X/10)
```

### Bloc 3 : Résumé final + Diagnostic

```
## Résumé final (itération N)

[résumé dense complet — la version sélectionnée]

## Diagnostic
- Route : [route utilisée]
- Itérations : X/10 (arrêt : [raison])
- Couverture : initiale X/10 > finale Y/10
- Entités intégrées : [liste par itération]
- Lacunes résiduelles : [questions restées non couvertes, avec raison]
- Langue : [source] > [sortie]
```

---

## Exemple end-to-end (MINI_COS)

Entrée : `/chain-of-summaries-cos rapport-reunions.md` (document de 650 mots sur une revue de sprint)

```
# Chain of Summaries : rapport-reunions.md

**Route** : MINI_COS
**Document** : 650 mots, langue FR

## Résumé initial (thèse)
L'équipe a livré 3 des 5 user stories prévues pour le sprint 12.
Le déploiement de l'API v2 a été retardé par un problème de
compatibilité avec le proxy reverse. La vélocité est en baisse
de 15 % par rapport au sprint précédent.

## Questions synthétiques (antithèse)
| # | Question | Réponse attendue | Verdict |
|---|----------|-----------------|---------|
| 1 | Quelles user stories ont été livrées ? | US-34, US-37, US-41 | [non couvert] |
| 2 | Quelle est la cause du retard API v2 ? | Header CORS bloqué par Nginx | [partiel] |
| 3 | Quelles décisions ont été prises ? | Reporter US-38 au sprint 13, pair-programming sur US-39 | [non couvert] |
| 4 | Qui est responsable du fix proxy ? | Marc, livraison prévue mercredi | [non couvert] |
| 5 | Quel est le plan pour remonter la vélocité ? | Réduire le WIP à 3, daily écourtée à 10 min | [non couvert] |

Couverture initiale : 0/5 couvert, 1/5 partiel, 4/5 non couvert

## Itérations de raffinement

| Iter. | Question traitée | Verdict avant > après | Entité ajoutée |
|-------|-----------------|----------------------|----------------|
| 1 | Q1 : US livrées | non couvert > couvert | US-34, US-37, US-41 |

Arrêt : itération unique (route MINI_COS)
Meilleure itération : 1 (couverture 1/5 couvert, 1/5 partiel)

## Résumé final (itération 1)

L'équipe a livré 3 user stories sur 5 prévues au sprint 12 (US-34,
US-37, US-41). Le déploiement de l'API v2 a été retardé par un
problème de compatibilité avec le proxy reverse. La vélocité est
en baisse de 15 % par rapport au sprint précédent.

## Diagnostic
- Route : MINI_COS (650 mots)
- Itérations : 1/1 (arrêt : route MINI_COS)
- Couverture : initiale 0/5 > finale 1/5
- Entités intégrées : US-34, US-37, US-41 (iter.1)
- Lacunes résiduelles : Q3 (décisions), Q4 (responsable fix), Q5 (plan vélocité)
- Langue : FR > FR
```

---

## Checklist de livraison

Avant de considérer le run terminé :

- [ ] Document ingéré et route annoncée
- [ ] Résumé initial produit (~mots-cibles)
- [ ] Questions générées depuis le document source (pas le résumé)
- [ ] Évaluation de couverture initiale affichée
- [ ] Itérations exécutées jusqu'au critère d'arrêt
- [ ] Meilleure itération sélectionnée (pas automatiquement la dernière)
- [ ] Résumé final dans la longueur cible (± 20 %)
- [ ] Diagnostic complet affiché (route, itérations, couverture, lacunes)

---

## Garde-fous

| Risque | Mitigation |
|--------|------------|
| Hallucination d'intégration | Rappel à chaque itération : n'ajouter que des informations du document. Si une entité n'est pas traçable au document, la retirer. |
| Dérive de longueur | Longueur cible ± 20 %. Si dépassée, comprimer avant de continuer. |
| Questions depuis le résumé | Les questions sont TOUJOURS générées depuis le document source, jamais depuis le résumé courant. |
| Oscillation | Si une information disparaît puis réapparaît entre itérations, geler les éléments stables et stopper. |
| Dernière = meilleure | Interdiction de sélection automatique de la dernière itération. Comparer toutes les versions. |
| Mode dégradé silencieux | Toujours afficher la route, les avertissements et le diagnostic complet. |
| Auto-évaluation biaisée | Les questions viennent du document (pas du résumé) — cela brise partiellement la circularité. Exposer les verdicts pour vérification humaine. |

---

## Complémentarité avec /chain-of-density

| Situation | Skill recommandé |
|-----------|-----------------|
| Couverture des entités factuelles clés | `/chain-of-summaries-cos` |
| Compression maximale (budget tokens strict) | `/chain-of-density` |
| Transcript ou document riche → cache réutilisable | `/chain-of-summaries-cos` |
| Documentation verbeuse → synthèse exécutive compacte | `/chain-of-density` |
| Doute | Essayer les deux, comparer la sortie |

**Différence fondamentale** : CoD compresse ce qui est dit (densification par injection d'entités). COS ajoute ce qui manque (raffinement par détection de lacunes).

---

## Limites inhérentes

1. **Scoring approximatif** — le LLM évalue lui-même la couverture (proxy, pas F1 exact). Les verdicts sont exposés pour vérification humaine.
2. **Auto-évaluation** — le même LLM génère, évalue et raffine. Les questions depuis le document brisent partiellement la circularité.
3. **Pas de validation FR empirique** — le papier teste sur TriviaQA/TruthfulQA/SQuAD (anglais). L'efficacité en français est à mesurer empiriquement.
4. **Coût contextuel** — ~6K tokens stables par invocation complète (document + résumé courant + tableau questions + historique condensé).

---

## Principe directeur

Le skill ne doit pas seulement résumer. Il doit apprendre de ce que son résumé ne sait pas encore porter.
