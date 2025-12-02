from collections import namedtuple

VM = namedtuple('VM', ['name', 'ip', 'cpu_cores', 'ram_gb'])
Task = namedtuple('Task', ['id', 'name', 'index', 'cpu_load'])


def fcfs_scheduler(tasks: list[Task], vms: list[VM]) -> dict:
    """Penjadwalan dengan prinsip First-Come First-Served (FCFS).

    - Task dilayani sesuai urutan kedatangan (urutan dalam list `tasks`).
    - Untuk tiap task yang datang, ia ditempatkan ke VM dengan *estimasi waktu selesai* paling cepat
      berdasarkan total beban saat ini (greedy load balancing) menggunakan cpu_load / cpu_cores.

    Mengembalikan mapping {task_id: vm_name} seperti SHC, PSO, dan RR.
    """
    if not tasks or not vms:
        return {}

    # Inisialisasi beban (estimated time) per VM
    vm_loads = {vm.name: 0.0 for vm in vms}
    vm_cores = {vm.name: vm.cpu_cores for vm in vms}

    assignment: dict[int, str] = {}

    for task in tasks:
        # Estimasi waktu eksekusi task pada tiap VM jika ditempatkan di sana
        best_vm = None
        best_completion_time = None

        for vm in vms:
            exec_time = task.cpu_load / vm_cores[vm.name]
            completion_time = vm_loads[vm.name] + exec_time

            if best_completion_time is None or completion_time < best_completion_time:
                best_completion_time = completion_time
                best_vm = vm.name

        # Assign task ke VM terpilih & update beban VM tersebut
        assignment[task.id] = best_vm
        vm_loads[best_vm] += task.cpu_load / vm_cores[best_vm]

    print("FCFS: penugasan tugas selesai (menghormati urutan kedatangan, load-aware).")
    return assignment
