#!/usr/bin/env bash
# Validation batch de tous les skills du workspace.
# Produit un tableau recapitulatif avec scores /50 et budgets tokens.
#
# Usage : bash validate-all-skills.sh [chemin-skills]
# Defaut : .claude/skills/

set -euo pipefail

SKILLS_DIR="${1:-$(dirname "$0")/../../}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CHECK_SCRIPT="$SCRIPT_DIR/check_structure.py"

if [[ ! -f "$CHECK_SCRIPT" ]]; then
    echo "Erreur : check_structure.py introuvable ($CHECK_SCRIPT)"
    exit 1
fi

# En-tete
printf "\n%-35s %6s  %-15s  %8s  %8s\n" "SKILL" "SCORE" "VERDICT" "DECOUVR." "ACTIV."
printf "%-35s %6s  %-15s  %8s  %8s\n" "-----------------------------------" "------" "---------------" "--------" "--------"

total_skills=0
total_ok=0
total_warn=0
total_fail=0

for skill_dir in "$SKILLS_DIR"/*/; do
    # Ignorer les dossiers sans SKILL.md
    [[ -f "$skill_dir/SKILL.md" ]] || continue

    skill_name=$(basename "$skill_dir")
    total_skills=$((total_skills + 1))

    # Executer check_structure.py en JSON
    json_output=$(python3 "$CHECK_SCRIPT" "$skill_dir" --json 2>/dev/null || true)

    if [[ -z "$json_output" ]]; then
        printf "%-35s %6s  %-15s  %8s  %8s\n" "$skill_name" "ERR" "Erreur script" "-" "-"
        total_fail=$((total_fail + 1))
        continue
    fi

    # Extraire les valeurs du JSON
    score=$(echo "$json_output" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['score_structurel'])" 2>/dev/null || echo "?")
    critiques=$(echo "$json_output" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['critiques'])" 2>/dev/null || echo "0")

    # Extraire les budgets tokens des messages INFO/WARNING
    discovery_tokens=$(echo "$json_output" | python3 -c "
import sys, json, re
d = json.load(sys.stdin)
for section in d.get('details', {}).values():
    for c in section.get('checks', []):
        m = re.search(r'Budget découverte.*?~(\d+) tokens', c.get('message', ''))
        if m: print(m.group(1)); sys.exit()
print('-')
" 2>/dev/null || echo "-")

    activation_tokens=$(echo "$json_output" | python3 -c "
import sys, json, re
d = json.load(sys.stdin)
for section in d.get('details', {}).values():
    for c in section.get('checks', []):
        m = re.search(r'Budget activation.*?~(\d+) tokens', c.get('message', ''))
        if m: print(m.group(1)); sys.exit()
print('-')
" 2>/dev/null || echo "-")

    # Verdict
    if [[ "$score" == "?" ]]; then
        verdict="Erreur"
        total_fail=$((total_fail + 1))
    elif [[ "$critiques" -gt 0 ]]; then
        verdict="Critique"
        total_fail=$((total_fail + 1))
    elif [[ "$score" -ge 45 ]]; then
        verdict="Conforme"
        total_ok=$((total_ok + 1))
    elif [[ "$score" -ge 35 ]]; then
        verdict="Acceptable"
        total_warn=$((total_warn + 1))
    elif [[ "$score" -ge 25 ]]; then
        verdict="Non conforme"
        total_fail=$((total_fail + 1))
    else
        verdict="Rejet"
        total_fail=$((total_fail + 1))
    fi

    # Marquer les depassements de budget tokens
    disc_display="$discovery_tokens"
    activ_display="$activation_tokens"
    [[ "$discovery_tokens" != "-" && "$discovery_tokens" -gt 150 ]] 2>/dev/null && disc_display="${discovery_tokens}!"
    [[ "$activation_tokens" != "-" && "$activation_tokens" -gt 5000 ]] 2>/dev/null && activ_display="${activation_tokens}!"

    printf "%-35s %4s/50  %-15s  %8s  %8s\n" "$skill_name" "$score" "$verdict" "$disc_display" "$activ_display"
done

# Resume
printf "\n%-35s\n" "==================================="
printf "Total : %d skills | Conformes : %d | Acceptables : %d | Echecs : %d\n\n" \
    "$total_skills" "$total_ok" "$total_warn" "$total_fail"
