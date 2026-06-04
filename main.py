import re

def normalize_id(x):
    x = x.strip()
    if not x.startswith("#"):
        x = "#" + x
    return x

def extract_match(content, match_id):
    match_id = normalize_id(match_id)

    pattern = r"(^#N\d+.*?)(?=^#N\d+|\Z)"
    blocks = re.findall(pattern, content, re.MULTILINE | re.DOTALL)

    for block in blocks:
        if block.startswith(match_id):
            return block.strip()

    return None


def main():
    with open("match.txt", "r", encoding="utf-8") as f:
        content = f.read()

    print("Read: True")

    match_id = input("Enter match id (example N59 or #N59): ")

    result = extract_match(content, match_id)

    if result:
        print("Export: Found")
        print(result)
    else:
        print("Match not found")


if __name__ == "__main__":
    main()