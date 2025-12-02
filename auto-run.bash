#!/usr/bin/env bash

# Script automasi untuk menjalankan berbagai algoritma scheduler
# menggunakan uv dan menyimpan hasil ke direktori results/<algo>/<dataset>/<percobaan>.csv
#
# Cara pakai umum:
#   chmod +x auto-run.bash
#   ./auto-run.bash <jumlah_percobaan> [algo1 algo2 ...] [-- dataset]
#
# Keterangan argumen:
#   - <jumlah_percobaan> : banyaknya percobaan per algoritma (wajib)
#   - [algo1 algo2 ...]  : daftar algoritma (opsional), default: shc pso rr fcfs
#   - [-- dataset]       : nama dataset (opsional), bisa berupa:
#                          * nama pendek yang dikenali scheduler:
#                              - random_simple      -> datasets/dataset_random_simple.txt
#                              - low_high           -> datasets/dataset_low_high.txt
#                              - random_stratified  -> datasets/dataset_random_stratified.txt
#                          * atau path langsung ke file dataset, misalnya:
#                              - datasets/dataset_low_high.txt
#                        Jika tidak diisi, scheduler akan memakai dataset default (dataset.txt)
#                        dan hasil tersimpan di results/<algo>/default/<n>.csv
#
# Contoh:
#   ./auto-run.bash 5
#     -> Menjalankan shc, pso, rr, fcfs masing-masing untuk percobaan 1..5,
#        menggunakan dataset default (dataset.txt)
#   ./auto-run.bash 3 shc pso -- random_simple
#     -> Hanya menjalankan shc dan pso untuk percobaan 1..3
#        menggunakan dataset datasets/dataset_random_simple.txt
#        Hasil akan berada di results/shc/random-simple/ dan results/pso/random-simple/
#   ./auto-run.bash 2 rr fcfs -- datasets/dataset_low_high.txt
#     -> Menjalankan rr dan fcfs untuk percobaan 1..2
#        menggunakan file datasets/dataset_low_high.txt

set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <jumlah_percobaan> [algo1 algo2 ...] [-- dataset]" >&2
  exit 1
fi

# Jumlah percobaan diambil dari argumen pertama
NUM_EXP=$1
shift

DATASET=""   # default: tidak di-set, scheduler akan pakai dataset.txt
ALGOS=()

# Parse sisa argumen: kumpulkan algoritma sampai ketemu '--', sisanya dianggap dataset
while [ "$#" -gt 0 ]; do
  if [ "$1" = "--" ]; then
    shift
    if [ "$#" -gt 0 ]; then
      DATASET=$1
      shift
    fi
    break
  else
    ALGOS+=("$1")
    shift
  fi
done

# Jika user tidak menyebutkan algoritma, pakai default
if [ "${#ALGOS[@]}" -eq 0 ]; then
  ALGOS=("shc" "pso" "rr" "fcfs")
fi

echo "Menjalankan automasi scheduler untuk ${NUM_EXP} percobaan per algoritma..."
echo "Algoritma yang dijalankan: ${ALGOS[*]}"
if [ -n "${DATASET}" ]; then
  echo "Dataset yang digunakan: ${DATASET}"
else
  echo "Dataset yang digunakan: default (dataset.txt)"
fi

for algo in "${ALGOS[@]}"; do
  echo
  echo "=== Algoritma: ${algo} ==="
  for ((i=1; i<=NUM_EXP; i++)); do
    echo "-- Percobaan ${i} (${algo}) --"
    if [ -n "${DATASET}" ]; then
      uv run scheduler.py "${algo}" "${i}" "${DATASET}"
    else
      uv run scheduler.py "${algo}" "${i}"
    fi
  done
done

echo
echo "Selesai menjalankan semua percobaan. Hasil tersimpan di direktori results/<algo>/<dataset>/<n>.csv"
