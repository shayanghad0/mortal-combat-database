from googletrans import Translator
import re

translator = Translator()

def normalize(text):
    return translator.translate(text, dest="en").text


def extract_match(content, match_id):
    pattern = r"(^#N\d+.*?)(?=^#N\d+|\Z)"
    blocks = re.findall(pattern, content, re.MULTILINE | re.DOTALL)

    for b in blocks:
        if b.startswith(match_id):
            return b
    return None


def parse_block(block):
    lines = [l.strip() for l in block.split("\n") if l.strip()]

    # header
    header = lines[0]
    match = re.search(r"#N\d+\.\s*(.*?)\s*-\s*(.*)", header)

    player1_ru = match.group(1).replace("#", "").strip()
    player2_ru = match.group(2).replace("#", "").strip()

    player1 = normalize(player1_ru)
    player2 = normalize(player2_ru)

    # odds + lines
    odds = lines[3]
    fbr = lines[4]
    yesno = lines[5]
    lines_data = lines[6]

    # bets section
    bets_start = 7
    bets = []
    i = 1

    for line in lines[bets_start:]:
        if line.startswith("2:") or "(" in line:
            break
        bets.append(f"{i}. {line}")
        i += 1

    # score
    score_line = [l for l in lines if ":" in l and "(" in l]
    score = score_line[0] if score_line else ""

    return f"""
Player one: {player1}
Player two: {player2}

Odds
{odds}
{fbr}
{yesno}
Lines: {lines_data}

Games Win?

{chr(10).join(bets)}

Score Progress:
{score}
""".strip()


def main():
    with open("match.txt", "r", encoding="utf-8") as f:
        content = f.read()

    print("Read: True")

    match_id = input("Enter match id (example #N215): ").strip()

    block = extract_match(content, match_id)

    if not block:
        print("Match not found")
        return

    result = parse_block(block)

    filename = match_id.replace("#", "") + "_export.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(result)

    print("Export done:", filename)


if __name__ == "__main__":
    main()