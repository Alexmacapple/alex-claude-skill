#!/usr/bin/env python3
"""
Initialisateur de skill - cree un nouveau skill a partir d'un template francophone
valide empiriquement par SkillsBench (arXiv:2602.12670v1).

Usage :
    init_skill.py <skill-name> --path <path> [--with-assets]

Exemples :
    init_skill.py mon-nouveau-skill --path skills/
    init_skill.py audit-rgaa --path .claude/skills/
    init_skill.py brand-guidelines --path .claude/skills/ --with-assets
"""

import sys
from pathlib import Path


# Template francophone a 7 sections fixes, derive de la Partie IV de
# guidelines-skills.md (SkillsBench). Ne pas modifier
# sans mettre a jour la documentation correspondante.
SKILL_TEMPLATE = """---
name: {skill_name}
description: "[A COMPLETER : description explicite avec declencheurs. Utiliser pour X. Ne pas utiliser pour Y. Declencheurs : a, b, c.]"
---

# {skill_title} — [A COMPLETER : accroche en une phrase]

## Quand l'utiliser

- [A COMPLETER : critère de déclenchement 1]
- [A COMPLETER : critère de déclenchement 2]
- Ne pas utiliser pour : [A COMPLETER : hors périmètre explicite]

## Procédure pas-à-pas

### Étape 1 — [A COMPLETER : nom de l'étape]

[A COMPLETER : description en 2-3 phrases max. Pas de contexte général, pas de théorie.]

**Exemple minimal** :
[A COMPLETER : input concret et output attendu]

### Étape 2 — [A COMPLETER : nom de l'étape]

[A COMPLETER : description en 2-3 phrases max.]

**Exemple minimal** :
[A COMPLETER : input concret et output attendu]

### Étape 3 — [A COMPLETER : nom de l'étape]

[A COMPLETER : description en 2-3 phrases max.]

**Exemple minimal** :
[A COMPLETER : input concret et output attendu]

## Exemple complet end-to-end

[A COMPLETER : un cas réel exécutable du début à la fin, avec les commandes exactes
et la sortie attendue. Pas un pseudo-exemple, un vrai cas reproductible.]

## Pièges connus

- Piège 1 : [A COMPLETER : symptôme observable] → [A COMPLETER : correction concrète]
- Piège 2 : [A COMPLETER : symptôme observable] → [A COMPLETER : correction concrète]
- Piège 3 : [A COMPLETER : symptôme observable] → [A COMPLETER : correction concrète]

## Checklist de livraison

Avant de conclure, vérifier :

- [ ] [A COMPLETER : livrable 1 présent]
- [ ] [A COMPLETER : livrable 2 conforme au format attendu]
- [ ] [A COMPLETER : vérification finale passée]

## Pour aller plus loin

Voir `references/` pour les cas avancés chargés à la demande.

---

<!--
Template genere par skill-creator (PRD-092).

Rappels empiriques SkillsBench :
- Cible : 150-250 lignes, 1 500-2 500 tokens, 6 sections H2 maximum
- Les skills exhaustifs (> 3 000 tokens) sont pires qu'aucun skill (-2,9 pp)
- Focalisation : 1 classe de taches, pas plusieurs melangees
- Au moins 1 exemple end-to-end executable est obligatoire
- Supprimer ce bloc de commentaire avant mise en production

Rappel workspace :
- Pas de README.md dans le dossier du skill (hook pre-commit)
- Pas d'emojis dans le SKILL.md
- Capitalisation francaise (premier mot uniquement en majuscule)
-->
"""

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""
Script d'exemple pour {skill_name}.

Ce script est un placeholder executable. Le remplacer par l'implementation
reelle ou le supprimer si le skill n'a pas besoin de script.

Exemples de scripts utiles dans d'autres skills :
- pdf/scripts/fill_fillable_fields.py - remplit les champs de formulaire PDF
- pdf/scripts/convert_pdf_to_images.py - convertit un PDF en images
"""


def main():
    print("Script d'exemple pour {skill_name}")
    # A COMPLETER : ajouter la logique du script ici


if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = """# Référence détaillée pour {skill_title}

Ce fichier est un placeholder pour une documentation de référence.
Le remplacer par le contenu réel ou le supprimer si le skill n'en a pas besoin.

Les fichiers dans `references/` sont chargés à la demande par Claude Code
quand il a besoin d'informations approfondies qui n'ont pas leur place
dans le SKILL.md principal.

## Quand utiliser references/

