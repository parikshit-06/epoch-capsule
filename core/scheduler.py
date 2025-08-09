# core/scheduler.py
import time
from datetime import datetime
from typing import Optional
from core.storage import load_locked_capsules, read_encrypted_blob, mark_unlocked
from core.encryption import decrypt_data
from utils.keymanager import prompt_password_and_derive
from gui.player import play_video_from_bytes, show_image_from_bytes, show_text_from_bytes


def _display_plaintext_by_type(ctype: str, plaintext: bytes, title: Optional[str]):
    """Dispatch to appropriate player."""
    if ctype == "video":
        play_video_from_bytes(plaintext, window_title=title or "Video")
    elif ctype == "photo" or ctype.startswith("image"):
        show_image_from_bytes(plaintext, window_title=title or "Photo")
    else:
        show_text_from_bytes(plaintext, title=title)

def check_and_unlock():
    """
    Check DB for locked capsules whose unlock_time <= now.
    For each, prompt for password (derived key), decrypt, display, and mark unlocked.
    """
    now = datetime.now()
    capsules = load_locked_capsules(before=now)
    if not capsules:
        # nothing to do
        return

    for cap in capsules:
        cid = cap["id"]
        title = cap["title"]
        ctype = cap.get("type", "text")
        print(f"[unlock] Capsule {cid} '{title}' scheduled for {cap['unlock_time']} is due. Attempting to unlock...")

        # Read encrypted blob
        blob = read_encrypted_blob(cap["file_path"])
        if blob is None:
            print(f"[unlock] ERROR: Encrypted file missing for capsule {cid}. Skipping.")
            continue

        salt = cap["salt"]
        nonce = cap["nonce"]
        # prompt for password (user typed) and derive key; this returns the derived key
        try:
            key = prompt_password_and_derive(salt)
        except Exception as e:
            print(f"[unlock] Password entry failed or aborted for capsule {cid}: {e}")
            continue

        # decrypt: your decrypt_data signature may be (nonce, ciphertext, key)
        try:
            plaintext = decrypt_data(nonce, blob, key)
        except Exception as e:
            print(f"[unlock] Decryption failed for capsule {cid}: {e}")
            print("         (wrong password or corrupted file). Skipping.")
            continue

        # display according to type
        try:
            _display_plaintext_by_type(ctype, plaintext, title)
        except Exception as e:
            print(f"[unlock] Failed during display for capsule {cid}: {e}")
            # Do not mark unlocked if display failed
            continue

        # mark unlocked in DB
        try:
            mark_unlocked(cid)
            print(f"[unlock] Capsule {cid} marked as unlocked.")
        except Exception as e:
            print(f"[unlock] Failed to mark capsule {cid} as unlocked: {e}")


def auto_unlock_loop(poll_interval_seconds: int = 60):
    """
    Run check_and_unlock() repeatedly until killed.
    Intended for `python main.py autounlock` usage (you already added that command).
    WARNING: This process must be kept running. For true OS-level scheduling prefer cron/schtasks.
    """
    print(f"[autounlock] Starting auto-unlock loop (poll every {poll_interval_seconds}s). Ctrl-C to stop.")
    try:
        while True:
            try:
                check_and_unlock()
            except Exception as e:
                # log but keep loop alive
                print(f"[autounlock] Error during check_and_unlock: {e}")
            time.sleep(poll_interval_seconds)
    except KeyboardInterrupt:
        print("\n[autounlock] Stopped by user.")
