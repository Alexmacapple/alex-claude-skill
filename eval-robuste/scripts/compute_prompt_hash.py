#!/usr/bin/env python3
"""
compute_prompt_hash.py — calcul du hash combiné de la chaîne d'évaluation.

Finding P3 de la revue /avocat-du-diable (PRD-098 Phase 4) : l'invariant 3
du PRD ne hashait que prompt_template.txt, pas les dépendances amont. Si
skill-review/SKILL.md ou sa grille changent, une baseline archivée reste
techniquement « compatible » (même prompt_hash) alors que la méthode de
notation a dérivé.

Ce script calcule un hash sha256 du tuple (contenus concaténés) :

    prompt_template.txt
    + skill-review/SKILL.md
    + skill-review/references/grilles.md

Plus optionnellement le commit SHA courant de git comme champ séparé, utile
pour tracer l'état du workspace sans le faire bloquer la comparaison.

Usage CLI :
    compute_prompt_hash.py                      # affiche le hash combiné
    compute_prompt_hash.py --json               # sortie JSON avec détails
    compute_prompt_hash.py --workspace PATH     # override workspace root

Sortie stdout :
    mode texte : « sha256:<hex> »
    mode JSON  : {"prompt_hash": "sha256:...", "components": {...}, "commit_sha": "..."}

Exit codes :
    0 : OK
    1 : fichier source manquant
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


DEFAULT_WORKSPACE = Path.cwd()

COMPONENT_PATHS = [
    ".claude/skills/eval-robuste/scripts/prompt_template.txt",
    ".claude/skills/skill-review/SKILL.md",
    ".claude/skills/skill-review/references/grilles.md",
]


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def combined_hash(workspace: Path) -> tuple[str, dict, list[str]]:
    """Retourne (combined_hash_hex, per_component_hashes, missing_files)."""
    hasher = hashlib.sha256()
    per_component = {}
    missing = []
    for rel in COMPONENT_PATHS:
        abs_path = workspace / rel
        if not abs_path.exists():
            missing.append(rel)
            continue
        content = abs_path.read_bytes()
        hasher.update(content)
        per_component[rel] = hashlib.sha256(content).hexdigest()
    return hasher.hexdigest(), per_component, missing


def git_commit_sha(workspace: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(workspace),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.SubprocessError):
        pass
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Hash combiné de la chaîne d'évaluation pour /eval-robuste (PRD-098 P3)"
    )
    ap.add_argument(
        "--workspace",
        type=Path,
        default=DEFAULT_WORKSPACE,
        help=f"Racine du workspace (défaut {DEFAULT_WORKSPACE})",
    )
    ap.add_argument(
        "--json",
        action="store_true",
        help="Sortie JSON avec détails par composant + commit SHA",
    )
    args = ap.parse_args(argv)

    combined, per_component, missing = combined_hash(args.workspace)

    if missing:
        print(
            f"ERREUR : fichiers manquants : {missing}",
            file=sys.stderr,
        )
        return 1

    if args.json:
        result = {
            "prompt_hash": f"sha256:{combined}",
            "components": per_component,
            "commit_sha": git_commit_sha(args.workspace),
            "component_count": len(per_component),
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"sha256:{combined}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
