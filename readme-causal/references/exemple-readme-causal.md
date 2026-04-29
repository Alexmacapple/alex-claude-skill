# Exemples de README causal annotés

---

## Exemple 1 — `json-normalizer` (outil CLI Python)

> Contexte fictif : normaliseur JSON en ligne de commande.

**Signaux observés avant de rédiger :**

```
git log --oneline -5
a3f2c1e fix: handle null values in nested objects
b8d04fa feat: add --strict mode for schema enforcement
c12e9a3 init: first working prototype
d44f801 init: project scaffold
```

```
find . -maxdepth 2 -name "*.py" | head -10
./normalizer/cli.py
./normalizer/core.py
./normalizer/validators.py
./tests/test_core.py
```

README existant : 3 lignes ("JSON normalizer. Run: python -m normalizer input.json"). → Réécriture complète (< 5 lignes).

**README causal produit :**

```markdown
# json-normalizer

> README causal — 2026-04-29

## Anamèse [IE]

Les pipelines de données qui agrègent des JSON depuis plusieurs sources
(APIs tierces, exports CSV convertis, formulaires) produisent des
structures hétérogènes : clés en camelCase dans une source, snake_case
dans une autre, valeurs nulles représentées par `null`, `""` ou absentes.
Chaque projet réécrivait le même code de normalisation ad hoc, sans
contrat de schéma partagé.

## Étiologie [FA]

**Kairos** : l'adoption de Pydantic v2 (2023) a rendu la validation de
schéma JSON suffisamment rapide pour être utilisée en entrée de pipeline
sans surcoût mesurable, ce qui rend viable un normaliseur générique là où
une solution custom s'imposait avant.

**Nécessitation** : les outils existants (jsonschema, cerberus) valident
mais ne normalisent pas — ils rejettent le JSON invalide sans le corriger.
Un outil qui valide ET normalise en une passe était la seule option pour
éviter une double dépendance.

## Ossature causale [IC]

**Pattern** : transformation pipeline en une passe — lecture → validation
Pydantic → normalisation → écriture.

**Composants** :
- `core.py` — moteur de normalisation (résout : hétérogénéité des sources)
- `validators.py` — schémas Pydantic v2 (résout : besoin de contrat partagé)
- `cli.py` — interface `--strict` / `--permissive` (résout : cas d'usage
  pipeline automatique vs. débogage manuel)

## Résidu [IE]

**Exclusions assumées** :
- Normalisation de JSON imbriqués > 5 niveaux : complexité disproportionnée
  pour les cas d'usage cibles (fichiers plats ou semi-plats)
- Support XML/YAML en entrée : hors scope délibéré — convertir en amont

**Dettes tracées** :
- Les schémas Pydantic sont définis en dur dans `validators.py` — pas de
  chargement dynamique depuis un fichier externe
```

<!-- ANNOTATION : Anamèse [IE] — inférée depuis la structure multi-sources et les commits "normalisation ad hoc". Étiologie [FA] — kairos fourni par l'auteur lors de la question kairos. Ossature causale [IC] — sourcée depuis la structure du code (noms de fichiers explicites). Résidu [IE] — déduit des TODO et de l'absence de chargement dynamique dans validators.py. -->

---

## Exemple 2 — `voice-transcript`

> Contexte fictif : outil `voice-transcript` — TTS+STT pipeline pour transcription de réunions.

---

# voice-transcript

> README causal — 2026-04-29

## Anamèse [IC]

Les équipes distribuées transcrivent leurs réunions manuellement ou via Whisper en ligne de commande, en produisant des fichiers bruts sans ponctuation ni identification des locuteurs. Les outils existants (Whisper, otter.ai) résolvent la reconnaissance vocale mais pas la structuration : un transcript de 90 minutes prend 45 minutes à nettoyer pour être lisible.

<!-- ANNOTATION : sourcé depuis README existant section "Context" + commit initial "init: raw whisper output is unreadable" -->

## Étiologie [IE]

**Kairos** : L'API Whisper d'OpenAI est devenue accessible en décembre 2022 à un coût < 0,006$/min, rendant la transcription automatique viable pour des budgets petits. Simultanément, les LLMs (GPT-4, Claude) ont atteint une qualité suffisante pour reformater des transcripts sans halluciner les contenus.

<!-- ANNOTATION : kairos extrapolé depuis la date des premiers commits (janv. 2023) et les dépendances openai==0.27.0 dans requirements.txt — marqué [IE] car non explicité dans les commits -->

**Nécessitation** : Les outils de transcription existants (otter.ai, Fireflies) nécessitent un compte enterprise pour le traitement local — impossible pour des données sensibles. Les solutions open source (Whisper seul) ne structurent pas. Un pipeline local combinant Whisper + LLM était la seule option viable pour des équipes soumises à contraintes de confidentialité.

<!-- ANNOTATION : nécessitation inférée depuis le README existant ("local-first, no data leaves your machine") et la structure du code (tout tourne en subprocess local) — [IE] -->

## Causal scaffold [IC]

**Pattern** : pipeline local séquentiel — audio → segments → transcript brut → reformatage LLM → sortie structurée.

**Composants** :
- `audio_splitter.py` — découpe l'audio en segments de 5 min pour rester dans les limites Whisper API (résout : contrainte de taille de fichier Whisper)
- `whisper_client.py` — appel API avec retry exponentiel (résout : instabilité réseau sur longues réunions)
- `transcript_formatter.py` — prompt LLM pour ajouter ponctuation + identification locuteurs (résout : illisibilité du transcript brut Whisper)
- `pipeline.py` — orchestration séquentielle avec cache intermédiaire (résout : relancer depuis le début si une étape échoue)

<!-- ANNOTATION : sourcé depuis la structure du code et les docstrings — [IC] -->

## Résidu [IE]

**Exclusions assumées** :
- Identification automatique des locuteurs par voix : nécessiterait un modèle de diarisation (pyannote) — complexité disproportionnée pour le cas d'usage cible (petites équipes où les locuteurs se connaissent)
- Temps réel : le pipeline est offline-first par design, le temps réel ajouterait de la latence et de la complexité réseau

**Dettes tracées** :
- Le cache intermédiaire n'a pas de TTL — croît indéfiniment. Contournement actuel : nettoyage manuel via `make clean`
- Les prompts LLM sont codés en dur en anglais — une réunion en français produit une sortie en franglais

<!-- ANNOTATION : dettes inférées depuis les TODO dans le code et l'issue #12 "cache gets huge" — [IE] -->

---

## Notes d'annotation

Ce README illustre :
1. **Anamèse [IC]** : quand le README existant contient une section "Context" exploitable
2. **Kairos [IE]** : quand on l'infère des dépendances et dates de commits, sans source explicite
3. **Nécessitation [IE]** : quand on la reconstruit depuis l'architecture "local-first"
4. **Causal scaffold [IC]** : quand les docstrings et noms de fichiers sont parlants
5. **Résidu [IE]** : quand les dettes sont dans les TODO et issues, pas explicitement tracées

Dans un cas réel, le kairos aurait déclenché la question à l'auteur pour passer de [IE] à [FA].
