import re

try:
    with open("match.txt", "r", encoding="utf-8") as file:
        content = file.read()

    # Count matches that start with #N<number>
    matches = re.findall(r'^#N\d+\.', content, re.MULTILINE)

    print("Read: True")
    print(f"{len(matches)} match code found")

except FileNotFoundError:
    print("Read: False")
    print("match.txt not found")

except Exception as e:
    print("Read: False")
    print(f"Error: {e}")