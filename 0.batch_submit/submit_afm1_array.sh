#!/bin/bash
#SBATCH --job-name=FeNi_AFM1
#SBATCH --partition=cp1
#SBATCH -N 1
#SBATCH -n 36
#SBATCH --output=%x_%A_%a.out
#SBATCH --error=%x_%A_%a.err

module purge
module add Intel_compiler/19.1.2 MPI/Intel/IMPI/2019.8.254 MKL/19.1.2
module add vasp/6.3.0

if [ -z "${INTENSITY}" ]; then
  echo "INTENSITY is required"
  exit 1
fi

if [ -z "${ROOT_DIR}" ]; then
  echo "ROOT_DIR is required"
  exit 1
fi

structure_id=${SLURM_ARRAY_TASK_ID}
case "${INTENSITY}" in
  high) folder="4.AFM1_high" ;;
  medium) folder="5.AFM1_medium" ;;
  low) folder="6.AFM1_low" ;;
  *) echo "Unknown INTENSITY: ${INTENSITY}"; exit 1 ;;
esac
work_dir="${ROOT_DIR}/${folder}/${structure_id}.structure-${structure_id}"

if [ ! -d "${work_dir}" ]; then
  echo "Missing directory: ${work_dir}"
  exit 1
fi

cd "${work_dir}"
start_time=$(date +%s)
yhrun vasp_ncl > log 2>&1
end_time=$(date +%s)
duration=$((end_time - start_time))
echo "Calculation finished at $(date)"
echo "Total runtime: $duration seconds"
