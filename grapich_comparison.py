import os
import sys

import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
OUTPUT_BASE_DIR = os.path.join(BASE_DIR, "grapich")


def normalise_dataset_name(dataset_arg: str | None) -> tuple[str, str]:
    """Return (dataset_folder_name, dataset_label) given raw dataset arg or None.

    - If None: ('default', 'default')
    - If looks like a path: use filename without extension as folder/label.
    - Else: use arg as key, but replace '_' with '-' for folder name.
    """
    if dataset_arg is None:
        return "default", "default"

    key = dataset_arg.strip()
    if not key:
        return "default", "default"

    # If contains path separator, treat as path
    if os.path.sep in key:
        base = os.path.basename(key)
        name, _ = os.path.splitext(base)
        return name, name

    # Treat as short name
    folder = key.replace("_", "-")
    return folder, key


def load_results(algo: str, exp_index: str, dataset_folder: str) -> pd.DataFrame:
    """Load hasil satu algoritma untuk satu percobaan dan dataset.

    File diharapkan berada di: results/<algo>/<dataset_folder>/<exp_index>.csv
    Contoh: results/shc/random-simple/1.csv, results/pso/default/3.csv, dll.
    """
    algo = algo.lower()
    path = os.path.join(RESULTS_DIR, algo, dataset_folder, f"{exp_index}.csv")

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"File hasil untuk {algo} percobaan {exp_index} (dataset={dataset_folder}) tidak ditemukan: {path}"
        )

    df = pd.read_csv(path)

    # Pastikan kolom waktu bertipe numerik
    for col in ["start_time", "exec_time", "finish_time", "wait_time"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["algo"] = algo.upper()
    return df


def ensure_output_dir(dataset_folder: str) -> str:
    out_dir = os.path.join(OUTPUT_BASE_DIR, dataset_folder)
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def plot_exec_time_comparison(dfs: list[pd.DataFrame], algos: list[str], exp_index: str, out_dir: str, dataset_label: str):
    plt.figure(figsize=(8, 5))

    data = [df["exec_time"] for df in dfs]
    labels = [a.upper() for a in algos]

    plt.boxplot(data, labels=labels, showfliers=True)
    plt.ylabel("Execution Time (s)")
    plt.title(f"Distribusi Execution Time per Task (Percobaan {exp_index}, Dataset={dataset_label})")
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    out_path = os.path.join(out_dir, f"exec_time_comparison_exp_{exp_index}.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Gambar disimpan: {out_path}")


def plot_makespan_bar(dfs: list[pd.DataFrame], algos: list[str], exp_index: str, out_dir: str, dataset_label: str):
    plt.figure(figsize=(6 + 0.5 * len(algos), 4))

    makespans = [df["finish_time"].max() for df in dfs]
    labels = [a.upper() for a in algos]

    plt.bar(labels, makespans, color=plt.cm.tab10.colors[: len(labels)])
    plt.ylabel("Makespan (s)")
    plt.title(f"Perbandingan Makespan (Percobaan {exp_index}, Dataset={dataset_label})")
    for i, v in enumerate(makespans):
        plt.text(i, v, f"{v:.2f}s", ha="center", va="bottom")

    plt.grid(axis="y", linestyle="--", alpha=0.5)

    out_path = os.path.join(out_dir, f"makespan_comparison_exp_{exp_index}.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Gambar disimpan: {out_path}")


def plot_vm_load_comparison(dfs: list[pd.DataFrame], algos: list[str], exp_index: str, out_dir: str, dataset_label: str):
    # Hitung total exec_time per VM untuk setiap algoritma
    vm_names = set()
    vm_loads_per_algo = []

    for df in dfs:
        load = df.groupby("vm_assigned")["exec_time"].sum()
        vm_names.update(load.index)
        vm_loads_per_algo.append(load)

    vms = sorted(vm_names)
    x = range(len(vms))
    width = 0.8 / max(1, len(algos))  # bagi lebar antar algoritma

    plt.figure(figsize=(8 + len(algos), 5))

    for j, (algo, load) in enumerate(zip(algos, vm_loads_per_algo)):
        vals = [load.get(vm, 0.0) for vm in vms]
        offsets = [i - 0.4 + width / 2 + j * width for i in x]
        plt.bar(offsets, vals, width=width, label=algo.upper())

    plt.xticks(list(x), vms)
    plt.ylabel("Total Execution Time per VM (s)")
    plt.title(f"Perbandingan Load per VM (Percobaan {exp_index}, Dataset={dataset_label})")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    out_path = os.path.join(out_dir, f"vm_load_comparison_exp_{exp_index}.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Gambar disimpan: {out_path}")


def main():
    """Main function.

    Cara pakai:
        uv run grapich_comparison.py <exp_index> <algo1> [algo2 ...] [-- dataset]

    Keterangan dataset:
      - Jika tidak diisi: dianggap 'default' (results/<algo>/default/<exp>.csv)
      - Jika diisi nama pendek yang sama seperti scheduler (random_simple, low_high, random_stratified),
        maka akan mencari di folder yang sudah dinormalisasi (random-simple, low-high, random-stratified).
      - Jika diisi path ke file dataset, nama folder akan mengikuti nama file (tanpa ekstensi).

    Contoh:
        uv run grapich_comparison.py 1 shc pso rr fcfs
        uv run grapich_comparison.py 2 shc pso -- random_simple
        uv run grapich_comparison.py 3 shc pso -- datasets/dataset_random_simple.txt
    """

    if len(sys.argv) < 3:
        print(
            "Usage: uv run grapich_comparison.py <exp_index> <algo1> [algo2 ...] [-- dataset]",
            file=sys.stderr,
        )
        sys.exit(1)

    exp_index = sys.argv[1]

    # Parse algoritma dan opsional dataset (menggunakan '--' sebagai pemisah)
    raw_args = sys.argv[2:]
    algos: list[str] = []
    dataset_arg: str | None = None

    i = 0
    while i < len(raw_args):
        if raw_args[i] == "--":
            i += 1
            if i < len(raw_args):
                dataset_arg = raw_args[i]
            break
        else:
            algos.append(raw_args[i].lower())
            i += 1

    if not algos:
        print("Error: Minimal satu algoritma harus disebutkan.", file=sys.stderr)
        sys.exit(1)

    dataset_folder, dataset_label = normalise_dataset_name(dataset_arg)
    out_dir = ensure_output_dir(dataset_folder)

    dfs: list[pd.DataFrame] = []
    for algo in algos:
        df = load_results(algo, exp_index, dataset_folder)
        df = df.sort_values("index")
        dfs.append(df)

    # Buat grafik perbandingan berdasarkan daftar algoritma, percobaan, dan dataset yang sama
    plot_exec_time_comparison(dfs, algos, exp_index, out_dir, dataset_label)
    plot_makespan_bar(dfs, algos, exp_index, out_dir, dataset_label)
    plot_vm_load_comparison(dfs, algos, exp_index, out_dir, dataset_label)


if __name__ == "__main__":
    main()
