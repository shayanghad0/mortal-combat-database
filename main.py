import re

def extract_blocks(content):
    pattern = r"(^#N\d+.*?)(?=^#N\d+|\Z)"
    return re.findall(pattern, content, re.MULTILINE | re.DOTALL)

def parse_match(block):
    lines = [l.strip() for l in block.splitlines() if l.strip()]

    # Match ID line
    match_id_line = lines[0]

    # Teams line
    teams_line = lines[1] if len(lines) > 1 else ""
    teams = teams_line.replace("#", "").split("-")
    player1 = teams[0].strip() if len(teams) > 0 else "Unknown"
    player2 = teams[1].strip() if len(teams) > 1 else "Unknown"

    # Odds line (find line containing P1/P2)
    odds_line = next((l for l in lines if "P1/P2" in l), "")

    # Lines (numbers like 28.5/34.5)
    lines_data = next((l for l in lines if re.match(r"^\d+(\.\d+)?(/\d+(\.\d+)?)*$", l)), "")

    # Score line (last bracket line usually)
    score_line = next((l for l in lines if "(" in l and ":" in l), "")

    # Predictions (between odds and score)
    try:
        start = lines.index(odds_line) + 1
        end = lines.index(score_line) if score_line in lines else len(lines)
        predictions = lines[start:end]
    except:
        predictions = []

    formatted = f"""
Player one: {player1}
Player two: {player2}

Odds
{odds_line}
{next((l for l in lines if "F 3." in l), "")}
{next((l for l in lines if "F_Yes" in l or "F Yes" in l), "")}
Lines: {lines_data}

Games Win?

""" + "\n".join(predictions) + f"""

Score Progress:

{score_line}
""".strip()

    return formatted


def main():
    with open("match.txt", "r", encoding="utf-8") as f:
        content = f.read()

    blocks = extract_blocks(content)

    print(f"Read: True")
    print(f"{len(blocks)} match code found")

    match_id = input("Enter match id (example N215): ").strip()

    if not match_id.startswith("#"):
        match_id = "#" + match_id

    for block in blocks:
        if block.startswith(match_id):
            result = parse_match(block)

            with open(f"{match_id.replace('#','')}_export.txt", "w", encoding="utf-8") as f:
                f.write(result)

            print("Export Done")
            print(result)
            return

    print("Match not found")


if __name__ == "__main__":
    main()