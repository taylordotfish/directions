from . import directions
from .directions import CACHE_DIR, log
import os
import sys
import traceback

LOG_PATH = os.path.join(CACHE_DIR, "directions.log")


def main():
    with open(LOG_PATH, "a", encoding="utf8") as f:
        directions.set_log_file(f)
        try:
            directions.run()
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)
        except Exception:
            log(traceback.format_exc())
            sys.exit(1)
        directions.set_log_file(None)
    try:
        sys.stdout.close()
    except BrokenPipeError:
        pass


if __name__ == "__main__":
    main()
