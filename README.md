# Epoch Capsule

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/parikshit-06/epoch-capsule)](https://github.com/parikshit-06/epoch-capsule/commits/main)
[![Issues](https://img.shields.io/github/issues/parikshit-06/epoch-capsule)](https://github.com/parikshit-06/epoch-capsule/issues)
[![Stars](https://img.shields.io/github/stars/parikshit-06/epoch-capsule?style=social)](https://github.com/parikshit-06/epoch-capsule/stargazers)

A secure, time-locked vault for text, photo, and video messages. Encrypt content now, and unlock it only at a specified date & time.

---

## Features

* Create encrypted capsules (text / photo / video)
* Support for relative (`20s`, `1h`, `2d`) and absolute (`2025-08-09T14:00:00`) unlock times
* AES-256-GCM encryption with PBKDF2-derived keys (per-capsule salt)
* Local storage (SQLite + encrypted blobs) - no plaintext saved permanently
* Manual and automatic unlock flows (`unlock`, `autounlock`)
* Capture modules designed to record to memory (no raw file left on disk)

---

## Requirements

* Python 3.9+
* A terminal (PowerShell, Bash, etc.)
* (Optional) Webcam for photo/video capture (if you use capture features)

Install dependencies:

```bash
pip install -r requirements.txt
```

`requirements.txt` should include at least:

```
cryptography
opencv-python
pillow
```

---

## Quickstart

```bash
# Clone the repo
git clone https://github.com/parikshit-06/epoch-capsule.git
cd epoch-capsule

# Create & activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Initialize the database

Run once to create the `data/` folder and SQLite DB:

```bash
python main.py init
# Output: "Initialized database."
```

---

## Create a capsule

```bash
python main.py create
```

Interactive prompts:

* **Title** - name for the capsule
* **Unlock in** - relative (e.g. `20s`, `1h`, `2d`) or absolute (`2025-08-09T14:00` or `YYYY-MM-DD HH:MM`)
* **Type** - `text`, `photo`, or `video`

  * `text`: multiline input, finish with a blank line
  * `photo` / `video`: you may be prompted to provide a file path (or use live capture if enabled)
* **Password** - used to derive encryption key (you’ll need it to decrypt)

After finishing you should see:

```
Saved Capsule id=<id> title='<title>' scheduled for <timestamp>
```

---

## Check capsule status

List all capsules and their status (locked / unlocked):

```bash
python main.py check
```

---

## Manual unlock

Attempt to unlock any due (past unlock time) capsules:

```bash
python main.py unlock
```

Or unlock a specific capsule by id:

```bash
python main.py unlock --id \<ID\>
```

You will be prompted for the password for each capsule being unlocked.

---

## Automatic unlock (interactive autounlock)

Run the autounlock loop which checks periodically and prompts for passwords when a capsule is due:

```bash
python main.py autounlock
```

This keeps running until you stop it (`Ctrl-C`). It is useful when you want a simple long-running process to prompt and display capsules automatically.

---

## (Alternative) Auto-unlock with a one-shot password argument

If your build includes an `autounlock` command that accepts a `--password` flag (risky because passwords on command lines can leak to system logs), you can run:

```bash
python main.py autounlock --password \<YOURPASSWORD\>
```

**Strong warning:** passing passwords on the command line is insecure on multi-user systems (visible in process lists and shell history). Prefer interactive prompts or OS keychain solutions.

---

## How it works

1. User provides content (text/photo/video) and a password.
2. App generates a random salt, derives a 32-byte key with PBKDF2(password, salt).
3. Content is encrypted with AES-256-GCM (nonce + ciphertext).
4. Ciphertext is written to `data/capsule_files/*.tccap` and metadata is saved in `data/capsules.db`.
5. At unlock time (manual or scheduled), the program reads metadata, prompts for password (or retrieves it), derives the key, decrypts in memory, displays content using secure temporary files, and marks the capsule `unlocked`.

---

## Security notes

* No plaintext is stored permanently by the app (only encrypted blobs).
* The app uses authenticated encryption (AES-GCM) to detect tampering.
* Passwords are not stored by default. If you enable headless auto-unlock you must handle password storage securely (OS keychain recommended).
* Secure deletion of temporary files is *best-effort* - some filesystems or OS caches might still retain data.

---

## Troubleshooting

* **Can't open webcam?** Ensure no other app is using it and that OpenCV supports your camera.
* **Decryption fails:** Make sure you enter the exact password used during creation. Corrupted blob or wrong password will prevent decryption.
* **Video won't play:** OpenCV may lack required codecs on some systems. You can use VLC/ffplay fallback later.
* **Cron/Task Scheduler issues:** Verify full absolute paths to `python` and `main.py`, and check scheduler logs.

---

## Development & Contribution

* Implementations live in:

  * `capture/` - capture modules (video/photo/text)
  * `core/` - encryption, storage, scheduler, metadata
  * `gui/` - secure player (optional)
  * `utils/` - key manager, secure temp
* Want to help? Open a PR, describe the change, and include tests.

---

## License & Contact

* MIT License - See LICENSE for details.
* This project lives at: [https://github.com/parikshit-06/epoch-capsule](https://github.com/parikshit-06/epoch-capsule)
---

## Contributing
* Fork this repository
* Create your feature branch (git checkout -b feature-name)
* Commit your changes (git commit -m "Add feature")
* Push to the branch (git push origin feature-name)
* Create a Pull Request
