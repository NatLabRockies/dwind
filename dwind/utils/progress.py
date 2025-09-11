import numpy as np
from joblib import Parallel, delayed
from threading import Thread
from rich.progress import Progress, BarColumn, TimeRemainingColumn, TextColumn
from rich.console import Console
from rich.live import Live
import time

# Define the number of tasks and create a shared memory numpy array to hold their progress
num_tasks = 4
progress_array = np.memmap("progress.mmap2", dtype=np.float32, mode="w+", shape=N)

# Define a function that performs a task and updates the progress array
def perform_task(task_idx, progress_array):
    for i in range(100):
        # Do some work here
        # ...

        # Update the progress array
        time.sleep(0.1)
        progress_array[task_idx] = i / 100

    # Update the progress array to 100% on completion
    progress_array[task_idx] = 1

# Define a function to continuously update the Rich progress bar
def update_progress_bar(
    progress_array=progress_array,
    num_tasks=num_tasks,
):
    with Progress(
        TextColumn("[bold blue]{task.fields[name]}"),
        BarColumn(),
        TextColumn("[bold green]{task.fields[status]}"),
        TimeRemainingColumn(),
        # console=console,
    ) as progress:
        tasks = [
            progress.add_task(
                description=f"Task {i}",
                name=f"Task {i}",
                status="pending",
                total=100,
            )
            for i in range(num_tasks)
        ]

        while not all(progress_array == 1):
            for i, task in enumerate(tasks):
                progress.update(task, completed=int(progress_array[i] * 100))
            time.sleep(0.1 * 2 ** abs(*np.random.randn(1)))


# Launch the progress bar update function in a separate thread
Thread(target=update_progress_bar, args=[progress_array, num_tasks]).start()

# Launch the tasks in parallel using joblib and the perform_task function
Parallel(n_jobs=-2, backend="loky")(
    delayed(perform_task)(i, progress_array) for i in range(num_tasks)
)
