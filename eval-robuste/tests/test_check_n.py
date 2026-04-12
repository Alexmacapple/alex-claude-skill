#!/usr/bin/env python3
"""Tests pour check_n.py (PRD-098 invariant 4 par construction)."""

import subprocess
import sys
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
CHECK_N = SKILL_DIR / "scripts" / "check_n.py"


def run_check_n(*args: str) -> tuple[int, str, str]:
    """Retourne (exit_code, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, str(CHECK_N), *args],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


class TestCheckN(unittest.TestCase):

    def test_n_valide_exit_0(self):
        code, out, _ = run_check_n("--n", "5")
        self.assertEqual(code, 0)
        self.assertIn("OK N=5", out)
        self.assertIn("cout_estime_k_tokens=300", out)

    def test_n_min_2_ok(self):
        code, _, _ = run_check_n("--n", "2")
        self.assertEqual(code, 0)

    def test_n_plafond_10_ok(self):
        code, _, _ = run_check_n("--n", "10")
        self.assertEqual(code, 0)

    def test_n_seuil_confirmation_8_ok_avec_warning(self):
        code, out, err = run_check_n("--n", "8")
        self.assertEqual(code, 0)
        self.assertIn("WARNING", err)
        self.assertIn("confirmation utilisateur recommandee", err)

    def test_n_depasse_plafond_sans_force_refus(self):
        code, _, err = run_check_n("--n", "11")
        self.assertEqual(code, 2)
        self.assertIn("REFUS", err)
        self.assertIn("> plafond dur 10", err)
        self.assertIn("660 k tokens", err)

    def test_n_depasse_plafond_avec_force_ok(self):
        code, out, err = run_check_n("--n", "15", "--force")
        self.assertEqual(code, 0)
        self.assertIn("WARNING", err)
        self.assertIn("OK N=15", out)

    def test_n_inferieur_min_refus(self):
        code, _, err = run_check_n("--n", "1")
        self.assertEqual(code, 2)
        self.assertIn("REFUS", err)
        self.assertIn("< 2", err)

    def test_n_non_entier_erreur(self):
        code, _, err = run_check_n("--n", "cinq")
        self.assertEqual(code, 1)
        self.assertIn("ERREUR", err)
        self.assertIn("entier", err)


if __name__ == "__main__":
    unittest.main(verbosity=2)
