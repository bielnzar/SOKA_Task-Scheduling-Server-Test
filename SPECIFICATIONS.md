# SPECIFICATIONS

---

**Metode Cloudlet Scheduler**:
- `shc`  -> Stochastic Hill Climbing (`shc_algorithm.py`)
- `pso`  -> Particle Swarm Optimization (`pso_algorithm.py`)
- `rr`   -> Round Robin (`rr_algorithm.py`)
- `fcfs` -> First-Come First-Served (`fcfs_algorithm.py`)

Catatan: ini adalah scheduler level-aplikasi (penetapan task -> VM). Kode tidak menggunakan CloudSim/objek `CloudletScheduler` khusus.

**Jumlah Datacenter / Host / VM / Power per Host**:
- Jumlah Datacenter: Tidak didefinisikan dalam kode.
- Jumlah Host per Datacenter: Tidak didefinisikan.
- Jumlah VM per Host: Tidak didefinisikan (VM didefinisikan langsung sebagai entitas terpisah).
- Jumlah VM yang tersedia di konfigurasi: 4 (lihat `VM_SPECS` di `scheduler.py`).
- Power per Host: Tidak didefinisikan (tidak ada model daya / power).

**Sumber Kode Relevan**:
  - `scheduler.py`:
  - `VM_SPECS` (variabel yang mendefinisikan VM yang tersedia)
  - `get_task_load(index)` (rumus untuk `cpu_load` / length cloudlet)

---

**Spesifikasi VM (yang tersedia dari kode)**

`VM_SPECS` pada `scheduler.py` (nilai langsung di code):

- `vm1`:
  - `ip`: dari env `VM1_IP` (lihat `.env` jika ada)
  - `cpu` (core): 1
  - `ram_gb`: 1

- `vm2`:
  - `ip`: dari env `VM2_IP`
  - `cpu` (core): 2
  - `ram_gb`: 2

- `vm3`:
  - `ip`: dari env `VM3_IP`
  - `cpu` (core): 4
  - `ram_gb`: 4

- `vm4`:
  - `ip`: dari env `VM4_IP`
  - `cpu` (core): 8
  - `ram_gb`: 4

Parameter VM lain yang diminta tapi TIDAK didefinisikan di kode saat ini:
- Storage: Tidak didefinisikan
- Bandwidth: Tidak didefinisikan
- MIPS (PE MIPS): Tidak didefinisikan
- Cost: Tidak didefinisikan

Jika Anda ingin nilai-nilai ini tersedia, saya bisa menambahkan field di `VM_SPECS` seperti `storage_gb`, `bandwidth_mbps`, `mips`, `cost` dan menyesuaikan algoritma/penulisan hasil.

---

**Spesifikasi Host Datacenter**

---

**Spesifikasi Cloudlet / Task**

Task structure di kode (`scheduler.py` dan algoritma):
```
Task = namedtuple('Task', ['id', 'name', 'index', 'cpu_load'])
```

- `Length` (ekuivalen kerja / MI dalam model sederhana kode):
  - Dihitung oleh `get_task_load(index)` di `scheduler.py`:
    - `cpu_load = index * index * 10000`  (index^2 * 10000)

  - Nilai `cpu_load` untuk index 1..10:
    - index 1  → 10_000
    - index 2  → 40_000
    - index 3  → 90_000
    - index 4  → 160_000
    - index 5  → 250_000
    - index 6  → 360_000
    - index 7  → 490_000
    - index 8  → 640_000
    - index 9  → 810_000
    - index 10 → 1_000_000

- `File Size` / `Output Size`: Tidak didefinisikan di kode (tidak ada field pada `Task` untuk ini).

Catatan: `cpu_load` digunakan oleh algoritma sebagai basis estimasi waktu eksekusi sederhana: exec_time ≈ cpu_load / vm.cpu_cores

---

**Ringkasan singkat: tersedia vs tidak tersedia**

- Tersedia langsung dari kode:
  - Daftar algoritma penjadwalan (SHC, PSO, RR, FCFS)
  - Jumlah dan spesifikasi dasar VM: 4 VM (core + RAM)
  - Rumus `cpu_load` per task (index^2 * 10000)

- Tidak tersedia / perlu ditambahkan jika diinginkan:
  - Datacenter/Host model eksplisit (jumlah datacenter, host per datacenter)
  - Storage, Bandwidth, PE MIPS, Cost, Power model
  - File size / output size untuk cloudlet

---