#!/usr/bin/env python3
"""
verify_parsing.py — validation du contrat d'output des sub-agents.

Aligné sur PRD-098 (invariant 2) : chaque sub-agent lancé par /eval-robuste
reçoit une instruction stricte de ne retourner qu'une seule ligne au format
`SCORE: NN/100`. Ce script est la regex de référence du parser amont.

Usage CLI :
  verify_parsing.py < raw_output.txt
  echo "SCORE: 92/100" | verify_parsing.py
  verify_parsing.py --text "SCORE: 92/100"

Sortie : exit 0 + "OK NN" si match, exit 1 + "KO raison" sinon.

Règle unique : dernière ligne non vide doit matcher `^SCORE: \\d{1,3}/100$`
et NN doit être dans [0, 100]. Les lignes précédentes sont tolérées — seule
la dernière ligne non vide est considérée comme « la réponse finale » de
l'agent. C'est cette tolérance qui permet aux agents d'émettre un chain-of-
thought avant la réponse finale sans casser le contrat.
"""

from __future__ import annotations

import argparse
import re
import sys

# P2 (PRD-098 Phase 6) : regex élargie pour tolérer les variations courantes
# observées en Phase 0 :
#   - « SCORE: 92/100 » (canonique)
#   - « Score: 92/100 » (Score au lieu de SCORE)
#   - « Score global : 92/100 » (format skill-review direct)
#   - « SCORE : 92 / 100 » (whitespaces autour)
# Case-insensitive, tolérant aux espaces.
SCORE_RE = re.compile(
    r"^\s*(?:SCORE|Score(?:\s+global)?)\s*:\s*(\d{1,3})\s*/\s*100\s*$",
    re.IGNORECASE,
)

# Nombre de dernières lignes non vides inspectées pour trouver le score.
# Un agent peut ajouter une politesse après le SCORE — on remonte les 3 dernières.
TAIL_LINES_TO_CHECK = 3


def verify(raw: str) -> tuple[bool, int | None, str]:
    """Retourne (is_ok, score_ou_None, message).

    Stratégie tolérante :
    1. Parser chacune des 3 dernières lignes non vides dans l'ordre inverse
       (la plus tardive en priorité).
    2. Retourner le premier match valide trouvé.
    3. Refuser seulement si aucune ligne dans ce fenêtrage ne match.
    """
    if not raw or not raw.strip():
        return False, None, "KO output vide"

    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    if not lines:
        return False, None, "KO output vide après strip"

    tail = lines[-TAIL_LINES_TO_CHECK:]
    for line in reversed(tail):
        match = SCORE_RE.match(line)
        if not match:
            continue
        score = int(match.group(1))
        if score < 0 or score > 100:
            return False, score, f"KO score {score} hors [0, 100]"
        return True, score, f"OK {score}"

    return False, None, f"KO aucune des {TAIL_LINES_TO_CHECK} dernières lignes ne match : {tail[-1]!r}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Validation du contrat d'output SCORE: NN/100 des sub-agents /eval-robuste",
    )
    ap.add_argument("--text", help="Texte à valider (sinon stdin)")
    args = ap.parse_args(argv)

    raw = args.text if args.text is not None else sys.stdin.read()
    ok, score, message = verify(raw)
    print(message)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
