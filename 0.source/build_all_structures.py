from pathlib import Path
import argparse
import re
import numpy as np


MAG_RANGES = {
    "high": {"Fe": [2.4, 2.8], "Ni": [0.6, 1.0]},
    "medium": {"Fe": [1.5, 2.2], "Ni": [0.3, 0.6]},
    "low": {"Fe": [0.6, 1.2], "Ni": [0.05, 0.3]},
}


MODE_DIRS = {
    "FM_high": "1.FM_high",
    "FM_medium": "2.FM_medium",
    "FM_low": "3.FM_low",
    "AFM1_high": "4.AFM1_high",
    "AFM1_medium": "5.AFM1_medium",
    "AFM1_low": "6.AFM1_low",
    "AFM2_high": "7.AFM2_high",
    "AFM2_medium": "8.AFM2_medium",
    "AFM2_low": "9.AFM2_low",
    "random_high": "10.random_high",
    "random_medium": "11.random_medium",
    "random_low": "12.random_low",
}


def parse_lattice(line):
    match = re.search(r'Lattice="([^"]+)"', line)
    if not match:
        raise ValueError("Missing Lattice in header line")
    numbers = [float(value) for value in match.group(1).split()]
    if len(numbers) != 9:
        raise ValueError("Lattice should have 9 numbers")
    return np.array([numbers[0:3], numbers[3:6], numbers[6:9]])


def read_frames(path):
    lines = path.read_text().splitlines()
    index = 0
    frames = []
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        atom_count = int(line)
        header = lines[index + 1]
        lattice = parse_lattice(header)
        atoms = []
        for offset in range(atom_count):
            parts = lines[index + 2 + offset].split()
            species = parts[0]
            coords = [float(parts[1]), float(parts[2]), float(parts[3])]
            atoms.append((species, coords))
        frames.append({"lattice": lattice, "atoms": atoms})
        index += 2 + atom_count
    return frames


def element_order(atoms):
    order = []
    for species, _ in atoms:
        if species not in order:
            order.append(species)
    return order


def write_poscar(frame, dest_path, title):
    atoms = frame["atoms"]
    order = element_order(atoms)
    counts = [sum(1 for species, _ in atoms if species == element) for element in order]
    with dest_path.open("w") as handle:
        handle.write(f"{title}\n")
        handle.write("1.0\n")
        for vector in frame["lattice"]:
            handle.write(f"{vector[0]:.16f} {vector[1]:.16f} {vector[2]:.16f}\n")
        handle.write(" ".join(order) + "\n")
        handle.write(" ".join(str(count) for count in counts) + "\n")
        handle.write("Cartesian\n")
        for element in order:
            for species, coord in atoms:
                if species == element:
                    handle.write(f"{coord[0]:.16f} {coord[1]:.16f} {coord[2]:.16f}\n")


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["FM", "AFM1", "AFM2", "random"])
    parser.add_argument("--intensity", required=True, choices=["high", "medium", "low"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(
        "/home/chenguangming/3.projects/22.spingnn/1.dft_calculations/01.raw_datasets/FeNi_550_sampling"
    )
    input_path = root / "0.source" / "combined_dataset.xyz"
    common_inputs = root / "0.common_inputs"
    base_incar = (common_inputs / "INCAR").read_text().splitlines()
    kpoints = common_inputs / "KPOINTS"
    potcar = common_inputs / "POTCAR"
    submit = common_inputs / "submit_vasp.sh"

    key = f"{args.mode}_{args.intensity}"
    if key not in MODE_DIRS:
        raise ValueError(f"Unsupported mode/intensity: {key}")
    output_dir = root / MODE_DIRS[key]
    output_dir.mkdir(parents=True, exist_ok=True)

    frames = read_frames(input_path)
    if args.dry_run:
        print(len(frames))
        return

    for index, frame in enumerate(frames, start=1):
        subdir_name = f"{index}.structure-{index}"
        structure_dir = output_dir / subdir_name
        structure_dir.mkdir(parents=True, exist_ok=True)
        write_poscar(frame, structure_dir / "POSCAR", f"structure_{index}")

        lattice = frame["lattice"]
        atoms = frame["atoms"]
        species = [species for species, _ in atoms]
        cart = np.array([coord for _, coord in atoms])
        frac = cart @ np.linalg.inv(lattice)
        mag_parts = generate_magmom_parts(species, frac, args.mode, args.intensity)
        incar_lines = update_incar(base_incar, mag_parts)
        (structure_dir / "INCAR").write_text("\n".join(incar_lines) + "\n")
        ensure_link(kpoints, structure_dir / "KPOINTS")
        ensure_link(potcar, structure_dir / "POTCAR")
        ensure_link(submit, structure_dir / "submit_vasp.sh")


if __name__ == "__main__":
    main()
