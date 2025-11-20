# Penjelasan Algoritma Particle Swarm Optimization (PSO)

Dokumen ini menjelaskan konsep dasar **Particle Swarm Optimization (PSO)** dengan bahasa yang sederhana dan dikaitkan langsung dengan implementasi di file `pso_algorithm.py`.

---

## 1. Intuisi Dasar PSO

Bayangkan sekelompok burung yang sedang mencari makanan di suatu area:

- Setiap burung **tidak tahu** di mana makanan yang paling banyak.
- Setiap burung **mencoba-coba posisi baru** di area tersebut.
- Setiap burung **mengingat posisi terbaik** yang pernah ia temukan.
- Burung-burung juga **berbagi informasi**: mereka mengetahui posisi terbaik yang pernah ditemukan oleh kawanan.

Dengan cara itu, lama-kelamaan kawanan burung akan **berkumpul** di area yang memang memiliki makanan terbanyak.

PSO meniru perilaku ini untuk **mencari solusi terbaik** dari suatu masalah optimasi.

- Burung → disebut **partikel** (particle).
- Posisi burung → **solusi** (misalnya penugasan task→VM).
- Makanan terbanyak → **nilai fungsi objektif terbaik** (di repo ini: **makespan terkecil**).

---

## 2. Istilah Penting dalam PSO

Setiap partikel memiliki:

1. **Posisi (position)**  
   - Mewakili **solusi saat ini**.
   - Di repo ini: posisi partikel menentukan untuk **setiap task, VM mana yang dipilih**.

2. **Kecepatan (velocity)**  
   - Bukan kecepatan fisik, tapi **arah dan seberapa besar perubahan posisi** di iterasi berikutnya.

3. **Personal best (pbest)**  
   - Posisi terbaik (nilai fungsi objektif paling bagus) yang pernah dicapai partikel itu sendiri.

4. **Global best (gbest)**  
   - Posisi terbaik yang pernah ditemukan **seluruh swarm** (semua partikel).

Tujuan PSO:  
Mencari posisi dengan **nilai fungsi objektif paling baik** dengan memanfaatkan pergerakan partikel serta informasi `pbest` dan `gbest`.

---

## 3. Representasi Solusi di Repo Ini

Di file `pso_algorithm.py`, kita ingin menyelesaikan masalah:

> "Bagaimana cara membagi sejumlah *task* ke beberapa *VM* sehingga **makespan** (waktu selesai paling akhir) seminimal mungkin?"

### 3.1. Data dasar

- `Task` punya properti `id` dan `cpu_load`.
- `VM` punya `name` dan `cpu_cores`.

### 3.2. Posisi partikel

Setiap partikel menyimpan:

```python
self.position = [random.uniform(0, len(vm_names) - 1) for _ in range(self.dimension)]
```

- `dimension` = jumlah task.
- Setiap elemen `position[d]` adalah **bilangan real** yang nanti akan di-mapping ke **indeks VM**.

Kemudian, posisi ini diubah menjadi solusi diskrit `task → vm` lewat:

```python
vm_index = int(round(pos_val))
vm_index = max(0, min(vm_index, len(self.vm_names) - 1))
assignment[task_id] = self.vm_names[vm_index]
```

Artinya:
- Nilai real di posisi dipersempit menjadi indeks VM terdekat (0, 1, 2, 3 untuk 4 VM).
- Sehingga: **satu partikel = satu assignment lengkap semua task ke VM**.

---

## 4. Fungsi Objektif (Cost Function)

Fungsi objektif di PSO ini sama dengan yang dipakai di SHC:

```python
def calculate_estimated_makespan(solution, tasks_dict, vms_dict) -> float:
    vm_loads = {vm.name: 0.0 for vm in vms_dict.values()}

    for task_id, vm_name in solution.items():
        task = tasks_dict[task_id]
        vm = vms_dict[vm_name]
        estimated_time = task.cpu_load / vm.cpu_cores
        vm_loads[vm_name] += estimated_time

    return max(vm_loads.values())
```

Penjelasan:
- Untuk setiap VM, kita hitung **total waktu estimasi** semua task yang masuk ke VM tersebut.
- Estimasi waktu task = `cpu_load / jumlah core VM`.
- **Makespan** = waktu VM yang paling lama (nilai maksimum `vm_loads`).

PSO akan mencoba **meminimalkan** nilai makespan ini.

---

## 5. Rumus Update Velocity dan Position

Di dalam `pso_scheduler`, untuk setiap iterasi dan setiap dimensi `d` dari partikel:

```python
r1 = random.random()
r2 = random.random()

cognitive_component = cognitive * r1 * (particle.best_position[d] - particle.position[d])
social_component = social * r2 * (global_best_position[d] - particle.position[d])

particle.velocity[d] = (
    inertia * particle.velocity[d]
    + cognitive_component
    + social_component
)
particle.position[d] += particle.velocity[d]
```

