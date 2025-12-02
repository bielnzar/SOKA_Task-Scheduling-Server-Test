from collections import namedtuple

VM = namedtuple('VM', ['name', 'ip', 'cpu_cores', 'ram_gb'])
Task = namedtuple('Task', ['id', 'name', 'index', 'cpu_load'])


def round_robin_scheduler(tasks: list[Task], vms: list[VM]) -> dict:
    """Penjadwalan sederhana menggunakan algoritma Round Robin.

    Setiap task dialokasikan ke VM secara bergiliran (vm1, vm2, vm3, vm4, kembali ke vm1, dst.).
    Mengembalikan mapping {task_id: vm_name} seperti SHC dan PSO.
    """
    if not tasks or not vms:
        return {}

    vm_names = [vm.name for vm in vms]
    num_vms = len(vm_names)

    assignment: dict[int, str] = {}
    for i, task in enumerate(tasks):
        vm_index = i % num_vms
        assignment[task.id] = vm_names[vm_index]

    print("Round Robin: penugasan tugas selesai.")
    return assignment
