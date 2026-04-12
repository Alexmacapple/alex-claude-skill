#!/usr/bin/env python3
"""
Tests déterministes pour aggregate.py (PRD-098 Phase 1).

Utilise unittest (stdlib) — pas de dépendance pytest. Couvre 7 cas :

1. stats identiques   : σ=0, verdict STABLE
2. stats dispersés    : σ>3, verdict INSTABLE
3. n_valid < 3        : exit 2, politique d'échec partiel
4. comparaison BRUIT  : delta < 1.5 σ_ref
5. comparaison REGRESSION : delta > 1.5 σ_ref (négatif)
6. baseline obsolète  : prompt_hash divergent → exit 3
7. scores mal formés  : exit 1

Invocation :
    cd ~/Claude/.claude/skills/eval-robuste
    python3 -m unittest tests.test_aggregate -v
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
AGG = SKILL_DIR / "scripts" / "aggregate.py"


def run_aggregate(*args: str) -> tuple[int, dict]:
    """Lance aggregate.py avec les args donnés, retourne (exit_code, json_parsé)."""
    result = subprocess.run(
        [sys.executable, str(AGG), *args],
        capture_output=True,
        text=True,
    )
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError:
        parsed = {"raw_stdout": result.stdout, "raw_stderr": result.stderr}
    return result.returncode, parsed


class TestAggregateStats(unittest.TestCase):
    """Statistiques descriptives sur scores sans comparaison."""

    def test_scores_identiques_verdict_stable(self):
        code, out = run_aggregate("--scores", "90,90,90,90,90")
        self.assertEqual(code, 0)
        self.assertEqual(out["n_valid"], 5)
        self.assertEqual(out["median"], 90)
        self.assertEqual(out["stdev"], 0.0)
        self.assertEqual(out["verdict"], "STABLE")
        self.assertIsNone(out["delta_vs_ref"])

    def test_scores_disperses_verdict_instable(self):
        # σ attendu ≈ 6.52 (sur [80, 85, 90, 95, 100])
        code, out = run_aggregate("--scores", "80,85,90,95,100")
        self.assertEqual(code, 0)
        self.assertEqual(out["median"], 90)
        self.assertGreater(out["stdev"], 3.0)
        self.assertEqual(out["verdict"], "INSTABLE")

    def test_n_valid_inferieur_3_echec_partiel(self):
        code, out = run_aggregate("--scores", "90,92")
        self.assertEqual(code, 2)
        self.assertIn("error", out)
        self.assertIn("échec partiel", out.get("politique", ""))

    def test_scores_mal_formes_erreur(self):
        code, out = run_aggregate("--scores", "90,abc,92,93,95")
        self.assertEqual(code, 1)
        self.assertIn("error", out)


class TestAggregateCompare(unittest.TestCase):
    """Comparaisons avec baseline archivée."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.baseline_path = Path(self.tmp.name) / "baseline.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _write_baseline(self, median, stdev, prompt_hash="sha256:abc", model="claude-opus-4-6"):
        self.baseline_path.write_text(
            json.dumps(
                {
                    "skill": "dummy",
                    "stats": {"median": median, "stdev": stdev},
                    "prompt_hash": prompt_hash,
                    "model_id": model,
                }
            ),
            encoding="utf-8",
        )

    def test_comparaison_bruit(self):
        """Delta de 2 points, σ_ref=3, seuil 1.5×3=4.5 → BRUIT."""
        self._write_baseline(median=90, stdev=3.0)
        code, out = run_aggregate(
            "--scores", "88,88,88,88,88",
            "--compare-to", str(self.baseline_path),
            "--sigma", "1.5",
            "--current-prompt-hash", "sha256:abc",
        )
        self.assertEqual(code, 0)
        self.assertEqual(out["verdict"], "BRUIT")
        self.assertEqual(out["delta_vs_ref"], -2.0)
        self.assertEqual(out["ref_median"], 90)
        self.assertEqual(out["seuil_delta_points"], 4.5)

    def test_comparaison_regression(self):
        """Delta de -10 points, σ_ref=3, seuil 4.5 → REGRESSION (delta < 0)."""
        self._write_baseline(median=90, stdev=3.0)
        code, out = run_aggregate(
            "--scores", "80,80,80,80,80",
            "--compare-to", str(self.baseline_path),
            "--sigma", "1.5",
            "--current-prompt-hash", "sha256:abc",
        )
        self.assertEqual(code, 0)
        self.assertEqual(out["verdict"], "REGRESSION")
        self.assertEqual(out["delta_vs_ref"], -10.0)

    def test_comparaison_amelioration(self):
        """Delta de +10 points, σ_ref=3, seuil 4.5 → AMELIORATION."""
        self._write_baseline(median=90, stdev=3.0)
        code, out = run_aggregate(
            "--scores", "100,100,100,100,100",
            "--compare-to", str(self.baseline_path),
            "--current-prompt-hash", "sha256:abc",
        )
        self.assertEqual(code, 0)
        self.assertEqual(out["verdict"], "AMELIORATION")
        self.assertEqual(out["delta_vs_ref"], 10.0)

    def test_baseline_obsolete_prompt_hash_divergent(self):
        """Invariant 3 du PRD : refus de comparaison si prompt_hash diffère."""
        self._write_baseline(median=90, stdev=3.0, prompt_hash="sha256:OLD")
        code, out = run_aggregate(
            "--scores", "88,88,88,88,88",
            "--compare-to", str(self.baseline_path),
            "--current-prompt-hash", "sha256:NEW",
        )
        self.assertEqual(code, 3)
        self.assertEqual(out["verdict"], "BASELINE_OBSOLETE")
        self.assertIsNone(out["delta_vs_ref"])
        self.assertIn("prompt", out["message"].lower())

    def test_comparaison_warning_modele_different(self):
        """H4 du PRD : warning (pas refus) si le modèle diffère."""
        self._write_baseline(median=90, stdev=3.0, model="claude-opus-4-5")
        code, out = run_aggregate(
            "--scores", "89,89,89,89,89",
            "--compare-to", str(self.baseline_path),
            "--current-prompt-hash", "sha256:abc",
            "--current-model", "claude-opus-4-6",
        )
        self.assertEqual(code, 0)
        self.assertEqual(out["verdict"], "BRUIT")
        self.assertIsNotNone(out["model_warning"])
        self.assertIn("4-5", out["model_warning"])


