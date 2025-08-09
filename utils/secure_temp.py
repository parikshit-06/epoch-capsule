# utils/secure_temp.py
import tempfile
import os
import stat

def create_secure_temp_file(contents: bytes, suffix: str = "") -> str:
    """
    Create a temp file with given bytes, return absolute path.
    File is created with restrictive permissions.
    Caller is responsible for calling secure_delete(path) afterwards.
    """
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        # set restrictive permissions (owner read/write only)
        if hasattr(os, "fchmod"):
            os.fchmod(fd, stat.S_IRUSR | stat.S_IWUSR)
        with os.fdopen(fd, "wb") as f:
            f.write(contents)
    except Exception:
        try:
            os.remove(path)
        except Exception:
            pass
        raise
    return path

def secure_delete(path: str):
    """
    Overwrite file with zeros and remove it.
    Best-effort — OS/filesystem may still keep copies.
    """
    try:
        if not os.path.exists(path):
            return
        length = os.path.getsize(path)
        with open(path, "r+b") as f:
            f.seek(0)
            f.write(b"\x00" * length)
            f.flush()
            os.fsync(f.fileno())
        os.remove(path)
    except Exception:
        # Last resort: try to remove
        try:
            os.remove(path)
        except Exception:
            pass
