from pathlib import Path
import re
import subprocess


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
    root = Path(
        "/home/chenguangming/3.projects/22.spingnn/1.dft_calculations/01.raw_datasets/FeNi_550_sampling"
    )
    submitted = 0
    for structure_dir in iter_structure_dirs(root):
        submit_script = structure_dir / "submit_vasp.sh"
        if not submit_script.exists():
            continue
        subprocess.run(["sbatch", "submit_vasp.sh"], cwd=structure_dir, check=True)
        submitted += 1
    print(f"submitted {submitted} jobs")


if __name__ == "__main__":
    main()
