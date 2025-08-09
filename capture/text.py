# capture/text.py
def capture_text():
    """
    Captures multiline text from user via CLI.
    Ends when user enters a blank line.
    """
    print("Enter your message. End with a blank line:")
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    text_data = "\n".join(lines)
    return text_data.encode("utf-8")