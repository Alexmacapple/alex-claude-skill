#!/usr/bin/env python3
"""Utilitaire de metriques textuelles pour Chain-of-Density.

Compatible Python 3.9+. Aucune dependance externe.

Usage :
    echo "votre texte" | python3 text_metrics.py words
    python3 text_metrics.py chars "votre texte"
    python3 text_metrics.py bytes "votre texte"
    python3 text_metrics.py metrics "votre texte"
"""

import sys
import json


def count_words(text):
    """Compte les mots d'un texte (separation par espaces)."""
    words = text.split()
    return len(words)


def count_chars(text):
    """Compte les caracteres d'un texte (espaces inclus)."""
    return len(text)


def count_bytes(text):
    """Compte les octets d'un texte (encodage UTF-8)."""
    return len(text.encode("utf-8"))


def compute_metrics(text):
    """Calcule toutes les metriques d'un texte."""
    return {
        "words": count_words(text),
        "chars": count_chars(text),
        "bytes": count_bytes(text),
    }


def read_input(args):
    """Lit le texte depuis les arguments ou stdin."""
    if len(args) > 0:
        return " ".join(args)
    else:
        return sys.stdin.read()


def main():
    if len(sys.argv) < 2:
        print("Usage: text_metrics.py <words|chars|bytes|metrics> [texte]", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    if command in ("--help", "-h", "help"):
        print("Usage: text_metrics.py <commande> [texte]")
        print()
        print("Commandes :")
        print("  words    Compte les mots (separation par espaces)")
        print("  chars    Compte les caracteres (espaces inclus)")
        print("  bytes    Compte les octets (encodage UTF-8)")
        print("  metrics  Affiche toutes les metriques en JSON")
        print()
        print("Le texte peut etre passe en argument ou via stdin.")
        print("Convention : un mot = toute sequence separee par des espaces.")
        sys.exit(0)

    text = read_input(sys.argv[2:]).strip()

    if not text:
        print("Erreur : aucun texte fourni.", file=sys.stderr)
        sys.exit(1)

    if command == "words":
        print(count_words(text))
    elif command == "chars":
        print(count_chars(text))
    elif command == "bytes":
        print(count_bytes(text))
    elif command == "metrics":
        print(json.dumps(compute_metrics(text), ensure_ascii=False))
    else:
        print("Commande inconnue : {}".format(command), file=sys.stderr)
        print("Commandes disponibles : words, chars, bytes, metrics", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
