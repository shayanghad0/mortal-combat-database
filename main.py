import re

def extract_blocks(content):
    pattern = r"(^#N\d+.*?)(?=^#N\d+|\Z)"
    return re.findall(pattern, content, re.MULTILINE | re.DOTALL)


def transliterate_ru_to_en(text: str) -> str:
    if not text:
        return text
    mapping = {
        'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'yo','ж':'zh','з':'z','и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'kh','ц':'ts','ч':'ch','ш':'sh','щ':'shch','ы':'y','э':'e','ю':'yu','я':'ya','ь':'','ъ':'',
    }
    result = []
    for ch in text:
        lower = ch.lower()
        if lower in mapping:
            trans = mapping[lower]
            # preserve capitalization
            if ch.isupper():
                if trans:
                    trans = trans[0].upper() + trans[1:]
            result.append(trans)
        else:
            result.append(ch)
    return ''.join(result)


def map_character_name(name: str) -> str:
    if not name:
        return name
    # normalize key: remove non-letters/digits and lowercase
    key = re.sub(r"[^\w\u0400-\u04FF]", "", name).lower()
    mapping = {
        'люкенг':'Liu Kang','эрмак':'Ermac','горо':'Goro','ферраиторр':'FerraiTorr','скорпион':'Scorpion','кожаноелицо':'Leatherface','коталькан':'Kotal Kahn','кенши':'Kenshi','чужой':'Alien','джакс':'Jax','кэссикейдж':'Cassie Cage','куанчичи':'Quan Chi','куанчич':'Quan Chi','рептилия':'Reptile','тремор':'Tremor','кунглао':'Kung Lao','такедатакахаши':'Takeda','такеда':'Takeda','сабзиро':'Sub-Zero','триборг':'Triborg','джейсонвурхиз':'Jason Voorhees','хищник':'Predator','джонникейдж':'Johnny Cage','кунгджин':'Kung Jin','эрронблэк':'Erron Black','соняблейд':'Sonya Blade','шиннок':'Shinnok','дивора':'D\'Vorah','дивора':'D\'Vorah','борaйчо':'Bo\' Rai Cho','борайчо':'Bo\' Rai Cho','джэкибрiggс':'Jacqui Briggs','джэкибрiggс':'Jacqui Briggs','джэкибрiggs':'Jacqui Briggs','милина':'Mileena','райден':'Raiden','райдэн':'Raiden','кано':'Kano','таня':'Tanya','китана':'Kitana','бойрайчо':'Bo\' Rai Cho','борaйчо':'Bo\' Rai Cho'
    }
    # try exact mapping
    if key in mapping:
        return mapping[key]
    # fallback: transliterate
    return transliterate_ru_to_en(name)

def parse_match(block):
    lines = [l.strip() for l in block.splitlines() if l.strip()]

    # Match ID line
    match_id_line = lines[0]

    # derive GameCode (e.g. N215) from the match id line
    m = re.search(r"#?([A-Za-z0-9]+)", match_id_line)
    game_code = m.group(1) if m else match_id_line.replace('#','')

    # Teams line
    teams_line = lines[1] if len(lines) > 1 else ""
    teams = teams_line.replace("#", "").split("-")
    player1 = teams[0].strip() if len(teams) > 0 else "Unknown"
    player2 = teams[1].strip() if len(teams) > 1 else "Unknown"

    # Map Russian character names to canonical English (fallback to transliteration)
    player1_en = map_character_name(player1)
    player2_en = map_character_name(player2)

    # Odds line (find line containing P1/P2 or Cyrillic П1/П2)
    odds_line = next((l for l in lines if "P1/P2" in l or "П1/П2" in l), "")

    # parse player-specific odds from the odds line (format like 'П1/П2 - 1.64/2.375')
    p1_odds = ""
    p2_odds = ""
    m_odds = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*/\s*([0-9]+(?:\.[0-9]+)?)", odds_line)
    if m_odds:
        p1_odds, p2_odds = m_odds.group(1), m_odds.group(2)

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

    # translate short betting/player codes in prediction lines
    def translate_betting_codes(s: str) -> str:
        if not s:
            return s
        repl = {
            'П1': 'Player one',
            'П2': 'Player two',
            'ТББ': 'Over (big)',
            'ТММ': 'Under (big)',
            'ТБ': 'Over',
            'ТМ': 'Under',
        }
        pattern = re.compile(r"\b(П1|П2|ТББ|ТММ|ТБ|ТМ)\b")
        return pattern.sub(lambda m: repl.get(m.group(0), m.group(0)), s)

    predictions = [translate_betting_codes(p) for p in predictions]

    formatted = f"""
{odds_line}
GameCode: {game_code}
Player one: {player1_en} {p1_odds}
Player two: {player2_en} {p2_odds}

Odds
{next((l for l in lines if "F 3." in l), "")}
{next((l for l in lines if "F_Yes" in l or "F Yes" in l), "")}

Lines: {lines_data}

Games Win?
\n
""" + "\n".join(predictions) + f"""


\nScore Progress:

{score_line}
""".strip()

    # return both formatted text and the GameCode for filename
    return formatted, game_code


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
            parsed = parse_match(block)
            # parse_match now returns (formatted, game_code)
            if isinstance(parsed, tuple):
                result_text, game_code = parsed
            else:
                result_text = parsed
                game_code = match_id.replace('#','')

            # Do not write export file to disk; print result only
            print("Export (no file):")
            print(result_text)
            return

    print("Match not found")


if __name__ == "__main__":
    main()