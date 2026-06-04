try:
    with open("match.txt", "r", encoding="utf-8") as file:
        content = file.read()

    print("Read: True")
    print("Message: File read completed.")

except FileNotFoundError:
    print("Read: False")
    print("Message: match.txt not found.")

except Exception as e:
    print("Read: False")
    print(f"Message: {e}")