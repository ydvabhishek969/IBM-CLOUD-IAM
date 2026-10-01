"""CLI: python -m cos_iam {setup|verify|cleanup|all}"""
import argparse
import logging
import sys

from ibm_cloud_sdk_core import ApiException

from .config import ConfigError, get_settings
from .iam_manager import IamManager
from .verify import run_verification, save_keys


def main() -> int:
    parser = argparse.ArgumentParser(prog="cos_iam", description=__doc__)
    parser.add_argument("command", choices=["setup", "verify", "cleanup", "all"])
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s %(message)s")
    try:
        s = get_settings()
        if args.command in ("setup", "all"):
            save_keys(IamManager(s).setup())
            print("Setup complete. Service ID API keys saved to .secrets/keys.json (gitignored).")
            print("Note: IAM policy changes can take up to a minute to propagate.")
        if args.command in ("verify", "all"):
            if not run_verification(s):
                return 1
        if args.command == "cleanup":
            IamManager(s).cleanup()
            print("Cleanup complete.")
        return 0
    except ConfigError as e:
        print(f"Config error: {e}", file=sys.stderr)
    except ApiException as e:
        print(f"IBM Cloud API error {e.code}: {e.message}", file=sys.stderr)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
