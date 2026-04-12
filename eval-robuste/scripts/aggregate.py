#!/usr/bin/env python3
"""
aggregate.py — agrégation statistique déterministe pour /eval-robuste.

Aligné sur PRD-098 (invariant 1) : aucun calcul statistique ne passe par le
LLM. Ce script est la source unique de vérité pour la médiane, l'écart-type,
l'intervalle de confiance, et le verdict delta > seuil × σ.

Dépendances : stdlib uniquement (argparse, json, math, statistics, sys, pathlib).

Usage CLI :
  aggregate.py --scores "92,88,90,85,91" [--sigma 1.5]
  aggregate.py --scores "86,84,88,85,87" --compare-to path/to/baseline.json \\
               --current-prompt-hash sha256:abc... [--current-model claude-opus-4-6]

Sortie : JSON (stdout). Exit 0 = OK, 1 = entrée mal formée, 2 = n_valid < 3
(politique d'échec partiel), 3 = baseline obsolète (prompt_hash divergent).

Politique d'échec partiel (alignée PRD-098 § Politique d'échec partiel) :
- n_valid ≥ 3 : agrégation normale
- n_valid < 3 : exit 2, pas d'agrégation, message d'erreur

Règle de décision delta (alignée PRD-098 § Règle de décision) :
- |delta_median| > sigma × σ_ref → SIGNIFICATIF (REGRESSION si delta < 0,
                                                 AMELIORATION si delta > 0)
- sinon → BRUIT

Intervalle de confiance : borne heuristique médiane ± 1.282 × σ. Approximation
gaussienne, à relativiser pour n < 10. Documenté dans le SKILL.md.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path


# Approximation gaussienne : z₀.₉ ≈ 1.282 pour IC 80 % bilatéral
Z_IC_80 = 1.282


def compute_stats(scores: list[int]) -> dict:
    """Calcule les statistiques descriptives d'une liste de scores entiers.

    L'IC 80 % est clippé à [0, 100] puisque les scores sont bornés par
    construction. Le champ `ic_fiabilite` indique si l'approximation
    gaussienne est fiable (n >= 10) ou faible (n < 10) — correction du
    finding P4 de la revue /avocat-du-diable (PRD-098 Phase 4).
    """
    n = len(scores)
    mean = statistics.mean(scores)
    median = statistics.median(scores)
    stdev = statistics.stdev(scores) if n >= 2 else 0.0
    half_width = Z_IC_80 * stdev
    ic_low_raw = median - half_width
    ic_high_raw = median + half_width
    # Clip aux bornes physiques des scores /100
    ic_low = max(0.0, ic_low_raw)
    ic_high = min(100.0, ic_high_raw)
    # Fiabilité de l'approximation gaussienne
    ic_fiabilite = "bonne" if n >= 10 else "faible"
    return {
        "n_valid": n,
        "mean": round(mean, 2),
        "median": round(median, 2),
        "stdev": round(stdev, 3),
        "ic_80_low": round(ic_low, 2),
        "ic_80_high": round(ic_high, 2),
        "ic_fiabilite": ic_fiabilite,
        "min": min(scores),
        "max": max(scores),
    }


def verdict_intrinseque(stdev: float) -> str:
    """Verdict de stabilité quand il n'y a pas de baseline à comparer."""
    if stdev < 3.0:
        return "STABLE"
    return "INSTABLE"


