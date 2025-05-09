import sys

from src.gac.cli import cli

if __name__ == "__main__":
    sys.argv = [sys.argv[0], "diff", "--help"]
    cli()
