# main.py
import argparse
import os
import getpass
from datetime import datetime
from core.encryption import encrypt_data, decrypt_data
from core.metadata import parse_unlock_time
from core.storage import save_capsule, init_db, check_capsules
from utils.keymanager import derive_key_from_password
from core.scheduler import check_and_unlock, auto_unlock_loop

def _derive_key_and_save(title, unlock_time, ctype, content, password):
    salt = os.urandom(16)
    key = derive_key_from_password(password, salt)
    nonce, encrypted = encrypt_data(content, key)
    save_capsule(title, unlock_time, ctype, encrypted, nonce, salt)
    print(f"Saved capsule '{title}' scheduled for {unlock_time.isoformat()}")

def create_capsule_flow():
    title = input("Title: ").strip()
    if not title:
        print("Title cannot be empty.")
        return

    unlock_str = input("Unlock in (e.g. 1h or 2025-08-09 14:00): ").strip()
    try:
        unlock_time = parse_unlock_time(unlock_str)
    except Exception as e:
        print(f"Invalid unlock time: {e}")
        return

    ctype = input("Type (text/photo/video) [text]: ").strip().lower() or "text"
    if ctype not in ("text", "photo", "video"):
        print("Invalid type.")
        return

    if ctype == "text":
        print("Enter your message. Finish with a blank line:")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        content = "\n".join(lines).encode("utf-8")
    elif ctype == "video":
        video_path = input("Provide path to video file (or leave blank to record now): ").strip()
        if not video_path:
            print("Recording from webcam is not implemented yet.")
            return
        if not os.path.isfile(video_path):
            print("Invalid file path. Please provide a valid video file.")
            return
        with open(video_path, "rb") as f:
            content = f.read()
    elif ctype == "photo":
        photo_path = input("Provide path to photo file: ").strip()
        if not os.path.isfile(photo_path):
            print("Invalid file path. Please provide a valid photo file.")
            return
        with open(photo_path, "rb") as f:
            content = f.read()

    password = getpass.getpass("Set a password for this capsule: ")
    if not password:
        print("Password cannot be empty.")
        return

    _derive_key_and_save(title, unlock_time, ctype, content, password)
def main():
    parser = argparse.ArgumentParser(prog="timecapsule")
    parser.add_argument(
        "command",
        nargs="?",
        default="help",
        choices=["create", "unlock", "init", "help", "check", "autounlock"],  # Added autounlock
    )
    args = parser.parse_args()

    if args.command == "create":
        create_capsule_flow()
    elif args.command == "unlock":
        check_and_unlock()
    elif args.command == "init":
        init_db()
        print("Initialized database.")
    elif args.command == "check":
        check_capsules()
    elif args.command == "autounlock":
        auto_unlock_loop()
    else:
        print("Usage: python main.py [create|unlock|init|autounlock]")
        print("  create      - make a new capsule")
        print("  unlock      - check and reveal ready capsules")
        print("  init        - initialize db/storage")
        print("  autounlock  - auto-check and unlock capsules in a loop")

if __name__ == "__main__":
    main()
