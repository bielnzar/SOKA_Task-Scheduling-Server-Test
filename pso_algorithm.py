import random
from collections import namedtuple

# Reuse compatible structures with scheduler.py
VM = namedtuple('VM', ['name', 'ip', 'cpu_cores', 'ram_gb'])
Task = namedtuple('Task', ['id', 'name', 'index', 'cpu_load'])


def calculate_estimated_makespan(solution: dict, tasks_dict: dict, vms_dict: dict) -> float:
    """Cost function: estimated makespan based on total CPU load / cores per VM."""
    vm_loads = {vm.name: 0.0 for vm in vms_dict.values()}

    for task_id, vm_name in solution.items():
        task = tasks_dict[task_id]
        vm = vms_dict[vm_name]
        estimated_time = task.cpu_load / vm.cpu_cores
        vm_loads[vm_name] += estimated_time

    return max(vm_loads.values()) if vm_loads else 0.0


class Particle:
    def __init__(self, task_ids: list[int], vm_names: list[str]):
        # Position and velocity are represented in continuous space per task
        # but will be mapped to discrete VM indices when building a solution.
        self.task_ids = task_ids
        self.vm_names = vm_names
        self.dimension = len(task_ids)

        # Continuous position & velocity vectors
        self.position = [random.uniform(0, len(vm_names) - 1) for _ in range(self.dimension)]
        self.velocity = [0.0 for _ in range(self.dimension)]

        # Best known position and its cost
        self.best_position = list(self.position)
        self.best_cost = float('inf')

    def build_solution(self) -> dict:
        """Map continuous position to a discrete task->vm assignment dict."""
        assignment: dict[int, str] = {}
        for idx, task_id in enumerate(self.task_ids):
            pos_val = self.position[idx]
            # Clamp and round to nearest VM index
            vm_index = int(round(pos_val))
            vm_index = max(0, min(vm_index, len(self.vm_names) - 1))
            assignment[task_id] = self.vm_names[vm_index]
        return assignment


def pso_scheduler(
    tasks: list[Task],
    vms: list[VM],
    iterations: int = 100,
    swarm_size: int = 30,
    inertia: float = 0.7,
    cognitive: float = 1.5,
    social: float = 1.5,
) -> dict:
    """Particle Swarm Optimization for task-to-VM assignment.

    Returns mapping {task_id: vm_name}, same as stochastic_hill_climb.
    """
    print(f"Memulai PSO (iterasi={iterations}, swarm_size={swarm_size})...")

    if not tasks or not vms:
        return {}

    vms_dict = {vm.name: vm for vm in vms}
    tasks_dict = {task.id: task for task in tasks}
    vm_names = list(vms_dict.keys())
    task_ids = [task.id for task in tasks]

    # Inisialisasi swarm
    swarm: list[Particle] = [Particle(task_ids, vm_names) for _ in range(swarm_size)]

    global_best_position = None
    global_best_cost = float('inf')

    # Hitung biaya awal untuk setiap partikel
    for i, particle in enumerate(swarm):
        solution = particle.build_solution()
        cost = calculate_estimated_makespan(solution, tasks_dict, vms_dict)
        particle.best_cost = cost
        particle.best_position = list(particle.position)

        if cost < global_best_cost:
            global_best_cost = cost
            global_best_position = list(particle.position)

    print(f"Estimasi Makespan Awal Terbaik (swarm): {global_best_cost:.2f}")

    # Iterasi utama PSO
    for it in range(iterations):
        for particle in swarm:
            for d in range(particle.dimension):
                r1 = random.random()
                r2 = random.random()

                cognitive_component = cognitive * r1 * (particle.best_position[d] - particle.position[d])
                social_component = 0.0
                if global_best_position is not None:
                    social_component = social * r2 * (global_best_position[d] - particle.position[d])

                # Update velocity & position
                particle.velocity[d] = (
                    inertia * particle.velocity[d]
                    + cognitive_component
                    + social_component
                )
                particle.position[d] += particle.velocity[d]

                # Soft clamp posisi dalam range VM index
                max_index = len(vm_names) - 1
                if particle.position[d] < 0:
                    particle.position[d] = 0.0
                elif particle.position[d] > max_index:
                    particle.position[d] = float(max_index)

            # Evaluasi solusi baru
            solution = particle.build_solution()
            cost = calculate_estimated_makespan(solution, tasks_dict, vms_dict)

            # Update personal best
            if cost < particle.best_cost:
                particle.best_cost = cost
                particle.best_position = list(particle.position)

            # Update global best
            if cost < global_best_cost:
                global_best_cost = cost
                global_best_position = list(particle.position)

        if (it + 1) % max(1, iterations // 10) == 0:
            print(f"Iterasi {it+1}/{iterations}: Estimasi Makespan Terbaik Saat Ini: {global_best_cost:.2f}")

    print(f"PSO Selesai. Estimasi Makespan Terbaik: {global_best_cost:.2f}")

    # Bangun assignment final dari global best
    if global_best_position is None:
        return {}

    # Recreate a particle-like view to reuse build_solution
    final_particle = Particle(task_ids, vm_names)
    final_particle.position = list(global_best_position)
    best_assignment = final_particle.build_solution()

    return best_assignment
