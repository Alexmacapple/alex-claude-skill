# Classification des skills du workflow

Référence pour le triage du pressure testing et des renforcements GREEN.
Mise à jour : 2026-04-07.

---

## Catégories

| Catégorie | Critère | Pressure test | Anti-rationalisations |
|-----------|---------|--------------|----------------------|
| **Discipline** | Impose un processus que l'agent peut contourner | Obligatoire | Obligatoires |
| **Analytique** | Produit une analyse qui peut être bâclée | Recommandé | Recommandées |
| **Workflow** | Orchestre des phases sans décision comportementale | Optionnel | Non |
| **Mécanique** | Exécute un pipeline déterministe | Non | Non |

---

## Inventaire (61 skills)

### Discipline (15 skills) — pressure test obligatoire

| Skill | Pressure testé | Score RED | Renforcé GREEN |
|-------|---------------|-----------|----------------|
| `/avocat-du-diable` | 2026-04-07 | 0/5 | Oui |
| `/code-review` | 2026-04-07 | 0/5 | Oui |
| `/commit` | 2026-04-07 | 1/5 | Oui |
| `/composition-dsfr-pptx` | 2026-04-07 | 1/5 | Oui |
| `/connu-inconnu` | 2026-04-07 | 0/5 | Oui |
| `/cr-reunion` | 2026-04-07 | 1/5 | Oui |
| `/gherkin` | Non | — | Non |
| `/humanizer` | Non | — | Non |
| `/parcoursup` | 2026-04-07 | 0/5 | Oui |
| `/prd` | 2026-04-07 | 0/5 | Oui |
| `/raisonnement-code` | 2026-04-07 | 1/5 | Oui |
| `/skill-review` | 2026-04-07 | 3/5 | Oui |
| `/slides-pedagogiques` | 2026-04-07 | 0/5 | Oui |
| `/verifier-etat` | 2026-04-07 | 1/5 | Oui |
| `/verifier-regles-md` | Non | — | Non |

### Analytique (14 skills) — pressure test recommandé

| Skill | Pressure testé | Score RED | Renforcé GREEN |
|-------|---------------|-----------|----------------|
| `/architect` | 2026-04-07 | 1/5 | Oui |
| `/audit-accessibilite-web` | Non | — | Non |
| `/audit-a11y-complet` | Non | — | Non |
| `/audit-rgaa` | Non | — | Non |
| `/audit-securite` | Non | — | Non |
| `/chain-of-density` | Non | — | Non |
| `/codex-security-best-practices` | Non | — | Non |
| `/decodeur` | Non | — | Non |
| `/enseignement-llm` | Non | — | Non |
| `/fiches-articles` | 2026-04-07 | 1/5 | Oui |
| `/pedagogie-neuro` | Non | — | Non |
| `/screen-reader-testing` | Non | — | Non |
| `/tests-conformite-wcag` | Non | — | Non |
| `/ux-checklist` | Non | — | Non |

### Workflow (12 skills) — pressure test optionnel

| Skill | Pressure testé | Score RED | Renforcé GREEN |
|-------|---------------|-----------|----------------|
| `/a11y-ci` | Non | — | Non |
| `/a11y-loop` | Non | — | Non |
| `/claude-code-veille` | Non | — | Non |
| `/sg-visual-discover` (plugin ShipGuard) | Plugin upstream | Gere par bacoco | Non |
| `/sg-visual-run` (plugin ShipGuard) | Plugin upstream | Gere par bacoco | Non |
| `/fix-accessibilite` | Non | — | Non |
| `/make-agent-md` | Non | — | Non |
| `/pipeline-document` | 2026-04-07 | 0/5 | Oui |
| `/sauvegarde-git` | Non | — | Non |
| `/skill-conformity-checker` | Non | — | Non |
| `/skill-creator` | Non | — | Non (template enrichi) |
| `/skill-pipeline` | Non | — | Non (phase 5 ajoutée) |

### Mécanique (16 skills) — pas de pressure test

| Skill | Raison d'exclusion |
|-------|--------------------|
| `/accessible-docx` | Pipeline déterministe (Pandoc) |
| `/accessible-html` | Pipeline déterministe (Pandoc) |
| `/accessible-pdf` | Pipeline déterministe (Pandoc + WeasyPrint) |
| `/accessible-pptx` | Pipeline déterministe (Pandoc + python-pptx) |
| `/agent-browser` | Exécution de commandes browser |
| `/anti-paresse` | Meta-skill interne |
| `/browse` | Navigation web déterministe |
| `/doctor` | Checks diagnostiques déterministes |
| `/dsfr-components` | Génération HTML déterministe |
| `/langgraph` | Référence technique (pas de processus) |
| `/meta-prompt-concept` | Génération créative (pas de processus contournable) |
| `/monter-mac-studio` | Script NFS déterministe |
| `/nano-rwd` | Pipeline CSS déterministe |
| `/ocr-pdf-to-word` | Pipeline OCR déterministe |
| `/opensrc-sync` | Script sync déterministe |
| `/pdf` | Pipeline conversion déterministe |
| `/playbook` | Génération de scripts bash |
| `/qwen-image` | Constructeur de prompts créatif |
| `/remediation-docx` | Pipeline déterministe |
| `/transfer` | Transfert SSH déterministe |

### Hors triage (4 skills) — cas particuliers

| Skill | Raison |
|-------|--------|
| `/claude-api` | Référence SDK, pas de processus |
| `/conductor` | Framework externe (TDD) |
| `/frontend-design` | Plugin externe |
| `/codex:*` | Plugin Codex (4 skills internes) |

---

## Statistiques

| Catégorie | Total | Pressure testés | Renforcés GREEN |
|-----------|-------|----------------|-----------------|
| Discipline | 15 | 13 | 13 |
| Analytique | 14 | 2 | 2 |
| Workflow | 12 | 1 | 1 |
| Mécanique | 16+4 | 0 | 0 |
| **Total** | **61** | **16** | **16** |

---

## Prochaines vagues de pressure testing

| Vague | Skills | Priorité |
|-------|--------|----------|
| 4 | gherkin, humanizer, verifier-regles-md, audit-securite, audit-accessibilite-web | Haute |
| 5 | decodeur, pedagogie-neuro, enseignement-llm, ux-checklist, chain-of-density | Moyenne |
| 6 | audit-rgaa, audit-a11y-complet, codex-security-best-practices, screen-reader-testing, tests-conformite-wcag | Basse |
