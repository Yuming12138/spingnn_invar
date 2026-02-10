from pathlib import Path

from ase.io import read


def element_order(symbols):
    order = []
    for symbol in symbols:
        if symbol not in order:
            order.append(symbol)
    return order


def write_poscar(symbols, positions, cell, dest_path, title):
    order = element_order(symbols)
    counts = [sum(1 for symbol in symbols if symbol == element) for element in order]
    with dest_path.open("w") as handle:
        handle.write(f"{title}\n")
        handle.write("1.0\n")
        for vector in cell:
            handle.write(f"{vector[0]:.16f} {vector[1]:.16f} {vector[2]:.16f}\n")
        handle.write(" ".join(order) + "\n")
        handle.write(" ".join(str(count) for count in counts) + "\n")
        handle.write("Cartesian\n")
        for element in order:
            for symbol, coord in zip(symbols, positions):
                if symbol == element:
                    handle.write(f"{coord[0]:.16f} {coord[1]:.16f} {coord[2]:.16f}\n")


def main():
    input_path = Path(
        "/home/chenguangming/3.projects/22.spingnn/1.dft_calculations/01.raw_datasets/FeNi_550_sampling/0.source/combined_dataset.xyz"
    )
    output_dirs = [
        Path(
            "/home/chenguangming/3.projects/22.spingnn/1.dft_calculations/01.raw_datasets/FeNi_550_sampling/1.FM_high"
        ),
        Path(
            "/home/chenguangming/3.projects/22.spingnn/1.dft_calculations/01.raw_datasets/FeNi_550_sampling/2.FM_medium"
        ),
        Path(
            "/home/chenguangming/3.projects/22.spingnn/1.dft_calculations/01.raw_datasets/FeNi_550_sampling/3.FM_low"
        ),
        Path(
            "/home/chenguangming/3.projects/22.spingnn/1.dft_calculations/01.raw_datasets/FeNi_550_sampling/4.AFM1_high"
        ),
        Path(
            "/home/chenguangming/3.projects/22.spingnn/1.dft_calculations/01.raw_datasets/FeNi_550_sampling/5.AFM1_medium"
        ),
        Path(
            "/home/chenguangming/3.projects/22.spingnn/1.dft_calculations/01.raw_datasets/FeNi_550_sampling/6.AFM1_low"
        ),
        Path(
            "/home/chenguangming/3.projects/22.spingnn/1.dft_calculations/01.raw_datasets/FeNi_550_sampling/7.AFM2_high"
        ),
        Path(
            "/home/chenguangming/3.projects/22.spingnn/1.dft_calculations/01.raw_datasets/FeNi_550_sampling/8.AFM2_medium"
        ),
        Path(
            "/home/chenguangming/3.projects/22.spingnn/1.dft_calculations/01.raw_datasets/FeNi_550_sampling/9.AFM2_low"
        ),
        Path(
            "/home/chenguangming/3.projects/22.spingnn/1.dft_calculations/01.raw_datasets/FeNi_550_sampling/10.random_high"
        ),
        Path(
            "/home/chenguangming/3.projects/22.spingnn/1.dft_calculations/01.raw_datasets/FeNi_550_sampling/11.random_medium"
        ),
        Path(
            "/home/chenguangming/3.projects/22.spingnn/1.dft_calculations/01.raw_datasets/FeNi_550_sampling/12.random_low"
        ),
    ]

    frames = read(str(input_path), index=":10")
    if len(frames) < 10:
        raise ValueError(f"Only found {len(frames)} frames in {input_path}")

    for index, atoms in enumerate(frames, start=1):
        symbols = atoms.get_chemical_symbols()
        positions = atoms.get_positions()
        cell = atoms.get_cell().array
        subdir_name = f"{index}.structure-{index}"
        for output_dir in output_dirs:
            target_dir = output_dir / subdir_name
            target_dir.mkdir(parents=True, exist_ok=True)
            write_poscar(symbols, positions, cell, target_dir / "POSCAR", f"structure_{index}")


if __name__ == "__main__":
    main()
