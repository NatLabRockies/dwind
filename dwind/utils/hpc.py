import time

from rich.table import Table
from rex.utilities.hpc import SLURM


def convert_seconds_for_print(time: float) -> str:
    """Convert number of seconds to number of hours, minutes, and seconds."""
    div = ((60, "seconds"), (60, "minutes"), (24, "hours"))

    result = []
    value = time
    for divisor, label in div:
        if not divisor:
            remainder = value
            if not remainder:
                break
        else:
            value, remainder = divmod(value, divisor)
            if not value and not remainder:
                break
        if remainder == 1:
            label = label[:-1]

        # 0.2 second precision for seconds, and no decimals otherwise
        if result:
            result.append(f"{remainder:,.0f} {label}")
        else:
            result.append(f"{remainder:.1f} {label}")
    if result:
        return ", ".join(reversed(result))
    return "0"


def update_status(job_status: dict) -> dict:
    """Get an updated status and timing statistics for all running jobs on the HPC.

    Args:
        job_status (dict): Dictionary of job id (primary key) with sub keys of "status",
            "start_time" (initial or start of run status), "wait", and "run".

    Returns:
        dict: Dictionary of updated statuses and timing statistics for all current queued and
            running jobs.
    """
    slurm = SLURM()
    update = {}
    for job, vals in job_status.items():
        original_status = vals["status"]
        if original_status in ("CG", "CF", "None", None):
            continue
        new_status = slurm.check_status(job_id=job)
        if new_status == "PD":
            update[job] = vals | {"status": new_status, "wait": time.perf_counter() - vals["start"]}
        elif new_status == "R":
            if original_status != "R":
                update[job] = vals | {
                    "status": new_status,
                    "wait": time.perf_counter() - vals["start"],
                    "start": time.perf_counter(),
                }
            else:
                update[job] = vals | {"run": time.perf_counter() - vals["start"]}
        elif new_status in ("CG", "CF", "None", None):
            update[job] = vals | {"status": new_status, "run": time.perf_counter() - vals["start"]}
        else:
            raise ValueError(f"Unaccounted for status code: {new_status}")
    return update


def generate_table(job_status: dict) -> tuple[Table, bool]:
    """Generate the job status run time statistics table.

    Args:
        job_status (dict): Dictionary of job id (primary key) with sub keys of "status",
            "start_time" (initial or start of run status), "wait", and "run".

    Returns:
        Table: ``rich.Table`` of human readable statistics.
        bool: True if all jobs are complete, otherwise False.
    """
    table = Table()
    table.add_column("Job ID")
    table.add_column("Status")
    table.add_column("Wait time")
    table.add_column("Run time")

    for job, vals in job_status.items():
        status = vals["status"]
        _wait = vals["wait"]
        _run = vals["run"]
        table.add_row(
            job, status, convert_seconds_for_print(_wait), convert_seconds_for_print(_run)
        )
    done = all(el["status"] in ("CG", None) for el in job_status.values())
    return table, done
