import os

import pandas as pd
import matplotlib.pyplot as plt


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
OUTPUT_DIR = os.path.join(BASE_DIR, 'grapich')

SHC_FILE = os.path.join(RESULTS_DIR, 'shc_results.csv')
PSO_FILE = os.path.join(RESULTS_DIR, 'pso_results.csv')


def load_results(path: str, algo_name: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File hasil untuk {algo_name} tidak ditemukan: {path}")

    df = pd.read_csv(path)

    # Pastikan kolom waktu bertipe numerik
    for col in ["start_time", "exec_time", "finish_time", "wait_time"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["algo"] = algo_name
    return df


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def plot_exec_time_comparison(shc_df: pd.DataFrame, pso_df: pd.DataFrame):
    plt.figure(figsize=(8, 5))

    plt.boxplot(
        [shc_df["exec_time"], pso_df["exec_time"]],
        labels=["SHC", "PSO"],
        showfliers=True,
    )
    plt.ylabel("Execution Time (s)")
    plt.title("Perbandingan Distribusi Execution Time per Task")
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    out_path = os.path.join(OUTPUT_DIR, "exec_time_comparison.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Gambar disimpan: {out_path}")


def plot_makespan_bar(shc_df: pd.DataFrame, pso_df: pd.DataFrame):
    # Makespan = max(finish_time)
    shc_makespan = shc_df["finish_time"].max()
    pso_makespan = pso_df["finish_time"].max()

    plt.figure(figsize=(6, 4))

    plt.bar(["SHC", "PSO"], [shc_makespan, pso_makespan], color=["tab:blue", "tab:orange"])
    plt.ylabel("Makespan (s)")
    plt.title("Perbandingan Makespan SHC vs PSO")
    for i, v in enumerate([shc_makespan, pso_makespan]):
        plt.text(i, v, f"{v:.2f}s", ha="center", va="bottom")

    plt.grid(axis="y", linestyle="--", alpha=0.5)

    out_path = os.path.join(OUTPUT_DIR, "makespan_comparison.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Gambar disimpan: {out_path}")


def plot_vm_load_comparison(shc_df: pd.DataFrame, pso_df: pd.DataFrame):
    # Total exec_time per VM
    shc_load = shc_df.groupby("vm_assigned")["exec_time"].sum()
    pso_load = pso_df.groupby("vm_assigned")["exec_time"].sum()

    vms = sorted(set(shc_load.index).union(pso_load.index))
    shc_vals = [shc_load.get(vm, 0.0) for vm in vms]
    pso_vals = [pso_load.get(vm, 0.0) for vm in vms]

    x = range(len(vms))
    width = 0.35

    plt.figure(figsize=(8, 5))
    plt.bar([i - width / 2 for i in x], shc_vals, width=width, label="SHC")
    plt.bar([i + width / 2 for i in x], pso_vals, width=width, label="PSO")

    plt.xticks(list(x), vms)
    plt.ylabel("Total Execution Time per VM (s)")
    plt.title("Perbandingan Load per VM (SHC vs PSO)")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    out_path = os.path.join(OUTPUT_DIR, "vm_load_comparison.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Gambar disimpan: {out_path}")


def main():
    ensure_output_dir()

    shc_df = load_results(SHC_FILE, "SHC")
    pso_df = load_results(PSO_FILE, "PSO")

    # Sort by index supaya urutan konsisten
    shc_df = shc_df.sort_values("index")
    pso_df = pso_df.sort_values("index")

    plot_exec_time_comparison(shc_df, pso_df)
    plot_makespan_bar(shc_df, pso_df)
    plot_vm_load_comparison(shc_df, pso_df)


if __name__ == "__main__":
    main()
