import argparse
import os
import getpass
from datetime import datetime
from core.encryption import encrypt_data, decrypt_data
from core.metadata import parse_unlock_time
from core.storage import save_capsule, init_db, check_capsules
from utils.keymanager import derive_key_from_password
from core.scheduler import check_and_unlock, auto_unlock_loop
from capture.text import capture_text
from gui.photo_gui import capture_photo_gui as capture_photo
from gui.video_gui import record_video_gui as record_video

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

    # --- Use capture modules ---
    if ctype == "text":
        content = capture_text()
    elif ctype == "photo":
        content = capture_photo()
        if content is None:
            print("Photo capture cancelled or failed.")
            return
    elif ctype == "video":
        content = record_video()
        if content is None:
            print("Video capture cancelled or failed.")
            return

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
        choices=["create", "unlock", "init", "help", "check", "autounlock"],
    )
    parser.add_argument(
        "--interval", type=int, default=60, help="Polling interval for autounlock (seconds)"
    )
    parser.add_argument(
        "--password", type=str, default=None, help="Password for auto-unlock (use with caution!)"
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
        auto_unlock_loop(poll_interval_seconds=args.interval, auto_password=args.password)
    else:
        print("Usage: python main.py [create|unlock|init|autounlock]")
        print("  create      - make a new capsule")
        print("  unlock      - check and reveal ready capsules")
        print("  init        - initialize db/storage")
        print("  autounlock  - auto-check and unlock capsules in a loop")

if __name__ == "__main__":
    main()