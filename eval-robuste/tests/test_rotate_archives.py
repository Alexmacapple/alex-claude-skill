#!/usr/bin/env python3
"""Tests pour rotate_archives.py (PRD-098 Phase 5 rétention LRU)."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
ROTATE = SKILL_DIR / "scripts" / "rotate_archives.py"


def run_rotate(*args: str) -> tuple[int, str, str]:
    """Retourne (exit_code, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, str(ROTATE), *args],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


class TestRotateArchives(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.eval_root = self.tmp_path / "eval-robuste"
        self.history_root = self.tmp_path / "skill-review-history"
        self.eval_root.mkdir()
        self.history_root.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def _make_eval_measurements(self, skill: str, n: int):
        """Crée n dossiers horodatés avec un baseline.json bidon."""
        skill_dir = self.eval_root / skill
        skill_dir.mkdir(exist_ok=True)
        for i in range(n):
            ts = f"2026-01-{i+1:02d}-120000"
            d = skill_dir / ts
            d.mkdir()
            (d / "baseline.json").write_text('{"test": true}')

    def _make_history_reports(self, skill: str, n: int):
        """Crée n fichiers .md horodatés bidon."""
        skill_dir = self.history_root / skill
        skill_dir.mkdir(exist_ok=True)
        for i in range(n):
            ts = f"2026-01-{i+1:02d}-120000"
            (skill_dir / f"{ts}.md").write_text(f"SCORE: {80+i}/100\n")

    def test_eval_robuste_rotation_supprime_les_plus_anciens(self):
        self._make_eval_measurements("skill-a", 25)
        code, out, _ = run_rotate(
            "--eval-root", str(self.eval_root),
            "--history-root", str(self.history_root),
            "--keep-eval", "20",
        )
        self.assertEqual(code, 0)
        remaining = sorted((self.eval_root / "skill-a").iterdir())
        self.assertEqual(len(remaining), 20)
        # Les 5 premiers (plus anciens) doivent avoir été supprimés
        names = [d.name for d in remaining]
        self.assertNotIn("2026-01-01-120000", names)
        self.assertNotIn("2026-01-05-120000", names)
        self.assertIn("2026-01-06-120000", names)
        self.assertIn("2026-01-25-120000", names)

    def test_eval_robuste_en_dessous_seuil_rien_supprime(self):
        self._make_eval_measurements("skill-b", 15)
        code, out, _ = run_rotate(
            "--eval-root", str(self.eval_root),
            "--history-root", str(self.history_root),
            "--keep-eval", "20",
        )
        self.assertEqual(code, 0)
        remaining = sorted((self.eval_root / "skill-b").iterdir())
        self.assertEqual(len(remaining), 15)

    def test_history_rotation_supprime_les_plus_anciens(self):
        self._make_history_reports("skill-c", 35)
        code, out, _ = run_rotate(
            "--eval-root", str(self.eval_root),
            "--history-root", str(self.history_root),
            "--keep-history", "30",
        )
        self.assertEqual(code, 0)
        remaining = sorted((self.history_root / "skill-c").iterdir())
        self.assertEqual(len(remaining), 30)

    def test_dry_run_ne_supprime_rien(self):
        self._make_eval_measurements("skill-d", 25)
        code, out, _ = run_rotate(
            "--eval-root", str(self.eval_root),
            "--history-root", str(self.history_root),
            "--keep-eval", "20",
            "--dry-run",
        )
        self.assertEqual(code, 0)
        self.assertIn("DRY-RUN", out)
        remaining = sorted((self.eval_root / "skill-d").iterdir())
        self.assertEqual(len(remaining), 25)

    def test_baseline_prefixe_underscore_preserve(self):
        """Les dossiers type _baseline-YYYY-MM-DD ne doivent jamais être supprimés."""
        skill_dir = self.eval_root / "_baseline-2026-04-12"
        skill_dir.mkdir()
        (skill_dir / "analyse.md").write_text("baseline preservee")
        code, _, _ = run_rotate(
            "--eval-root", str(self.eval_root),
            "--history-root", str(self.history_root),
            "--keep-eval", "1",
        )
        self.assertEqual(code, 0)
        self.assertTrue((skill_dir / "analyse.md").exists())

    def test_multi_skills_rotation_independante(self):
        self._make_eval_measurements("skill-x", 25)
        self._make_eval_measurements("skill-y", 15)
        code, _, _ = run_rotate(
            "--eval-root", str(self.eval_root),
            "--history-root", str(self.history_root),
            "--keep-eval", "20",
        )
        self.assertEqual(code, 0)
        self.assertEqual(len(list((self.eval_root / "skill-x").iterdir())), 20)
        self.assertEqual(len(list((self.eval_root / "skill-y").iterdir())), 15)

    def test_root_inexistant_ne_plante_pas(self):
        """rotate doit gérer l'absence du root sans erreur."""
        code, out, _ = run_rotate(
            "--eval-root", str(self.tmp_path / "inexistant"),
            "--history-root", str(self.tmp_path / "inexistant2"),
        )
        self.assertEqual(code, 0)
        self.assertIn("ignoré", out)

    def test_keep_inferieur_1_erreur(self):
        code, _, err = run_rotate(
            "--eval-root", str(self.eval_root),
            "--history-root", str(self.history_root),
            "--keep-eval", "0",
        )
        self.assertEqual(code, 1)
        self.assertIn("ERREUR", err)


if __name__ == "__main__":
    unittest.main(verbosity=2)
