#!/usr/bin/env python3
"""
Validation structurelle d'un SKILL.md selon les standards Anthropic.
Partie programmatique (déterministe) du skill-conformity-checker.

Score sur 65 points :
- Frontmatter Anthropic (S01-S07) : 20 pts
- Structure du body (S08-S13) : 20 pts
- Ressources (S14-S15) : 10 pts
- Critères empiriques SkillsBench (S16-S20) : 15 pts

Chaque critère est vérifié par parsing, pas par LLM.
Inclut des mesures de budget tokens (informatif, hors barème).

Référence SkillsBench : arXiv:2602.12670v1 (février 2026).
Basé sur SkillsBench guidelines-skills.md.
"""

import sys
import os
import re
import json
import argparse
import yaml

def estimate_tokens(text):
    """Estime le nombre de tokens d'un texte (approximation : 1 token ~ 4 caractères)."""
    return len(text) // 4


def load_skill(path):
    """Charge un SKILL.md et sépare frontmatter / body."""
    if not os.path.isfile(path):
        return None, None, f"Fichier introuvable : {path}"

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extraire le frontmatter YAML
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not fm_match:
        return None, content, None

    try:
        frontmatter = yaml.safe_load(fm_match.group(1))
    except yaml.YAMLError as e:
        return None, content, f"Erreur YAML : {e}"

    body = content[fm_match.end():]
    return frontmatter, body, None


def check_frontmatter(fm, skill_dir):
    """Vérifie le frontmatter YAML. Max 20 points."""
    results = []
    score = 0

    if fm is None:
        results.append(("CRITIQUE", 0, 20, "Frontmatter YAML absent ou invalide (délimiteurs --- manquants)"))
        return score, results

    # S01 : Frontmatter présent (3 pts)
    results.append(("OK", 3, 3, "Frontmatter YAML présent avec délimiteurs ---"))
    score += 3

    # S02 : name kebab-case (5 pts)
    name = fm.get("name", "")
    name_valid = False
    if not name:
        results.append(("CRITIQUE", 0, 5, "Champ 'name' absent"))
    elif " " in str(name):
        results.append(("CRITIQUE", 0, 5, f"Champ 'name' contient des espaces : '{name}'"))
    elif not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", str(name)):
        results.append(("MAJEUR", 0, 5, f"Champ 'name' non kebab-case : '{name}'"))
    else:
        results.append(("OK", 5, 5, f"name = '{name}' (kebab-case valide)"))
        score += 5
        name_valid = True

    # S15 : name == nom du dossier (2 pts)
    if name_valid:
        dir_name = os.path.basename(skill_dir.rstrip("/"))
        if str(name) == dir_name:
            results.append(("OK", 2, 2, f"name '{name}' identique au nom du dossier"))
            score += 2
        else:
            results.append(("MINEUR", 0, 2, f"'name' ({name}) != nom du dossier ({dir_name})"))
    else:
        results.append(("MINEUR", 0, 2, "S15 non évalué (name invalide)"))

    # Description (8 pts)
    desc = fm.get("description", "")
    if not desc:
        results.append(("CRITIQUE", 0, 8, "Champ 'description' absent"))
    else:
        desc_str = str(desc)
        desc_score = 0

        if len(desc_str) > 1024:
            results.append(("MAJEUR", 0, 2, f"Description trop longue ({len(desc_str)} car. > 1024)"))
        elif len(desc_str) > 250:
            desc_score += 1
            results.append(("MINEUR", 1, 2, f"Description dépasse 250 car. ({len(desc_str)} car.) — tronquée dans le menu /skills"))
        else:
            desc_score += 2

        if "<" in desc_str or ">" in desc_str:
            results.append(("CRITIQUE", 0, 2, "Chevrons XML (< >) détectés dans la description"))
        else:
            desc_score += 2

        # Vérifier présence de triggers (mots-clés d'activation)
        trigger_patterns = [
            r"(?i)(use when|utiliser quand|when user|quand l.utilisateur)",
            r"(?i)(trigger|déclenche|déclench|activ)",
            r'(?i)(ask|demand|dit|says|mention)',
        ]
        has_trigger = any(re.search(p, desc_str) for p in trigger_patterns)
        if has_trigger:
            desc_score += 2
            results.append(("OK", 2, 2, "Description contient des conditions de déclenchement"))
        else:
            results.append(("MAJEUR", 0, 2, "Description sans conditions de déclenchement (quand utiliser)"))

        # Longueur minimale
        if len(desc_str) < 30:
            results.append(("MAJEUR", 0, 2, f"Description trop courte ({len(desc_str)} car.)"))
        else:
            desc_score += 2
            results.append(("OK", 2, 2, f"Description de longueur adéquate ({len(desc_str)} car.)"))

        score += desc_score

    # Noms réservés (2 pts)
    name_str = str(fm.get("name", "")).lower()
    if "claude" in name_str or "anthropic" in name_str:
        results.append(("CRITIQUE", 0, 2, f"Nom réservé détecté : '{name_str}' (claude/anthropic interdit)"))
    else:
        results.append(("OK", 2, 2, "Pas de nom réservé"))
        score += 2

    # S16a : Budget tokens de découverte (informatif, hors barème)
    if desc:
        discovery_text = f"{fm.get('name', '')} {desc}"
        discovery_tokens = estimate_tokens(discovery_text)
        if discovery_tokens > 150:
            results.append(("WARNING", 0, 0, f"Budget découverte élevé : ~{discovery_tokens} tokens (recommandé : < 150). Réduire la description."))
        else:
            results.append(("INFO", 0, 0, f"Budget découverte : ~{discovery_tokens} tokens (< 150 OK)"))

    return score, results


