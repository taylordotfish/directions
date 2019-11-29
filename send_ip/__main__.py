from .send import run
import sys


def main():
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
