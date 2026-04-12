#!/usr/bin/env python3
"""
rotate_archives.py — rotation LRU des archives /eval-robuste.

Politique alignée sur PRD-098 § Phase 5 « rétention » :
- `.claude/outputs/eval-robuste/<skill>/` : conserver les N dernières
  mesures par skill (défaut 20). Au-delà, suppression du plus ancien.
- `.claude/outputs/skill-review-history/<skill>/` : conserver M derniers
  rapports par skill (défaut 30). Au-delà, suppression du plus ancien.

Chaque « mesure » de /eval-robuste est un dossier horodaté
`YYYY-MM-DD-HHMMSS/` contenant baseline.json + rapport.md. L'ordre LRU
est déterminé par le nom du dossier (tri lexical = tri temporel car
format ISO-compatible).

Chaque rapport de skill-review (Phase 1.5) est un fichier unique
`YYYY-MM-DD-HHMMSS.md` directement dans le dossier du skill.

Usage CLI :
  rotate_archives.py                          # applique les 2 politiques
  rotate_archives.py --keep-eval 20           # override eval-robuste
  rotate_archives.py --keep-history 30        # override skill-review-history
  rotate_archives.py --dry-run                # montre sans supprimer

Exit codes :
  0 : OK (rotation appliquée ou aucune action nécessaire)
  1 : erreur (chemin invalide, permissions, etc.)

Dépendances : stdlib uniquement.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


DEFAULT_KEEP_EVAL = 20
DEFAULT_KEEP_HISTORY = 30

EVAL_ROOT = Path.home() / ".claude/outputs/eval-robuste"
HISTORY_ROOT = Path.home() / ".claude/outputs/skill-review-history"


def rotate_directory_entries(
    skill_dir: Path, keep: int, dry_run: bool, entry_is_dir: bool
) -> tuple[int, int]:
    """Supprime les entrées les plus anciennes au-delà de `keep`.

    Retourne (kept_count, removed_count).
    """
    if not skill_dir.exists() or not skill_dir.is_dir():
        return (0, 0)

    if entry_is_dir:
        entries = sorted(
            [p for p in skill_dir.iterdir() if p.is_dir() and not p.name.startswith("_")],
            key=lambda p: p.name,
        )
    else:
        entries = sorted(
            [p for p in skill_dir.iterdir() if p.is_file() and p.suffix == ".md"],
            key=lambda p: p.name,
        )

    if len(entries) <= keep:
        return (len(entries), 0)

    to_remove = entries[: len(entries) - keep]
    for entry in to_remove:
        if dry_run:
            continue
        if entry_is_dir:
            shutil.rmtree(entry)
        else:
            entry.unlink()

    return (keep, len(to_remove))


def rotate_root(
    root: Path, keep: int, dry_run: bool, entry_is_dir: bool, label: str
) -> int:
    """Applique la rotation à tous les sous-dossiers d'un root. Retourne le nombre total supprimé."""
    if not root.exists():
        print(f"[{label}] Root inexistant : {root} (ignoré)")
        return 0

    total_removed = 0
    for skill_dir in sorted(root.iterdir()):
        if not skill_dir.is_dir():
            continue
        if skill_dir.name.startswith("_"):
            # Dossiers de baseline type _baseline-YYYY-MM-DD préservés
            continue
        kept, removed = rotate_directory_entries(skill_dir, keep, dry_run, entry_is_dir)
        total_removed += removed
        if removed > 0:
            prefix = "[DRY-RUN] " if dry_run else ""
            print(
                f"[{label}] {prefix}{skill_dir.name}: garde {kept}, "
                f"supprime {removed} ancien(s)"
            )
        elif kept > 0:
            print(f"[{label}] {skill_dir.name}: {kept} entrée(s), rien à supprimer")
    return total_removed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Rotation LRU des archives /eval-robuste et skill-review-history (PRD-098 Phase 5)"
    )
    ap.add_argument(
        "--keep-eval",
        type=int,
        default=DEFAULT_KEEP_EVAL,
        help=f"Nombre de mesures /eval-robuste à conserver par skill (défaut {DEFAULT_KEEP_EVAL})",
    )
    ap.add_argument(
        "--keep-history",
        type=int,
        default=DEFAULT_KEEP_HISTORY,
        help=f"Nombre de rapports skill-review à conserver par skill (défaut {DEFAULT_KEEP_HISTORY})",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Afficher les suppressions prévues sans les appliquer",
    )
    ap.add_argument(
        "--eval-root",
        type=Path,
        default=EVAL_ROOT,
        help=f"Override du root eval-robuste (défaut {EVAL_ROOT})",
    )
    ap.add_argument(
        "--history-root",
        type=Path,
        default=HISTORY_ROOT,
        help=f"Override du root skill-review-history (défaut {HISTORY_ROOT})",
    )
    args = ap.parse_args(argv)

    if args.keep_eval < 1 or args.keep_history < 1:
        print("ERREUR : --keep-* doit être >= 1", file=sys.stderr)
        return 1

    print(f"=== Rotation LRU (dry-run={args.dry_run}) ===")
    total_eval = rotate_root(
        args.eval_root, args.keep_eval, args.dry_run, entry_is_dir=True, label="eval-robuste"
    )
    total_history = rotate_root(
        args.history_root,
        args.keep_history,
        args.dry_run,
        entry_is_dir=False,
        label="skill-review-history",
    )
    print(
        f"=== Total : eval-robuste {total_eval} supprimé(s), "
        f"skill-review-history {total_history} supprimé(s) ==="
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
