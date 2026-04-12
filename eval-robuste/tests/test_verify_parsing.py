#!/usr/bin/env python3
"""Tests déterministes pour verify_parsing.py (PRD-098 invariant 2)."""

import unittest
from pathlib import Path
import sys

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import verify_parsing  # noqa: E402


class TestVerifyParsing(unittest.TestCase):

    def test_match_exact_une_ligne(self):
        ok, score, msg = verify_parsing.verify("SCORE: 92/100")
        self.assertTrue(ok)
        self.assertEqual(score, 92)
        self.assertEqual(msg, "OK 92")

    def test_match_apres_chain_of_thought(self):
        """L'agent peut raisonner avant, seule la dernière ligne compte."""
        raw = (
            "Je vais évaluer le skill...\n"
            "Grille appliquée, critères pondérés.\n"
            "SCORE: 88/100\n"
        )
        ok, score, _ = verify_parsing.verify(raw)
        self.assertTrue(ok)
        self.assertEqual(score, 88)

    def test_score_limite_basse(self):
        ok, score, _ = verify_parsing.verify("SCORE: 0/100")
        self.assertTrue(ok)
        self.assertEqual(score, 0)

    def test_score_limite_haute(self):
        ok, score, _ = verify_parsing.verify("SCORE: 100/100")
        self.assertTrue(ok)
        self.assertEqual(score, 100)

    def test_accepte_score_minuscule(self):
        """P2 : « Score: 92/100 » accepté (case-insensitive)."""
        ok, score, _ = verify_parsing.verify("Score: 92/100")
        self.assertTrue(ok)
        self.assertEqual(score, 92)

    def test_accepte_score_global_format(self):
        """P2 : « Score global : 92/100 » accepté (format skill-review brut)."""
        ok, score, _ = verify_parsing.verify("Score global : 88/100")
        self.assertTrue(ok)
        self.assertEqual(score, 88)

    def test_accepte_whitespaces_autour(self):
        """P2 : whitespace autour du score toléré."""
        ok, score, _ = verify_parsing.verify("  SCORE  :  92 / 100  ")
        self.assertTrue(ok)
        self.assertEqual(score, 92)

    def test_rejet_score_hors_borne(self):
        ok, score, msg = verify_parsing.verify("SCORE: 150/100")
        self.assertFalse(ok)
        self.assertIn("hors [0, 100]", msg)

    def test_rejet_output_vide(self):
        ok, _, msg = verify_parsing.verify("")
        self.assertFalse(ok)
        self.assertIn("vide", msg)

    def test_accepte_trailing_text_court(self):
        """P2 : politesse après SCORE tolérée (fenêtre de 3 dernières lignes)."""
        raw = "SCORE: 92/100\n\nMerci !\n"
        ok, score, _ = verify_parsing.verify(raw)
        self.assertTrue(ok)
        self.assertEqual(score, 92)

    def test_rejet_trailing_text_trop_long(self):
        """P2 : plus de 3 lignes après SCORE → hors fenêtre → rejet."""
        raw = "SCORE: 92/100\nLigne A\nLigne B\nLigne C\nLigne D\n"
        ok, score, _ = verify_parsing.verify(raw)
        self.assertFalse(ok)
        self.assertIsNone(score)

    def test_accepte_apres_chain_of_thought_long(self):
        """P2 : chain-of-thought long avant SCORE, dernière ligne match."""
        raw = (
            "Analyse détaillée du skill...\n"
            "Je passe en revue les 7 critères...\n"
            "Frontmatter OK, workflow clair, exemples concrets...\n"
            "SCORE: 88/100"
        )
        ok, score, _ = verify_parsing.verify(raw)
        self.assertTrue(ok)
        self.assertEqual(score, 88)


if __name__ == "__main__":
    unittest.main(verbosity=2)