def check_structure(body, skill_dir):
    """Vérifie la structure du body Markdown. Max 20 points."""
    results = []
    score = 0

    if not body or not body.strip():
        results.append(("CRITIQUE", 0, 20, "Corps du SKILL.md vide"))
        return score, results

    lines = body.strip().split("\n")

    # H1 unique (3 pts)
    h1_count = len(re.findall(r"^# .+", body, re.MULTILINE))
    if h1_count == 0:
        results.append(("MAJEUR", 0, 3, "Aucun titre H1 trouvé"))
    elif h1_count == 1:
        results.append(("OK", 3, 3, "Titre H1 unique"))
        score += 3
    else:
        results.append(("MINEUR", 1, 3, f"{h1_count} titres H1 (1 seul recommandé)"))
        score += 1

    # Sections H2 présentes (5 pts)
    h2_sections = re.findall(r"^## (.+)", body, re.MULTILINE)
    if len(h2_sections) == 0:
        results.append(("MAJEUR", 0, 5, "Aucune section H2 trouvée"))
    elif len(h2_sections) < 2:
        results.append(("MINEUR", 2, 5, f"Seulement {len(h2_sections)} section(s) H2"))
        score += 2
    else:
        results.append(("OK", 5, 5, f"{len(h2_sections)} sections H2 : {', '.join(h2_sections[:6])}"))
        score += 5

    # Longueur viable (4 pts)
    line_count = len(lines)
    if line_count < 20:
        results.append(("MAJEUR", 0, 4, f"Corps trop court ({line_count} lignes < 20 minimum)"))
    elif line_count > 500:
        results.append(("MINEUR", 2, 4, f"Corps très long ({line_count} lignes > 500 recommandé)"))
        score += 2
    else:
        results.append(("OK", 4, 4, f"Longueur adéquate ({line_count} lignes)"))
        score += 4

    # Exemples ou blocs de code (4 pts)
    code_blocks = len(re.findall(r"```", body))
    if code_blocks >= 2:
        results.append(("OK", 4, 4, f"{code_blocks // 2} bloc(s) de code trouvés"))
        score += 4
    elif code_blocks >= 1:
        results.append(("MINEUR", 2, 4, "Un seul bloc de code (exemples recommandés)"))
        score += 2
    else:
        results.append(("MINEUR", 0, 4, "Aucun bloc de code ni exemple"))

    # Pas de README.md dans le dossier (4 pts)
    readme_path = os.path.join(skill_dir, "README.md")
    if os.path.isfile(readme_path):
        results.append(("MAJEUR", 0, 4, "README.md présent dans le dossier (interdit par Anthropic)"))
    else:
        results.append(("OK", 4, 4, "Pas de README.md dans le dossier"))
        score += 4

    # S16b : Budget tokens d'activation (informatif, hors barème)
    skill_file = os.path.join(skill_dir, "SKILL.md")
    if os.path.isfile(skill_file):
        with open(skill_file, "r", encoding="utf-8") as f:
            full_content = f.read()
        activation_tokens = estimate_tokens(full_content)
        if activation_tokens > 5000:
            results.append(("WARNING", 0, 0, f"Budget activation élevé : ~{activation_tokens} tokens (recommandé : < 5000). Externaliser en references/."))
        else:
            results.append(("INFO", 0, 0, f"Budget activation : ~{activation_tokens} tokens (< 5000 OK)"))

    return score, results


