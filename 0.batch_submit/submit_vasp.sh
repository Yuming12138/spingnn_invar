#!/bin/bash
#SBATCH --job-name=FeNi
#SBATCH --partition=cp1
#SBATCH -N 1
#SBATCH -n 36
#SBATCH --output=%j.out
#SBATCH --error=%j.err

#module add Intel_compiler/16.0.3
#module add MPI/Intel/IMPI/5.1.3.210
#module add MKL/16.0.3
#module add lammps/7Aug19-icc16-IMPI5.1
module  purge
module add Intel_compiler/19.1.2   MPI/Intel/IMPI/2019.8.254    MKL/19.1.2
module add vasp/6.3.0
#module add phonopy

echo "Starting VASP non-collinear calculation..."
start_time=$(date +%s)

# 注意：Fe64Ni36 非共线计算必须使用 vasp_ncl
yhrun vasp_ncl    > log 2>&1

end_time=$(date +%s)
duration=$((end_time - start_time))
echo "Calculation finished at $(date)"
echo "Total runtime: $duration seconds"
