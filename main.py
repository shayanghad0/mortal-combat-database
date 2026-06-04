import re

import re
from typing import Optional, Dict


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
            if ch.isupper() and trans:
                trans = trans[0].upper() + trans[1:]
            result.append(trans)
        else:
            result.append(ch)
    return ''.join(result)


def map_character_name(name: str) -> str:
    if not name:
        return name
    key = re.sub(r"[^\w\u0400-\u04FF]", "", name).lower()
    mapping = {
        'люкенг':'Liu Kang','эрмак':'Ermac','горо':'Goro','ферраиторр':'FerraiTorr','скорпион':'Scorpion','кожаноелицо':'Leatherface','коталькан':'Kotal Kahn','кенши':'Kenshi','чужой':'Alien','джакс':'Jax','кэссикейдж':'Cassie Cage','куанчичи':'Quan Chi','куанчич':'Quan Chi','рептилия':'Reptile','тремор':'Tremor','кунглао':'Kung Lao','такедатакахаши':'Takeda','такеда':'Takeda','сабзиро':'Sub-Zero','триборг':'Triborg','джейсонвурхиз':'Jason Voorhees','хищник':'Predator','джонникейдж':'Johnny Cage','кунгджин':'Kung Jin','эрронблэк':'Erron Black','соняблейд':'Sonya Blade','шиннок':'Shinnok','дивора':'D\'Vorah','борaйчо':'Bo\' Rai Cho','борайчо':'Bo\' Rai Cho','джэкибрiggs':'Jacqui Briggs','милина':'Mileena','райден':'Raiden','райдэн':'Raiden','кано':'Kano','таня':'Tanya','китана':'Kitana'
    }
    if key in mapping:
        return mapping[key]
    return transliterate_ru_to_en(name)


def parse_match(block: str) -> Dict:
    lines = [l.strip() for l in block.splitlines() if l.strip()]
    match_id_line = lines[0] if lines else ""
    m = re.search(r"#?([A-Za-z0-9]+)", match_id_line)
    game_code = m.group(1) if m else match_id_line.replace('#','')

    teams_line = lines[1] if len(lines) > 1 else ""
    teams = teams_line.replace("#", "").split("-")
    raw_p1 = teams[0].strip() if len(teams) > 0 else "Unknown"
    raw_p2 = teams[1].strip() if len(teams) > 1 else "Unknown"

    player1_en = map_character_name(raw_p1)
    player2_en = map_character_name(raw_p2)

    odds_line = next((l for l in lines if "P1/P2" in l or "П1/П2" in l), "")
    p1_odds = None
    p2_odds = None
    m_odds = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*/\s*([0-9]+(?:\.[0-9]+)?)", odds_line)
    if m_odds:
        try:
            p1_odds = float(m_odds.group(1))
            p2_odds = float(m_odds.group(2))
        except:
            p1_odds = None
            p2_odds = None

    score_line = next((l for l in lines if "(" in l and ":" in l), "")
    # Predictions area
    try:
        start = lines.index(odds_line) + 1
        end = lines.index(score_line) if score_line in lines else len(lines)
        predictions = lines[start:end]
    except:
        predictions = []

    def translate_betting_codes(s: str) -> str:
        if not s:
            return s
        repl = {'П1': 'Player one', 'П2': 'Player two', 'ТББ': 'Over (big)', 'ТММ': 'Under (big)', 'ТБ': 'Over', 'ТМ': 'Under'}
        pattern = re.compile(r"\b(П1|П2|ТББ|ТММ|ТБ|ТМ)\b")
        return pattern.sub(lambda m: repl.get(m.group(0), m.group(0)), s)

    predictions = [translate_betting_codes(p) for p in predictions]

    formatted = f"{odds_line}\nGameCode: {game_code}\nPlayer one: {player1_en} {p1_odds or ''}\nPlayer two: {player2_en} {p2_odds or ''}\n\n" + "\n".join(predictions) + f"\n\nScore Progress:\n{score_line}".strip()

    return {
        'formatted': formatted,
        'game_code': game_code,
        'player1': player1_en,
        'player2': player2_en,
        'p1_odds': p1_odds,
        'p2_odds': p2_odds,
        'raw_block': block,
    }


def compare_multiplier(parsed: Optional[float], provided: float) -> str:
    if parsed is None:
        return 'no'
    eps = 1e-6
    if abs(parsed - provided) <= eps:
        return '100'
    if parsed >= 0.85 * provided:
        return '85'
    return 'no'


def normalize_for_compare(name: str) -> str:
    return map_character_name(name).strip().lower()


def main():
    with open("match.txt", "r", encoding="utf-8") as f:
        content = f.read()

    blocks = extract_blocks(content)

    print(f"Read: True")
    print(f"{len(blocks)} match code found")
    # loop so user can run multiple lookups; type 'exit' to quit
    while True:
        print("(Type 'exit' at any prompt to quit)")
        # New input sequence per request
        p1_input = input("Player one (Russian or English): ").strip()
        if p1_input.lower() in ('exit', 'quit', 'q'):
            break
        try:
            raw = input("Player one multiplier (e.g. 1.64): ").strip()
            if raw.lower() in ('exit', 'quit', 'q'):
                break
            p1_mult = float(raw)
        except:
            print("Invalid multiplier for player one")
            continue

        p2_input = input("Player two (Russian or English): ").strip()
        if p2_input.lower() in ('exit', 'quit', 'q'):
            break
        try:
            raw = input("Player two multiplier (e.g. 2.375): ").strip()
            if raw.lower() in ('exit', 'quit', 'q'):
                break
            p2_mult = float(raw)
        except:
            print("Invalid multiplier for player two")
            continue

        gid = input("Optional game ID (example 215) or leave empty: ").strip()
        if gid.lower() in ('exit', 'quit', 'q'):
            break

        norm_p1 = normalize_for_compare(p1_input)
        norm_p2 = normalize_for_compare(p2_input)

        found_any = False
        for block in blocks:
            parsed = parse_match(block)
            game_code = parsed['game_code']

            if gid:
                if gid not in game_code:
                    continue

            parsed_p1 = normalize_for_compare(parsed['player1'])
            parsed_p2 = normalize_for_compare(parsed['player2'])

            swapped = False
            if parsed_p1 == norm_p1 and parsed_p2 == norm_p2:
                swapped = False
            elif parsed_p1 == norm_p2 and parsed_p2 == norm_p1:
                swapped = True
            else:
                continue

            # if swapped, interpret multipliers accordingly
            if not swapped:
                status1 = compare_multiplier(parsed['p1_odds'], p1_mult)
                status2 = compare_multiplier(parsed['p2_odds'], p2_mult)
            else:
                status1 = compare_multiplier(parsed['p1_odds'], p2_mult)
                status2 = compare_multiplier(parsed['p2_odds'], p1_mult)

            # Decide export criteria: both 100% OR both >=85%
            both_100 = (status1 == '100' and status2 == '100')
            both_85_or_100 = (status1 in ('100','85') and status2 in ('100','85'))

            if both_100 or both_85_or_100:
                found_any = True
                label = '100%' if both_100 else '>=85%'
                print('\n--- MATCH FOUND ---')
                print(f'GameCode: {game_code}  Match type: {label}')
                print(parsed['formatted'])
                print(f"Player1 multiplier status: {status1}, Player2 multiplier status: {status2}")

        if not found_any:
            print("No matches found matching the given names/multipliers and optional game ID.")

        again = input("\nSearch again? Press Enter to continue or type 'exit' to quit: ").strip()
        if again.lower() in ('exit', 'quit', 'q'):
            break


if __name__ == "__main__":
    main()