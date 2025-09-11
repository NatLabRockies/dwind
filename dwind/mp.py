"""Provides the :py:class:`MultiProcess` class for running a model on `NREL's Kestrel HPC system`_.

.. NREL's Kestrel HPC system: https://nrel.github.io/HPC/Documentation/Systems/Kestrel/
"""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
from rich.live import Live
from rex.utilities.hpc import SLURM

from dwind.utils import hpc
from dwind.utils.array import split_by_index


class MultiProcess:
    """Multiprocessing interface for running batch jobs via ``SLURM``.

    Parameters
    ----------
    location : str
        The state name, or an underscore-separated string of "state_county"
    sector : str
        One of "fom" (front of meter) or "btm" (back of the meter).
    scenario : str
        An underscore-separated string for the scenario to be run.
    year : int
        The year-basis for the scenario.
    env : str | Path
        The path to the ``dwind`` Python environment that should be used to run the model.
    n_nodes : int
        Number of nodes to request from the HPC when running an ``sbatch`` job.
    memory : int
        Node memory, in GB.
    walltime : int
        Node walltime request, in hours.
    alloc : str
        The HPC project (allocation) handle that will be charged for running the analysis.
    feature : str
        Additional flags for the SLURM job, using formatting such as ``--qos=high`` or
        ``--depend=[state:job_id]``.
    model_config : str
        The full file path and name of where the model configuration file is located.
    stdout_path : str | Path | None, optional
        The path where all the stdout logs should be written to, by default None. When None,
        ":py:attr:`dir_out` / logs" is used.
    dir_out : _type_, optional
        The path to save the chunked results files, by default Path.getcwd() (current working
        directory).
    """

    def __init__(
        self,
        location: str,
        sector: str,
        scenario: str,
        year: int,
        env: str | Path,
        n_nodes: int,
        memory: int,
        walltime: int,
        allocation: str,
        feature: str,
        repository: str | Path,
        model_config: str,
        stdout_path: str | Path | None = None,
        dir_out: str | Path | None = None,
    ):
        """Initialize the ``SLURM`` interface.

        Parameters
        ----------
        location : str
            The state name, or an underscore-separated string of "state_county"
        sector : str
            One of "fom" (front of meter) or "btm" (back of the meter).
        scenario : str
            An underscore-separated string for the scenario to be run, such as "baseline_2022".
        year : int
            The year-basis for the scenario.
        env : str | Path
            The path to the ``dwind`` Python environment that should be used to run the model.
        n_nodes : int
            Number of nodes to request from the HPC when running an ``sbatch`` job.
        memory : int
            Node memory, in GB.
        walltime : int
            Node walltime request, in hours.
        allocation : str
            The HPC project (allocation) handle that will be charged for running the analysis.
        feature : str
            Additional flags for the SLURM job, using formatting such as ``--qos=high`` or
            ``--depend=[state:job_id]``.
        repository : str | Path
            The path to the dwind repository to use for analysis.
        model_config : str
            The full file path and name of where the model configuration file is located.
        stdout_path : str | Path | None, optional
            The path where all the stdout logs should be written to, by default None. When None,
            ":py:attr:`dir_out` / logs" is used.
        dir_out : str | Path, optional
            The path to save the chunked results files, by default Path.cwd() (current working
            directory).
        """
        self.run_name = f"{location}_{sector}_{scenario}_{year}"
        self.location = location
        self.sector = sector
        self.scenario = scenario
        self.year = year
        self.env = env
        self.n_nodes = n_nodes
        self.memory = memory
        self.walltime = walltime
        self.alloc = allocation
        self.feature = feature
        self.stdout_path = stdout_path
        self.dir_out = dir_out
        self.repository = repository
        self.model_config = model_config

        # Create the output directory if it doesn't already exist
        self.dir_out = Path.cwd() if dir_out is None else Path(self.dir_out).resolve()
        self.out_path = self.dir_out / "chunk_files"
        if not self.out_path.exists():
            self.out_path.mkdir()

        # Create a new path in the output directory for the logs if a path is not provided
        if self.stdout_path is None:
            log_dir = self.out_path / "logs"
            if not log_dir.exists():
                log_dir.mkdir()
            self.stdout_path = log_dir

    def check_status(self, job_ids: list[int], start_time: float):
        """Prints the status of all :py:attr:`jobs` submitted.

        Parameters
        ----------
        job_ids : list[int]
            The list of HPC ``job_id``s to check on.
        start_time : float
            The results of initial ``time.perf_counter()``.
        """
        slurm = SLURM()
        job_status = {
            j: {
                "status": slurm.check_status(job_id=j),
                "start": start_time,
                "wait": time.perf_counter() - start_time,
                "run": 0,
            }
            for j in job_ids
        }
        table, complete = hpc.generate_run_status_table(job_status)
        with Live(table, refresh_per_second=1) as live:
            while not complete:
                time.sleep(5)
                job_status |= hpc.update_status(job_status)
                table, complete = hpc.generate_run_status_table(job_status)
                live.update(table)

    def run_jobs(self, agent_df: pd.DataFrame) -> dict[str, int]:
        """Run :py:attr:`n_jobs` number of jobs for the :py:attr:`agent_df`.

        Args:
            agent_df (pandas.DataFrame): The agent DataFrame to be chunked and analyzed.

        Returns:
            dict[str, int]: Dictionary mapping of each SLURM job id to the chunk run in that job.
        """
        agent_df = agent_df.reset_index(drop=True)
        # chunks = np.array_split(agent_df, self.n_nodes)
        starts, ends = split_by_index(agent_df, self.n_nodes)
        job_chunk_map = {}

        base_cmd_str = f"module load conda; conda activate {self.env};"
        base_cmd_str += " dwind run chunk"

        base_args = f" {self.location}"
        base_args += f" {self.sector}"
        base_args += f" {self.scenario}"
        base_args += f" {self.year}"
        base_args += f" {self.out_path}"
        base_args += f" {self.repository}"
        base_args += f" {self.model_config}"

        if not (agent_path := self.out_path / "agent_chunks").is_dir():
            agent_path.mkdir()

        start_time = time.perf_counter()
        # for i, (start, end) in enumerate(zip(starts, ends, strict=True)):
        for i, (start, end) in enumerate(zip(starts, ends)):  # noqa: B905
            fn = self.out_path / "agent_chunks" / f"agents_{i}.pqt"
            agent_df.iloc[start:end].to_parquet(fn)

            job_name = f"{self.run_name}_{i}"
            cmd_str = f"{base_cmd_str} {i} {base_args}"
            print("cmd:", cmd_str)

            slurm_manager = SLURM()
            job_id, err = slurm_manager.sbatch(
                cmd=cmd_str,
                alloc=self.alloc,
                memory=self.memory,
                walltime=self.walltime,
                feature=self.feature,
                name=job_name,
                stdout_path=self.stdout_path,
            )

            if job_id:
                job_chunk_map[job_id] = i
                print(f"Kicked off job: {job_name}, with SLURM {job_id=} on Eagle.")
            else:
                print(
                    f"{job_name=} was unable to be kicked off due to the following error:\n{err}."
                )

        # Check on the job statuses until they're complete, then aggregate the results
        jobs = [*job_chunk_map]
        self.check_status(jobs, start_time)
        return job_chunk_map