def check_resources(skill_dir):
    """Vérifie les ressources bundled. Max 10 points."""
    results = []
    score = 0

    # Fichier SKILL.md exact (3 pts)
    skill_file = os.path.join(skill_dir, "SKILL.md")
    if os.path.isfile(skill_file):
        results.append(("OK", 3, 3, "Fichier SKILL.md présent (casse exacte)"))
        score += 3
    else:
        # Vérifier les variantes
        variants = ["skill.md", "SKILL.MD", "Skill.md"]
        found = [v for v in variants if os.path.isfile(os.path.join(skill_dir, v))]
        if found:
            results.append(("CRITIQUE", 0, 3, f"Fichier mal nommé : {found[0]} (doit être SKILL.md)"))
        else:
            results.append(("CRITIQUE", 0, 3, "Fichier SKILL.md absent"))

    # Dossier en kebab-case (3 pts)
    dir_name = os.path.basename(skill_dir.rstrip("/"))
    if re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", dir_name):
        results.append(("OK", 3, 3, f"Dossier en kebab-case : {dir_name}"))
        score += 3
    else:
        results.append(("MAJEUR", 0, 3, f"Dossier non kebab-case : {dir_name}"))

    # Liens references/ existants (4 pts)
    body_path = os.path.join(skill_dir, "SKILL.md")
    if os.path.isfile(body_path):
        with open(body_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Retirer les blocs de code avant de chercher les liens
        content_no_codeblocks = re.sub(r"```.*?```", "", content, flags=re.DOTALL)

        # Chercher les liens relatifs (hors blocs de code)
        links = re.findall(r"\[.*?\]\(((?!http)[^)]+)\)", content_no_codeblocks)
        broken = []
        for link in links:
            full_path = os.path.join(skill_dir, link)
            if not os.path.exists(full_path):
                broken.append(link)

        if links and not broken:
            results.append(("OK", 4, 4, f"{len(links)} lien(s) relatif(s), tous valides"))
            score += 4
        elif broken:
            results.append(("MAJEUR", 1, 4, f"Lien(s) cassé(s) : {', '.join(broken)}"))
            score += 1
        else:
            results.append(("INFO", 4, 4, "Aucun lien relatif (acceptable)"))
            score += 4

    return score, results


def check_skillsbench(body):
    """Vérifie les critères empiriques SkillsBench (S16-S20). Max 15 points.

    Référence : arXiv:2602.12670v1 (Li et al., février 2026).
    Ces critères ne remplacent pas S01-S15 mais s'ajoutent pour durcir
    la qualité des skills générés et audités.
    """
    results = []
    score = 0

    if not body or not body.strip():
        results.append(("CRITIQUE", 0, 15, "Corps du SKILL.md vide — critères SkillsBench non évaluables"))
        return score, results

    lines = body.strip().split("\n")
    line_count = len(lines)

    # S16 : Corps ≤ 300 lignes (cible empirique SkillsBench) (3 pts)
    # SkillsBench Finding 6 : Skills exhaustifs (> 3000 tokens) = -2,9 pp
    # Cible pragmatique : 300 lignes ~ 1500-2500 tokens
    if line_count <= 300:
        results.append(("OK", 3, 3, f"S16 Cible SkillsBench respectée ({line_count} lignes ≤ 300)"))
        score += 3
    elif line_count <= 400:
        results.append(("MINEUR", 1, 3, f"S16 Dépasse la cible SkillsBench ({line_count} lignes, cible 300)"))
        score += 1
    else:
        results.append(("MINEUR", 0, 3, f"S16 Corps trop long ({line_count} lignes > 400) — SkillsBench : < 300"))

    # S17 : Section Checklist ET >=2 items (3 pts)
    # SkillsBench : réduit les Incomplete Solution failures (10,2 % des échecs)
    has_checklist_section = bool(re.search(r"(?mi)^## .*(checklist|check.?list)", body))
    checkbox_items = len(re.findall(r"^\s*-\s*\[\s*\]", body, re.MULTILINE))

    if has_checklist_section and checkbox_items >= 2:
        results.append(("OK", 3, 3, f"S17 Section Checklist présente avec {checkbox_items} items"))
        score += 3
    elif has_checklist_section or checkbox_items >= 2:
        partial = "section titrée sans items" if has_checklist_section else f"{checkbox_items} items sans section titrée"
        results.append(("MAJEUR", 1, 3, f"S17 Checklist partielle ({partial})"))
        score += 1
    else:
        results.append(("MAJEUR", 0, 3, "S17 Aucune section Checklist ni items '- [ ]' (risque Incomplete Solution)"))

    # S18 : Section "Pièges" / "Pitfalls" / "Conventions" (2 pts)
    # SkillsBench : réduit les Quality Below Threshold failures (49,8 % des échecs)
    has_pitfalls_section = bool(re.search(
        r"(?mi)^## .*(piège|pitfall|convention|gotcha|piéger|erreur courante)",
        body
    ))
    if has_pitfalls_section:
        results.append(("OK", 2, 2, "S18 Section Pièges/Pitfalls/Conventions présente"))
        score += 2
    else:
        results.append(("MINEUR", 0, 2, "S18 Aucune section Pièges documentés (risque Quality Below Threshold)"))

    # S19 : Guidance négative (>=1 occurrence) (3 pts)
    # SkillsBench : réduit les Specification Violation failures (3,3 % des échecs)
    negative_patterns = [
        r"\bNE PAS\b",
        r"\bJAMAIS\b",
        r"\bNe pas utiliser\b",
        r"\bNe jamais\b",
        r"(?i)\bDo NOT\b",
        r"(?i)\bnever\b",
        r"(?i)\bavoid\b",
        r"\bhors périmètre\b",
        r"\bhors perimetre\b",
    ]
    neg_count = sum(len(re.findall(p, body)) for p in negative_patterns)
    if neg_count >= 3:
        results.append(("OK", 3, 3, f"S19 Guidance négative forte ({neg_count} occurrences)"))
        score += 3
    elif neg_count >= 1:
        results.append(("MAJEUR", 2, 3, f"S19 Guidance négative faible ({neg_count} occurrence) — viser ≥ 3"))
        score += 2
    else:
        results.append(("MAJEUR", 0, 3, "S19 Aucune guidance négative (NE PAS/JAMAIS/hors périmètre)"))

    # S20 : Section Exemple avec bloc de code (4 pts)
    # SkillsBench Discussion §5 : exemples > documentation exhaustive
    has_example_section = bool(re.search(r"(?mi)^## .*(exemple|example)", body))
    code_blocks = len(re.findall(r"```", body))

    if has_example_section and code_blocks >= 2:
        results.append(("OK", 4, 4, f"S20 Section Exemple présente + {code_blocks // 2} bloc(s) de code"))
        score += 4
    elif has_example_section:
        results.append(("MAJEUR", 2, 4, "S20 Section Exemple présente sans bloc de code ''' '''"))
        score += 2
    elif code_blocks >= 2:
        results.append(("MAJEUR", 2, 4, "S20 Blocs de code présents sans section Exemple titrée"))
        score += 2
    else:
        results.append(("MAJEUR", 0, 4, "S20 Aucun exemple end-to-end (section Exemple + bloc de code)"))

    return score, results


def generate_report(skill_path, fm_score, fm_results, struct_score, struct_results, res_score, res_results, sb_score, sb_results):
    """Génère le rapport de conformité structurelle."""
    total = fm_score + struct_score + res_score + sb_score
    max_total = 65  # Sur 65 : Anthropic (50) + SkillsBench (15)

    # Compteurs
    all_results = fm_results + struct_results + res_results + sb_results
    critiques = sum(1 for r in all_results if r[0] == "CRITIQUE")
    majeurs = sum(1 for r in all_results if r[0] == "MAJEUR")
    mineurs = sum(1 for r in all_results if r[0] == "MINEUR")
    ok_count = sum(1 for r in all_results if r[0] == "OK")

    # Verdict selon seuils proportionnels (ex-/50 × 1,3 = /65)
    if total >= 58:
        verdict = "Conforme"
    elif total >= 45:
        verdict = "Acceptable"
    elif total >= 32:
        verdict = "Non conforme"
    else:
        verdict = "Rejet"

    report = {
        "skill_path": skill_path,
        "score_structurel": total,
        "score_max": max_total,
        "verdict": verdict,
        "critiques": critiques,
        "majeurs": majeurs,
        "mineurs": mineurs,
        "conformes": ok_count,
        "details": {
            "frontmatter": {"score": fm_score, "max": 20, "checks": [{"severity": r[0], "pts": r[1], "max": r[2], "message": r[3]} for r in fm_results]},
            "structure": {"score": struct_score, "max": 20, "checks": [{"severity": r[0], "pts": r[1], "max": r[2], "message": r[3]} for r in struct_results]},
            "ressources": {"score": res_score, "max": 10, "checks": [{"severity": r[0], "pts": r[1], "max": r[2], "message": r[3]} for r in res_results]},
            "skillsbench": {"score": sb_score, "max": 15, "checks": [{"severity": r[0], "pts": r[1], "max": r[2], "message": r[3]} for r in sb_results]},
        }
    }

    return report


def print_report(report):
    """Affiche le rapport en format lisible."""
    total = report["score_structurel"]
    max_t = report["score_max"]

    print(f"\n{'='*60}")
    print(f"  RAPPORT DE CONFORMITÉ STRUCTURELLE")
    print(f"  Skill : {report['skill_path']}")
    print(f"{'='*60}")
    print(f"\n  Score structurel : {total}/{max_t} — {report['verdict']}")
    print(f"  Critiques : {report['critiques']} | Majeurs : {report['majeurs']} | Mineurs : {report['mineurs']} | Conformes : {report['conformes']}")

    for section_name, section in report["details"].items():
        print(f"\n  --- {section_name.upper()} ({section['score']}/{section['max']}) ---")
        for check in section["checks"]:
            icon = {"OK": "V", "CRITIQUE": "X", "MAJEUR": "!", "MINEUR": "~", "INFO": "i", "WARNING": "W"}
            print(f"    [{icon.get(check['severity'], '?')}] {check['severity']:8s} ({check['pts']}/{check['max']}) {check['message']}")

    print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        prog="check_structure.py",
        description="Validation structurelle d'un SKILL.md selon les standards Anthropic + critères empiriques SkillsBench. Score sur 65 points.",
        epilog="Codes de sortie : 0 = conforme/acceptable, 1 = score < 40, 2 = erreur(s) critique(s)."
    )
    parser.add_argument(
        "path",
        help="Chemin vers le dossier du skill ou vers le fichier SKILL.md"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Sortie au format JSON au lieu du rapport lisible"
    )

    args = parser.parse_args()
    path = args.path

    # Déterminer le dossier et le fichier SKILL.md
    if os.path.isfile(path) and os.path.basename(path) == "SKILL.md":
        skill_dir = os.path.dirname(path) or "."
        skill_file = path
    elif os.path.isdir(path):
        skill_dir = path
        skill_file = os.path.join(path, "SKILL.md")
    else:
        print(f"Erreur : '{path}' n'est ni un dossier ni un SKILL.md")
        sys.exit(1)

    # Charger et analyser
    fm, body, error = load_skill(skill_file)
    if error and fm is None and body is None:
        print(f"Erreur : {error}")
        sys.exit(1)

    # Exécuter les checks
    fm_score, fm_results = check_frontmatter(fm, skill_dir)
    struct_score, struct_results = check_structure(body, skill_dir)
    res_score, res_results = check_resources(skill_dir)
    sb_score, sb_results = check_skillsbench(body)

    # Générer le rapport
    report = generate_report(skill_dir, fm_score, fm_results, struct_score, struct_results, res_score, res_results, sb_score, sb_results)

    if args.json_output:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_report(report)

    # Code de sortie (seuil proportionnel 30/50 → 40/65)
    if report["critiques"] > 0:
        sys.exit(2)
    elif report["score_structurel"] < 40:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
