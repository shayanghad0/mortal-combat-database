import re

def load_file():
    with open("match.txt", "r", encoding="utf-8") as f:
        return f.read()

def get_all_match_ids(content):
    # finds #N123 patterns
    return re.findall(r"^#N\d+", content, re.MULTILINE)

def extract_match(content, match_id):
    # split by match headers
    pattern = r"(^#N\d+.*?)(?=^#N\d+|\Z)"
    blocks = re.findall(pattern, content, re.MULTILINE | re.DOTALL)

    for block in blocks:
        if block.startswith(match_id):
            return block.strip()

    return None


def main():
    content = load_file()

    matches = get_all_match_ids(content)

    print("Read: True")
    print(f"{len(matches)} match code found")

    match_id = input("Enter match id (example #N59): ").strip()

    result = extract_match(content, match_id)

    if result:
        filename = f"{match_id.replace('#', '')}_export.txt"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(result)

        print("Export: Done")
        print(f"Saved as {filename}")
    else:
        print("Match not found")


if __name__ == "__main__":
    main()