Makna tiap bagian:

- `inertia * velocity`  
  Menjaga **arah gerakan sebelumnya**. Kalau inertia besar → pergerakan lebih stabil/"ngotot".

- `cognitive_component`  
  Menarik partikel menuju **posisi terbaiknya sendiri (pbest)**.

- `social_component`  
  Menarik partikel menuju **posisi terbaik swarm (gbest)**.

Angka pengali:

- `inertia` (misal 0.7) → seberapa besar pengaruh kecepatan lama.
- `cognitive` (misal 1.5) → seberapa kuat partikel percaya pengalaman dirinya.
- `social` (misal 1.5) → seberapa kuat partikel mengikuti kawanan.

Setelah posisi diupdate, nilai posisi di-*clamp* agar tetap dalam rentang indeks VM:

```python
max_index = len(vm_names) - 1
if particle.position[d] < 0:
    particle.position[d] = 0.0
elif particle.position[d] > max_index:
    particle.position[d] = float(max_index)
```

---

## 6. Alur Lengkap PSO di `pso_scheduler`

Ringkasannya sebagai berikut:

1. **Inisialisasi**
   - Bentuk `vms_dict`, `tasks_dict`, `vm_names`, dan daftar `task_ids`.
   - Buat swarm berisi beberapa `Particle` dengan posisi awal acak.

2. **Evaluasi awal**
   - Untuk setiap partikel:
     - Bangun solusi diskrit (assignment task→VM).
     - Hitung makespan dengan `calculate_estimated_makespan`.
     - Set sebagai `particle.best_cost` dan `global_best_cost` jika paling baik.

3. **Iterasi PSO** (loop sejumlah `iterations`):
   - Untuk setiap partikel:
     1. Update **velocity** dan **position** setiap dimensi.
     2. Bangun solusi baru dari posisi baru.
     3. Hitung cost (makespan) baru.
     4. Jika cost baru lebih baik dari `particle.best_cost` → update **pbest**.
     5. Jika cost baru lebih baik dari `global_best_cost` → update **gbest**.
   - Sesekali mencetak nilai makespan terbaik saat ini ke console.

4. **Hasil akhir**
   - Setelah iterasi selesai, posisi `global_best_position` digunakan untuk membangun assignment terbaik.
   - Fungsi `pso_scheduler` mengembalikan mapping:

     ```python
     {task_id: vm_name}
     ```

   - Struktur ini sama dengan output `stochastic_hill_climb`, sehingga `scheduler.py` bisa memakai keduanya dengan cara yang sama.

---

## 7. Perbandingan Singkat SHC vs PSO

**Stochastic Hill Climbing (SHC)**:
- Hanya punya **satu** solusi yang berjalan.
- Setiap langkah, pindahkan satu task ke VM lain (tetangga) dan **hanya menerima** jika solusi baru lebih baik.
- Bisa cepat, tapi lebih mudah **terjebak di local optimum**.

**Particle Swarm Optimization (PSO)**:
- Punya **banyak solusi (partikel)** yang dieksplorasi bersamaan.
- Setiap partikel belajar dari pengalaman sendiri (`pbest`) dan dari yang terbaik global (`gbest`).
- Biasanya lebih baik dalam **eksplorasi ruang solusi** dan cenderung memberi solusi yang lebih stabil/baik, tapi dengan **biaya komputasi lebih besar**.

Dalam konteks repo ini, PSO diharapkan bisa:
- Menghasilkan penugasan task→VM dengan **makespan lebih kecil**.
- Menyeimbangkan load antar VM dengan lebih baik dibanding SHC (imbalance degree lebih kecil), tergantung parameter dan dataset.

---

## 8. Cara Menggunakan PSO di Proyek Ini

1. Pastikan environment sudah siap:

   ```bash
   uv sync
   ```

2. Jalankan scheduler dengan PSO:

   ```bash
   uv run scheduler.py pso
   ```

3. Hasil akan tersimpan sebagai:

   ```text
   results/pso_results.csv
   ```

4. Untuk membandingkan dengan SHC secara visual, jalankan:

   ```bash
   uv run grapich_comparison.py
   ```

   Gambar perbandingan akan muncul di folder `grapich/`.

---

Dengan penjelasan ini, kamu bisa:
- Mengerti **konsep dasar PSO**.
- Memahami bagaimana **PSO direpresentasikan dan diimplementasikan** di `pso_algorithm.py`.
- Menghubungkan hasil PSO dengan metrik yang keluar di `scheduler.py` dan grafik perbandingan yang dibuat oleh `grapich_comparison.py`.
