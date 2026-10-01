"""Prove the policies work: reader can read but not write; writer can do both."""
import json
from pathlib import Path

from .config import Settings
from .cos_client import can_delete, can_list, can_upload, make_cos_client

KEYS_FILE = Path(".secrets/keys.json")


def save_keys(keys: dict) -> None:
    KEYS_FILE.parent.mkdir(exist_ok=True)
    KEYS_FILE.write_text(json.dumps(keys, indent=2))
    KEYS_FILE.chmod(0o600)


def load_keys() -> dict:
    if not KEYS_FILE.exists():
        raise FileNotFoundError("Run `python -m cos_iam setup` first.")
    return json.loads(KEYS_FILE.read_text())


def run_verification(s: Settings) -> bool:
    keys = load_keys()
    reader = make_cos_client(keys["reader_api_key"], s.instance_crn, s.endpoint)
    writer = make_cos_client(keys["writer_api_key"], s.instance_crn, s.endpoint)

    # (label, client, action, expected result)
    checks = [
        ("reader  LIST   ", lambda: can_list(reader, s.bucket), True),
        ("reader  UPLOAD ", lambda: can_upload(reader, s.bucket), False),
        ("writer  UPLOAD ", lambda: can_upload(writer, s.bucket), True),
        ("writer  LIST   ", lambda: can_list(writer, s.bucket), True),
        ("writer  DELETE ", lambda: can_delete(writer, s.bucket), True),
    ]
    ok = True
    print(f"\nVerifying IAM policies on bucket '{s.bucket}'\n" + "-" * 50)
    for label, fn, expected in checks:
        actual = fn()
        passed = actual == expected
        ok &= passed
        print(f"{'PASS' if passed else 'FAIL'}  {label} expected={'allow' if expected else 'deny '} got={'allow' if actual else 'deny'}")
    print("-" * 50, "\nResult:", "ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED")
    return ok