class TestICClipping(unittest.TestCase):
    """Finding P4 de la revue avocat-du-diable : IC clippé à [0, 100]."""

    def test_ic_high_clippe_a_100(self):
        """Scores proches de 100 avec forte variance → ic_high doit être clippé."""
        code, out = run_aggregate("--scores", "85,100,100,98,95")
        self.assertEqual(code, 0)
        self.assertLessEqual(out["ic_80_high"], 100.0)
        self.assertGreaterEqual(out["ic_80_low"], 0.0)

    def test_ic_low_clippe_a_0(self):
        """Scores proches de 0 avec forte variance → ic_low doit être clippé."""
        code, out = run_aggregate("--scores", "0,5,10,15,0")
        self.assertEqual(code, 0)
        self.assertGreaterEqual(out["ic_80_low"], 0.0)
        self.assertLessEqual(out["ic_80_high"], 100.0)

    def test_ic_fiabilite_faible_pour_n_inferieur_10(self):
        code, out = run_aggregate("--scores", "85,90,95,92,88")
        self.assertEqual(code, 0)
        self.assertEqual(out["ic_fiabilite"], "faible")

    def test_ic_fiabilite_bonne_pour_n_superieur_ou_egal_10(self):
        code, out = run_aggregate("--scores", "85,90,95,92,88,91,89,93,87,94")
        self.assertEqual(code, 0)
        self.assertEqual(out["n_valid"], 10)
        self.assertEqual(out["ic_fiabilite"], "bonne")


class TestDeterminisme(unittest.TestCase):
    """Invariant 1 : aggregate.py doit être déterministe au bit près."""

    def test_meme_entree_meme_sortie_sur_10_runs(self):
        """10 invocations successives avec mêmes scores → JSON identique."""
        args = ["--scores", "92,88,90,85,91", "--sigma", "1.5"]
        first_code, first_out = run_aggregate(*args)
        self.assertEqual(first_code, 0)
        first_json = json.dumps(first_out, sort_keys=True)
        for _ in range(9):
            code, out = run_aggregate(*args)
            self.assertEqual(code, 0)
            self.assertEqual(json.dumps(out, sort_keys=True), first_json)


if __name__ == "__main__":
    unittest.main(verbosity=2)