- Documentation API exhaustive (endpoints, payloads, codes d'erreur)
- Guides de workflows multi-étapes complexes
- Spécifications techniques trop longues pour le SKILL.md
- Contenu nécessaire seulement pour des cas d'usage spécifiques

## Structure suggérée

### Exemple : référence API

- Vue d'ensemble
- Authentification
- Endpoints avec exemples
- Codes d'erreur
- Limites de débit

### Exemple : guide de workflow

- Prérequis
- Instructions pas à pas
- Patterns courants
- Résolution de problèmes
- Bonnes pratiques
"""


def title_case_skill_name(skill_name):
    """Convertit un nom de skill en kebab-case vers un titre lisible."""
    return ' '.join(word.capitalize() for word in skill_name.split('-'))


def init_skill(skill_name, path, with_assets=False):
    """
    Initialise un nouveau dossier de skill avec un template SKILL.md.

    Args:
        skill_name : nom du skill (kebab-case)
        path : chemin ou creer le dossier du skill
        with_assets : si True, cree aussi le dossier assets/ (defaut False)

    Returns:
        Chemin vers le dossier cree, ou None en cas d'erreur.
    """
    skill_dir = Path(path).resolve() / skill_name

    if skill_dir.exists():
        print(f"[ERREUR] Le dossier du skill existe deja : {skill_dir}")
        return None

    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(f"[OK] Dossier cree : {skill_dir}")
    except Exception as e:
        print(f"[ERREUR] Creation du dossier : {e}")
        return None

    skill_title = title_case_skill_name(skill_name)
    skill_content = SKILL_TEMPLATE.format(
        skill_name=skill_name,
        skill_title=skill_title
    )

    skill_md_path = skill_dir / 'SKILL.md'
    try:
        skill_md_path.write_text(skill_content)
        print("[OK] SKILL.md cree")
    except Exception as e:
        print(f"[ERREUR] Ecriture du SKILL.md : {e}")
        return None

    try:
        scripts_dir = skill_dir / 'scripts'
        scripts_dir.mkdir(exist_ok=True)
        example_script = scripts_dir / 'example.py'
        example_script.write_text(EXAMPLE_SCRIPT.format(skill_name=skill_name))
        example_script.chmod(0o755)
        print("[OK] scripts/example.py cree")

        references_dir = skill_dir / 'references'
        references_dir.mkdir(exist_ok=True)
        example_reference = references_dir / 'guide-detaille.md'
        example_reference.write_text(EXAMPLE_REFERENCE.format(skill_title=skill_title))
        print("[OK] references/guide-detaille.md cree")

        if with_assets:
            assets_dir = skill_dir / 'assets'
            assets_dir.mkdir(exist_ok=True)
            placeholder = assets_dir / '.gitkeep'
            placeholder.write_text("")
            print("[OK] assets/ cree (vide)")
    except Exception as e:
        print(f"[ERREUR] Creation des ressources : {e}")
        return None

    print(f"\n[OK] Skill '{skill_name}' initialise : {skill_dir}")
    print("\nProchaines etapes :")
    print("1. Remplir les [A COMPLETER] du SKILL.md et completer la description")
    print("2. Personnaliser ou supprimer les fichiers scripts/ et references/")
    print("3. Verifier le skill avec /skill-pipeline ou /skill-conformity-checker")

    return skill_dir


def main():
    args = sys.argv[1:]

    if len(args) < 3 or args[1] != '--path':
        print("Usage : init_skill.py <skill-name> --path <path> [--with-assets]")
        print("")
        print("Contraintes du nom de skill :")
        print("  - Identifiant kebab-case (ex : 'mon-analyseur-donnees')")
        print("  - Minuscules, chiffres et tirets uniquement")
        print("  - 64 caracteres maximum")
        print("  - Doit correspondre exactement au nom du dossier")
        print("")
        print("Exemples :")
        print("  init_skill.py mon-nouveau-skill --path skills/")
        print("  init_skill.py audit-rgaa --path .claude/skills/")
        print("  init_skill.py brand-guidelines --path .claude/skills/ --with-assets")
        sys.exit(1)

    skill_name = args[0]
    path = args[2]
    with_assets = '--with-assets' in args

    print(f">> Initialisation du skill : {skill_name}")
    print(f"   Emplacement : {path}")
    if with_assets:
        print(f"   Options : dossier assets/ inclus")
    print("")

    result = init_skill(skill_name, path, with_assets=with_assets)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
