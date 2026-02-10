from pathlib import Path
import re

import numpy as np


MAG_RANGES = {
    "high": {"Fe": [2.4, 2.8], "Ni": [0.6, 1.0]},
    "medium": {"Fe": [1.5, 2.2], "Ni": [0.3, 0.6]},
    "low": {"Fe": [0.6, 1.2], "Ni": [0.05, 0.3]},
}


def parse_poscar(path):
    lines = path.read_text().splitlines()
    scale = float(lines[1].strip())
    lattice = np.array(
        [
            [float(x) for x in lines[2].split()],
            [float(x) for x in lines[3].split()],
            [float(x) for x in lines[4].split()],
        ]
    )
    lattice = lattice * scale
    elements = lines[5].split()
    counts = [int(x) for x in lines[6].split()]
    coord_type = lines[7].strip().lower()
    total = sum(counts)
    coords = []
    for i in range(total):
        coords.append([float(x) for x in lines[8 + i].split()[:3]])
    coords = np.array(coords)
    if coord_type.startswith("c"):
        frac = coords @ np.linalg.inv(lattice)
    else:
        frac = coords
    species = []
    for element, count in zip(elements, counts):
        species.extend([element] * count)
    return species, frac


def generate_magmom_parts(species_list, coords_list, mode, intensity):
    mag_parts = []
    for species, (x, y, z) in zip(species_list, coords_list):
        r_min, r_max = MAG_RANGES[intensity][species]
        m_mag = np.random.uniform(r_min, r_max)
        if "random" in mode:
            u = np.random.uniform(-1, 1)
            phi = np.random.uniform(0, 2 * np.pi)
            sin_theta = np.sqrt(1 - u**2)
            vec = [sin_theta * np.cos(phi), sin_theta * np.sin(phi), u]
        elif mode == "FM":
            vec = [0.0, 0.0, 1.0]
        elif mode == "AFM1":
            layer_idx = int(round(z * 4))
            sign = 1.0 if layer_idx % 2 == 0 else -1.0
            vec = [0.0, 0.0, sign]
        elif mode == "AFM2":
            ix = int(round(x * 4))
            iy = int(round(y * 4))
            sign = 1.0 if (ix + iy) % 2 == 0 else -1.0
            vec = [0.0, 0.0, sign]
        else:
            vec = [0.0, 0.0, 1.0]
        mx = m_mag * vec[0]
        my = m_mag * vec[1]
        mz = m_mag * vec[2]
        mag_parts.append(f"{mx:.3f} {my:.3f} {mz:.3f}")
    return mag_parts


def format_magmom_lines(mag_parts, per_line=8):
    lines = []
    for i in range(0, len(mag_parts), per_line):
        chunk = "   ".join(mag_parts[i : i + per_line])
        is_last = i + per_line >= len(mag_parts)
        suffix = "" if is_last else " \\"
        if i == 0:
            lines.append(f"MAGMOM = {chunk}{suffix}")
        else:
            lines.append(f"         {chunk}{suffix}")
    return lines


def update_incar(base_lines, mag_parts):
    updated = []
    in_magmom_block = False
    for line in base_lines:
        if re.match(r"\s*MAGMOM\s*=", line, re.IGNORECASE):
            in_magmom_block = True
            continue
        if in_magmom_block:
            if line.strip() == "":
                in_magmom_block = False
            elif "=" in line:
                in_magmom_block = False
                updated.append(line)
            elif not line[:1].isspace():
                in_magmom_block = False
                updated.append(line)
            else:
                continue
        else:
            updated.append(line)
    formatted = format_magmom_lines(mag_parts)
    if updated and updated[-1].strip() != "":
        updated.append("")
    updated.extend(formatted)
    return updated


def ensure_link(target, link_path):
    if link_path.exists() or link_path.is_symlink():
        link_path.unlink()
    link_path.symlink_to(target)


def iter_structure_dirs(root_dir):
    pattern = re.compile(r"^\d+\.(FM|AFM1|AFM2|random)_(high|medium|low)$")
    for child in root_dir.iterdir():
        if not child.is_dir():
            continue
        match = pattern.match(child.name)
        if not match:
            continue
        mode, intensity = match.group(1), match.group(2)
        for subdir in child.iterdir():
            if subdir.is_dir() and ".structure-" in subdir.name:
                yield subdir, mode, intensity


def main():
    root = Path(
        "/home/chenguangming/3.projects/22.spingnn/1.dft_calculations/01.raw_datasets/FeNi_550_sampling"
    )
    common_inputs = root / "0.common_inputs"
    base_incar = (common_inputs / "INCAR").read_text().splitlines()
    kpoints = common_inputs / "KPOINTS"
    potcar = common_inputs / "POTCAR"
    submit = common_inputs / "submit_vasp.sh"

    for structure_dir, mode, intensity in iter_structure_dirs(root):
        poscar_path = structure_dir / "POSCAR"
        species, frac = parse_poscar(poscar_path)
        mode_key = "random" if mode == "random" else mode
        mag_parts = generate_magmom_parts(species, frac, mode_key, intensity)
        incar_lines = update_incar(base_incar, mag_parts)
        (structure_dir / "INCAR").write_text("\n".join(incar_lines) + "\n")
        ensure_link(kpoints, structure_dir / "KPOINTS")
        ensure_link(potcar, structure_dir / "POTCAR")
        ensure_link(submit, structure_dir / "submit_vasp.sh")


if __name__ == "__main__":
    main()
