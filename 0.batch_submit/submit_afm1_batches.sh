#!/bin/bash

ROOT_DIR="/home/chenguangming/3.projects/22.spingnn/1.dft_calculations/01.raw_datasets/FeNi_550_sampling"
ARRAY_SCRIPT="${ROOT_DIR}/0.batch_submit/submit_afm1_array.sh"

sbatch --array=1-505%1 --export=ALL,INTENSITY=high,ROOT_DIR="${ROOT_DIR}" "${ARRAY_SCRIPT}"
sbatch --array=1-505%1 --export=ALL,INTENSITY=medium,ROOT_DIR="${ROOT_DIR}" "${ARRAY_SCRIPT}"
sbatch --array=1-505%1 --export=ALL,INTENSITY=low,ROOT_DIR="${ROOT_DIR}" "${ARRAY_SCRIPT}"