def compare_with_ref(
    current_stats: dict,
    ref_path: Path,
    sigma_threshold: float,
    current_prompt_hash: str | None,
    current_model: str | None,
) -> dict:
    """Compare une nouvelle mesure à un baseline archivé.

    Retourne un dict avec verdict, delta et métadonnées de la comparaison.
    Lève ValueError si le baseline est structurellement invalide.
    Retourne verdict=BASELINE_OBSOLETE si le prompt_hash diffère.
    """
    ref_raw = json.loads(ref_path.read_text(encoding="utf-8"))
    ref_stats = ref_raw.get("stats", {})
    ref_median = ref_stats.get("median")
    ref_stdev = ref_stats.get("stdev", ref_stats.get("std"))

    if ref_median is None or ref_stdev is None:
        raise ValueError(
            f"Baseline {ref_path} invalide : stats.median ou stats.stdev absent"
        )

    ref_prompt_hash = ref_raw.get("prompt_hash")
    ref_model = ref_raw.get("model_id")

    # Invariant 3 du PRD : refus de comparaison si prompt divergent
    if current_prompt_hash and ref_prompt_hash and current_prompt_hash != ref_prompt_hash:
        return {
            "verdict": "BASELINE_OBSOLETE",
            "delta_vs_ref": None,
            "ref_median": ref_median,
            "ref_stdev": ref_stdev,
            "ref_prompt_hash": ref_prompt_hash,
            "current_prompt_hash": current_prompt_hash,
            "message": "Le prompt interne a changé depuis la baseline — relancer une nouvelle baseline",
        }

    # H4 du PRD : avertissement (pas refus) si le modèle diffère
    model_warning = None
    if current_model and ref_model and current_model != ref_model:
        model_warning = (
            f"Le modèle a changé depuis la baseline ({ref_model} → {current_model}). "
            "La comparaison peut être biaisée."
        )

    delta = current_stats["median"] - ref_median
    seuil_points = sigma_threshold * ref_stdev

    if abs(delta) > seuil_points:
        verdict = "REGRESSION" if delta < 0 else "AMELIORATION"
    else:
        verdict = "BRUIT"

    return {
        "verdict": verdict,
        "delta_vs_ref": round(delta, 2),
        "ref_median": ref_median,
        "ref_stdev": ref_stdev,
        "seuil_delta_points": round(seuil_points, 2),
        "ref_prompt_hash": ref_prompt_hash,
        "model_warning": model_warning,
    }


def parse_scores(raw: str) -> list[int]:
    """Parse 'S1,S2,...' en liste d'entiers, lève ValueError si mal formé."""
    items = [s.strip() for s in raw.split(",") if s.strip()]
    if not items:
        raise ValueError("Liste de scores vide")
    return [int(s) for s in items]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Agrégation statistique déterministe pour /eval-robuste (PRD-098)",
    )
    ap.add_argument("--scores", required=True, help="Scores séparés par virgule, ex : 92,88,90")
    ap.add_argument("--sigma", type=float, default=1.5, help="Seuil multiplicateur σ (défaut 1.5)")
    ap.add_argument("--compare-to", help="Chemin vers un baseline.json à comparer (optionnel)")
    ap.add_argument("--current-prompt-hash", help="Hash sha256 du prompt interne courant")
    ap.add_argument("--current-model", help="ID du modèle utilisé pour les runs courants")
    args = ap.parse_args(argv)

    try:
        scores = parse_scores(args.scores)
    except ValueError as exc:
        print(json.dumps({"error": f"Scores mal formés : {exc}"}, ensure_ascii=False))
        return 1

    # Politique d'échec partiel : n_valid < 3 → erreur
    if len(scores) < 3:
        print(
            json.dumps(
                {
                    "error": f"n_valid={len(scores)} < 3, agrégation refusée",
                    "politique": "échec partiel (PRD-098)",
                },
                ensure_ascii=False,
            )
        )
        return 2

    stats = compute_stats(scores)
    result = {
        **stats,
        "sigma_threshold": args.sigma,
        "scores_bruts": scores,
    }

    if args.compare_to:
        try:
            comparison = compare_with_ref(
                stats,
                Path(args.compare_to),
                args.sigma,
                args.current_prompt_hash,
                args.current_model,
            )
        except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
            print(json.dumps({"error": f"Baseline invalide : {exc}"}, ensure_ascii=False))
            return 1
        result.update(comparison)
        if comparison["verdict"] == "BASELINE_OBSOLETE":
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 3
    else:
        result["verdict"] = verdict_intrinseque(stats["stdev"])
        result["delta_vs_ref"] = None

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
