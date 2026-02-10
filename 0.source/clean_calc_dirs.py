from pathlib import Path
import argparse
import re


KEEP_FILES = {"INCAR", "POSCAR", "POTCAR", "KPOINTS", "submit_vasp.sh"}


def iter_structure_dirs(root_dir):
    pattern = re.compile(r"^\d+\.(FM|AFM1|AFM2|random)_(high|medium|low)$")
    for child in root_dir.iterdir():
        if not child.is_dir():
            continue
        if not pattern.match(child.name):
            continue
        for subdir in child.iterdir():
            if subdir.is_dir() and ".structure-" in subdir.name:
                yield subdir


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.root)
    removed = 0
    for structure_dir in iter_structure_dirs(root):
        for item in structure_dir.iterdir():
            if item.name in KEEP_FILES:
                continue
            if args.dry_run:
                print(f"REMOVE {item}")
                continue
            if item.is_dir():
                for sub in item.rglob("*"):
                    if sub.is_file():
                        sub.unlink()
                for sub in sorted(item.rglob("*"), reverse=True):
                    if sub.is_dir():
                        sub.rmdir()
                item.rmdir()
            else:
                item.unlink()
            removed += 1
    if args.dry_run:
        return
    print(f"removed {removed} items")


if __name__ == "__main__":
    main()
