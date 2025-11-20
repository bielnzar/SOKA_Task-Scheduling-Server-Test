# Pengujian Algoritma Task Scheduler pada Server IT

Repo ini merupakan kode dari server yang digunakan dalam pengujian Task Scheduling pada Server IT serta contoh algoritma scheduler untuk keperluan mata kuliah **Strategi Optimasi Komputasi Awan (SOKA)**.

Saat ini tersedia **dua algoritma penjadwalan** yang dapat digunakan dan dibandingkan:
- **Stochastic Hill Climbing (SHC)** – algoritma awal/bawaan.
- **Particle Swarm Optimization (PSO)** – algoritma tambahan untuk perbandingan performa.

Hasil eksekusi kedua algoritma dapat disimpan ke file CSV dan divisualisasikan menggunakan script pembuat grafik.

## Cara Penggunaan - Dev

1. Install `uv` sebagai dependency manager. Lihat [link berikut](https://docs.astral.sh/uv/getting-started/installation/)

2. Install semua requirement

```bash
uv sync
```

3. Buat file `.env` kemudian isi menggunakan variabel pada `.env.example`. Isi nilai setiap variabel sesuai kebutuhan

```conf
VM1_IP=""
VM2_IP=""
VM3_IP=""
VM4_IP=""

VM_PORT=5000
```

4. Algoritma penjadwalan yang tersedia

- **Stochastic Hill Climbing (SHC)**  
  Implementasi terdapat pada file `shc_algorithm.py`.  
  Algoritma ini mencari solusi dengan melakukan perbaikan bertahap pada penugasan task→VM dan hanya menerima solusi tetangga yang lebih baik.

  ![shc_algorithm](https://i.sstatic.net/HISbC.png)

- **Particle Swarm Optimization (PSO)**  
  Implementasi terdapat pada file `pso_algorithm.py`.  
  Algoritma ini menggunakan sekumpulan partikel (swarm) yang masing-masing merepresentasikan solusi penjadwalan. Setiap partikel bergerak di ruang solusi dengan mempertimbangkan pengalaman terbaiknya sendiri (pbest) dan terbaik global (gbest) untuk meminimalkan estimasi makespan.

5. Untuk menjalankan server, jalankan docker

```bash
docker compose build --no-cache
docker compose up -d
```

Server akan berjalan pada port `5000` (dapat diubah melalui konfigurasi jika diperlukan) dan menyediakan endpoint:
- `GET /health` – untuk pengecekan status server.
- `GET /task/<index>` – untuk mensimulasikan eksekusi task dengan indeks `1-10`.

6. Inisiasi Dataset untuk scheduler. Buat file `dataset.txt` kemudian isi dengan dataset berupa angka 1 - 10. Berikut adalah contohnya:

```txt
6
5
8
2
10
3
4
4
7
3
9
1
7
9
1
8
2
5
6
10
```

Anda juga dapat menggunakan dataset yang sudah tersedia pada folder `datasets/` (misalnya `datasets/randomSimple/RandSimple1000.txt`, dll) dengan cara menyalin/rename file tersebut menjadi `dataset.txt`.

7. Menjalankan scheduler

**Catatan:** Pastikan sudah terhubung ke jaringan yang dapat mengakses VM (misal VPN / WiFi ITS).

- Menjalankan dengan **Stochastic Hill Climbing (default)**:

```bash
uv run scheduler.py
# atau
uv run scheduler.py shc
```

- Menjalankan dengan **Particle Swarm Optimization (PSO)**:

```bash
uv run scheduler.py pso
```

8. Hasil eksekusi

Setelah eksekusi sukses, hasil akan disimpan dalam folder `results/`:

- Hasil dengan SHC:
  - `results/shc_results.csv`
- Hasil dengan PSO:
  - `results/pso_results.csv`

Di console juga akan muncul perhitungan metrik untuk analisis, antara lain:
- Makespan (waktu total)
- Throughput (tugas/detik)
- Total CPU Time
- Total Wait Time
- Average Execution Time
- Imbalance Degree (ketidakseimbangan load antar VM)
- Resource Utilization (utilisasi CPU)

Contoh tampilan hasil:

`result.csv`

![result csv](./images/result-csv.png)

`console`

![console](./images/console.png)

9. Membuat grafik perbandingan SHC vs PSO

Untuk membandingkan performa kedua algoritma secara visual, gunakan script `grapich_comparison.py`.

Pastikan kedua file hasil sudah ada:
- `results/shc_results.csv`
- `results/pso_results.csv`

Lalu jalankan:

```bash
uv run grapich_comparison.py
```

Script ini akan menghasilkan beberapa gambar di folder `grapich/`, antara lain:
- `exec_time_comparison.png` – perbandingan distribusi execution time per task.
- `makespan_comparison.png` – perbandingan makespan SHC vs PSO.
- `vm_load_comparison.png` – perbandingan total execution time per VM.

## Hak Cipta / Acknowledgement
Sebagian konten pada repositori ini merupakan turunan atau didasarkan pada garapan dari
[lab-kcks/SOKA-Task-Scheduling-Server-Test](https://github.com/lab-kcks/SOKA-Task-Scheduling-Server-Test).