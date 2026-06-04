import re

def extract_blocks(content):
    pattern = r"(^#N\d+.*?)(?=^#N\d+|\Z)"
    return re.findall(pattern, content, re.MULTILINE | re.DOTALL)

def parse_match(block):
    lines = [l.strip() for l in block.splitlines() if l.strip()]

    match_id_line = lines[0]

    teams_line = lines[1] if len(lines) > 1 else ""
    teams = teams_line.replace("#", "").split("-")
    player1 = teams[0].strip() if len(teams) > 0 else "Unknown"
    player2 = teams[1].strip() if len(teams) > 1 else "Unknown"

    odds_line = next((l for l in lines if "P1/P2" in l), "")
    lines_data = next((l for l in lines if re.match(r"^\d+(\.\d+)?(/\d+(\.\d+)?)*$", l)), "")
    score_line = next((l for l in lines if "(" in l and ":" in l), "")

    start = lines.index(odds_line) + 1 if odds_line in lines else 0
    end = lines.index(score_line) if score_line in lines else len(lines)
    predictions = lines[start:end]

    return f"""
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


def main():
    with open("match.txt", "r", encoding="utf-8") as f:
        content = f.read()

    blocks = extract_blocks(content)

    print("Read: True")
    print(f"{len(blocks)} match code found")

    match_id = input("Enter match id (example N215): ").strip()
    if not match_id.startswith("#"):
        match_id = "#" + match_id

    for block in blocks:
        if block.startswith(match_id):
            result = parse_match(block)
            print("\n=== MATCH EXPORT ===\n")
            print(result)
            return

    print("Match not found")


if __name__ == "__main__":
    main()