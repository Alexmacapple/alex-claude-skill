#!/usr/bin/env python3
"""
check_n.py — enforcement par construction de l'invariant 4 de PRD-098.

Plafond N = 10, confirmation obligatoire si N >= 8, --force requis au-dela
de 10. Ce script est appele en ouverture de l'Etape 1 du workflow
/eval-robuste. Il ne fait AUCUN calcul statistique et ne lit aucun score :
son seul role est de refuser un argument --n hors des bornes acceptables.

Usage :
  check_n.py --n 5                -> exit 0, OK silencieux
  check_n.py --n 8                -> exit 0 avec avertissement coût et
                                      demande de confirmation (à tracer par
                                      l'appelant)
  check_n.py --n 11               -> exit 2, refus franc
  check_n.py --n 11 --force       -> exit 0 avec avertissement
  check_n.py --n 1                -> exit 2, refus franc (min = 2)

Exit codes :
  0 : OK (N valide, eventuellement avec warning)
  1 : N mal forme (non-entier, vide, etc.)
  2 : N hors bornes et --force absent

Invariant 4 de PRD-098 (non negociable) :
  - 2 <= N <= 10 : autorise sans force
  - N >= 8       : confirmation recommandee (le LLM doit demander a l'utilisateur)
  - N > 10       : exige --force explicite, message d'avertissement sur le cout
  - N < 2        : refus franc (pas de statistique possible avec n<2)
"""

from __future__ import annotations

import argparse
import sys


PLAFOND_DUR = 10
SEUIL_CONFIRMATION = 8
N_MIN = 2
COUT_PAR_RUN_K_TOKENS = 60  # ordre de grandeur observe en Phase 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Enforcement par construction du plafond N (PRD-098 invariant 4)"
    )
    ap.add_argument("--n", required=True, help="Nombre de runs paralleles demande")
    ap.add_argument("--force", action="store_true", help="Contourne le plafond N>10")
    args = ap.parse_args(argv)

    try:
        n = int(args.n)
    except ValueError:
        print(f"ERREUR : --n doit etre un entier, recu : {args.n!r}", file=sys.stderr)
        return 1

    if n < N_MIN:
        print(
            f"REFUS : N={n} < {N_MIN}. Aucune estimation statistique valable "
            f"en dessous de 2 runs. Invariant 4 de PRD-098.",
            file=sys.stderr,
        )
        return 2

    if n > PLAFOND_DUR and not args.force:
        print(
            f"REFUS : N={n} > plafond dur {PLAFOND_DUR} sans --force. "
            f"Cout estime : {n * COUT_PAR_RUN_K_TOKENS} k tokens. "
            f"Invariant 4 de PRD-098.",
            file=sys.stderr,
        )
        return 2

    # OK avec warnings eventuels
    cout_estime = n * COUT_PAR_RUN_K_TOKENS
    if n > PLAFOND_DUR:
        print(
            f"WARNING : N={n} > {PLAFOND_DUR}, --force actif. "
            f"Cout estime : {cout_estime} k tokens. A tracer dans le rapport.",
            file=sys.stderr,
        )
    elif n >= SEUIL_CONFIRMATION:
        print(
            f"WARNING : N={n} >= {SEUIL_CONFIRMATION}, "
            f"confirmation utilisateur recommandee. "
            f"Cout estime : {cout_estime} k tokens.",
            file=sys.stderr,
        )

    # Toujours afficher le cout en stdout pour que l'appelant puisse l'utiliser
    print(f"OK N={n} cout_estime_k_tokens={cout_estime}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
