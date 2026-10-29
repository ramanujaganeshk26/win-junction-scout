import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Win Junction Scout")
    parser.add_argument("path", nargs="?", default=".", help="Target directory to scan")
    args = parser.parse_args()
    print(f"Scanning: {args.path}")

if __name__ == "__main__":
    main()
