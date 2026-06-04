from googletrans import Translator
import re

translator = Translator()

def tr(text):
    """Translate Russian → English safely"""
    if not text:
        return ""
    return translator.translate(text, dest="en").text


def parse_match(block):
    lines = block.strip().split("\n")

    # Match header
    match_id = lines[0]
    players = lines[1].replace("#", "").split(" - ")

    player1 = tr(players[0].strip())
    player2 = tr(players[1].strip())

    odds = []
    bets = []
    score = ""

    for line in lines[2:]:
        if "П1/П2" in line:
            odds.append(line)
        elif "F " in line or "F_Yes" in line or "B" in line or "R" in line:
            odds.append(line)
        elif re.match(r"^\d+\.", line):
            bets.append(line)
        elif ":" in line and "(" in line:
            score = line
        elif "Lines" in line or "/" in line:
            odds.append(line)

    # OUTPUT FORMAT
    output = []
    output.append(f"Player one: {player1}")
    output.append(f"Player two: {player2}\n")

    output.append("Odds")
    output.extend(odds)
    output.append("\nGames Win?\n")

    output.extend(bets)
    output.append("\nScore Progress:\n")
    output.append(score)

    return "\n".join(output)


def main():
    with open("match.txt", "r", encoding="utf-8") as f:
        content = f.read()

    # split matches
    blocks = re.findall(r"(^#N\d+.*?)(?=^#N\d+|\Z)", content, re.MULTILINE | re.DOTALL)

    print(f"{len(blocks)} match code found\n")

    for b in blocks:
        result = parse_match(b)
        print("=" * 50)
        print(result)
        print("=" * 50)


if __name__ == "__main__":
    main()