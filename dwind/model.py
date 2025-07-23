from __future__ import annotations

import logging
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from dwind import Configuration, resource, scenarios, valuation, btm_sizing
from dwind.utils import array


# POTENTIALLY DANGEROUS!
warnings.filterwarnings("ignore")


class Agents:
    """Reponsible for reading in the agent data and storing it for the ``Model`` class.

    Agents are the modified parcels that have been truncated to the largest circle able
    to be contained in the parcel, and contain all of the relevant tax lot and
    geographic variables that would be found in a parcel.

    Parameters
    ---------
    agent_file : str | pathlib.Path
        Either a parquet file (.pqt or .parquet) or pickle file (.pkl or .pickle)
        containing the previously generated agent data.

    Raises:
    ------
    ValueError
        Raised if the :py:attr:`agent_file` does not have a valid file extension for
        either a pickle file (.pkl or .pickle) or a parquet file (.pqt or .parquet).
    """

    def __init__(
        self,
        agent_file: str | Path,
        sector: str | None = None,
        model_config: str | Path | None = None,
        *,
        resource_year: int = 2018,
    ):
        self.agent_file = Path(agent_file).resolve()
        self.sector = sector
        self.config = model_config
        self.resource_year = resource_year
        self._load_agents()

    @classmethod
    def load_and_prepare_agents(
        cls,
        agent_file: str | Path,
        sector: str,
        model_config: str | Path,
        *,
        save_results: bool = False,
        file_name: str | Path | None = None,
    ) -> pd.DataFrame:
        """Load and prepare the agent files to run through ``Model``.

        Args:
            agent_file (str | Path): The full file path of the agent parquet, CSV, or pickle data.
            save_results (bool, optional): True to save any updates to the data. Defaults to False.
            file_name (str | Path | None, optional): The file path and name for where to save the
                prepared data, if not overwriting the existing agent data. Defaults to None.

        Returns:
            pd.DataFrame: The prepared agent data.
        """
        agents = cls(agent_file, sector, model_config)
        agents.prepare()
        if save_results:
            agents.save_agents(file_name=file_name)
        return agents.agents

    @classmethod
    def load_agents(cls, agent_file: str | Path) -> pd.DataFrame:
        """Load the agent data without making any additional modifications.

        Args:
            agent_file (str | Path): The full file path of the agent parquet, pickle, or CSV data.

        Returns:
            pd.DataFrame: The agent data.
        """
        agents = cls(agent_file)
        return agents.agents

    def _load_agents(self):
        """Loads in the agent file and drops any indices."""
        suffix = self.agent_file.suffix
        if suffix in (".pqt", ".parquet"):
            file_reader = pd.read_parquet
        elif suffix in (".pkl", ".pickle"):
            file_reader = pd.read_pickle
        elif suffix == ".csv":
            file_reader = pd.read_csv
        else:
            raise ValueError(
                f"File types ending in {suffix} can't be read as pickle, parquet, or CSV"
            )

        self.agents = file_reader(self.agent_file)
        if suffix == ".csv":
            self.agents = self.agents.reset_index(drop=True)

    def prepare(self):
        """Prepares the agent data so that it has the necessary columns required for modeling.

        Steps:
        1. Extract `state_fips` from the `fips_code` column.
        2. If `census_tract_id` is missing, load and merge the 2020 census tracts
          based on the `pgid` column.
        3. Convert the 2012 rev ID to the 2018 rev id in `rev_index_wind`.
        4. Attach the universal resource generation data.
        """
        self.config = Configuration(self.config)
        if "state_fips" not in self.agents.columns:
            self.agents["state_fips"] = [el[:2] for el in self.agents["fips_code"]]

        if "census_tract_id" not in self.agents.columns:
            self.merge_census_data()

        self.update_rev_id()
        self.merge_generation()

    def save_agents(self, file_name: str | Path | None = None):
        if file_name is None:
            file_name = self.agent_file

        suffix = file_name.suffix
        if suffix in (".pqt", ".parquet"):
            file_saver = self.agents.to_parquet
        elif suffix in (".pkl", ".pickle"):
            file_saver = self.agents.to_pickle
        elif suffix == ".csv":
            file_saver = self.agents.to_csv
        else:
            raise ValueError(
                f"File types ending in {suffix} can't be read as pickle, parquet, or CSV"
            )

        file_saver(file_name)

    def merge_census_data(self):
        census_tracts = pd.read_csv(
            "/projects/dwind/configs/sizing/wind/lkup_block_to_pgid_2020.csv",
            usecols=["pgid", "fips_block"],
            dtype=str,
        ).drop_duplicates()
        census_tracts["census_tract_id"] = [el[:11] for el in census_tracts["fips_block"]]
        self.agents = (
            self.agents.merge(census_tracts, how="left", on="pgid")
            .drop_duplicates(subset=["gid"])
            .reset_index(drop=True)
        )

    def update_rev_id(self, resource_year="2018"):
        """Update 2012 rev index to 2018 index."""
        if resource_year != "2018":
            return

        index_file = "/projects/dwind/configs/rev/wind/lkup_rev_index_2012_to_2018.csv"
        rev_index_map = (
            pd.read_csv(index_file, usecols=["rev_index_wind_2012", "rev_index_wind_2018"])
            .rename(columns={"rev_index_wind_2012": "rev_index_wind"})
            .set_index("rev_index_wind")
        )

        ix_original = self.agents.index.name
        if ix_original is None:
            self.agents = (
                self.agents.set_index("rev_index_wind", drop=True)
                .join(rev_index_map, how="left")
                .reset_index(drop=True)
                .rename(columns={"rev_index_wind_2018": "rev_index_wind"})
                .dropna(subset="rev_index_wind")
            )
        else:
            self.agents = (
                self.agents.reset_index(drop=False)
                .set_index("rev_index_wind")
                .join(rev_index_map, how="left")
                .set_index(ix_original, drop=True)
                .rename(columns={"rev_index_wind_2018": "rev_index_wind"})
                .dropna(subset="rev_index_wind")
            )

    def merge_generation(self):
        if self.resource_year != "2018":
            return

        # update 2012 rev cf/naep/aep to 2018 values
        # self.agents = self.agents.drop(columns=["wind_naep", "wind_cf", "wind_aep"])
        resource_potential = resource.ResourcePotential(
            parcels=self.agents,
            application=self.sector,
            year=self.resource_year,
            model_config=self.model_config,
        )
        self.agents = resource_potential.match_rev_summary_to_agents()


class Model:
    def __init__(
        self,
        agents: pd.DataFrame,
        location: str,
        sector: str,
        scenario: str,
        year: int,
        out_path: str | Path,
        model_config: str | Path,
        chunk_ix: int | None = None,
    ):
        if chunk_ix is None:
            chunk_ix = 0
        self.agents = agents
        self.out_path = Path(out_path).resolve()

        self.full_scenario = f"{location}_{sector}_{scenario}_{year}"
        self.run_name = f"{self.full_scenario}_{chunk_ix}"
        self.location = location
        self.sector = sector
        self.scenario = scenario
        self.year = year
        self.config = Configuration(model_config)

        self.init_logging()

        t_dict = self.config.rev.turbine_class_dict
        if self.sector == "fom":
            apps = ["BTM, FOM", "BTM, FOM, Utility", "FOM, Utility"]
            self.agents["turbine_class"] = self.agents["wind_size_kw_fom"].map(t_dict)
        else:
            apps = ["BTM", "BTM, FOM", "BTM, FOM, Utility"]
            self.agents["turbine_class"] = self.agents["wind_size_kw"].map(t_dict)

        # filter by sector
        self.agents = self.agents[self.agents["application"].isin(apps)]

    def init_logging(self):
        log_dir = self.out_path / "logs"
        if not log_dir.exists():
            log_dir.mkdir()

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
            handlers=[
                logging.FileHandler(log_dir / "dwfs.txt"),
                logging.StreamHandler(),
            ],
        )

        self.log = logging.getLogger("dwfs")

    def get_rates(self):
        self.agents = self.agents[~self.agents["rate_id_alias"].isna()]
        self.agents["rate_id_alias"] = self.agents["rate_id_alias"].astype(int)
        rate_ids = np.unique(self.agents.rate_id_alias.values)

        tariff = (
            pd.read_parquet("/projects/dwind/data/tariffs/2025_tariffs.pqt")
            .loc[rate_ids]
            .reset_index(drop=False)  # , names="rate_id_alias")
        )
        self.tariff_columns = [
            c for c in tariff.columns if c not in ("rate_id_alias", "tariff_name")
        ]

        self.agents = self.agents.merge(tariff, how="left", on="rate_id_alias")

    def get_load(self):
        consumption_hourly = pd.read_parquet("/projects/dwind/data/crb_consumption_hourly.pqt")

        consumption_hourly["scale_offset"] = 1e8
        consumption_hourly = array.scale_array_precision(
            consumption_hourly, "consumption_hourly", "scale_offset"
        )

        self.agents = self.agents.merge(
            consumption_hourly, how="left", on=["crb_model", "hdf_index"]
        )

        # update load based on scaling factors from 2024 consumption data
        f = "/projects/dwind/data/parcel_landuse_load_application_mapping.csv"
        bldg_types = pd.read_csv(f)[["land_use", "bldg_type"]]
        self.agents = self.agents.merge(bldg_types, on="land_use", how="left")

        f = "/projects/dwind/data/consumption/2024/load_scaling_factors.csv"
        sfs = pd.read_csv(f, dtype={"state_fips": str})[["state_fips", "bldg_type", "load_sf_2024"]]
        self.agents = self.agents.merge(sfs, on=["state_fips", "bldg_type"], how="left")
        self.agents["load_kwh"] *= self.agents["load_sf_2024"]
        self.agents["max_demand_kw"] *= self.agents["load_sf_2024"]
        self.agents = self.agents.drop(columns=["load_sf_2024"])

        if self.year > 2025:
            # get county_id to nerc_region_abbr lkup
            # from diffusion_shared.county_nerc_join (dgen_db_fy23q4_ss23)
            f = "/projects/dwind/data/county_nerc_join.csv"
            nerc_regions = pd.read_csv(f)[["county_id", "nerc_region_abbr"]]
            self.agents = self.agents.merge(nerc_regions, on=["county_id"], how="left")

            # get load growth projects from AEO
            # from diffusion_shared.aeo_load_growth_projections_nerc_2023_updt (dgen_db_fy23q4_ss23)
            f = "/projects/dwind/data/consumption/aeo_load_growth_projections_nerc_2023_updt.csv"
            load_growth = pd.read_csv(f)
            load_growth = load_growth.loc[
                load_growth["scenario"].eq("AEO2023 Reference case")
                & load_growth["year"].eq(self.year),
                ["nerc_region_abbr", "sector_abbr", "load_multiplier"],
            ]

            # merge load growth projections
            self.agents = self.agents.merge(
                load_growth, on=["nerc_region_abbr", "sector_abbr"], how="left"
            )
            self.agents["load_kwh"] *= self.agents["load_multiplier"]
            self.agents["max_demand_kw"] *= self.agents["load_multiplier"]
            self.agents = self.agents.drop(columns=["load_multiplier", "nerc_region_abbr"])

        self.agents = array.scale_array_sum(self.agents, "consumption_hourly", "load_kwh")

    def get_nem(self):
        if self.scenario == "metering":
            self.agents["compensation_style"] = "net metering"
            self.agents["nem_system_kw_limit"] = 1000000000
        elif self.scenario == "billing":
            self.agents["compensation_style"] = "net billing"
            self.agents["nem_system_kw_limit"] = 1000000000
        else:
            cols = ["state_abbr", "sector_abbr", "compensation_style", "nem_system_kw_limit"]
            nem_scenario_csv = scenarios.config_nem(self.scenario, self.year)
            nem_df = (
                pd.read_csv(self.config.project.DIR / f"data/nem/{nem_scenario_csv}")
                .rename(columns={"max_pv_kw_limit": "nem_system_kw_limit"})
                .loc[:, cols]
            )

            self.agents = self.agents.merge(nem_df, how="left", on=["state_abbr", "sector_abbr"])

            self.agents["compensation_style"] = self.agents["compensation_style"].fillna(
                "net billing"
            )
            self.agents["nem_system_kw_limit"] = self.agents["nem_system_kw_limit"].fillna(0.0)

            # check if selected system size by tech violate nem_system_kw_limit
            for tech in self.config.project.settings.TECHS:
                col = f"{tech}_size_kw_btm"
                self.agents.loc[
                    (self.agents[col] > self.agents["nem_system_kw_limit"]), "compensation_style"
                ] = "net billing"

    def prepare_agents(self):
        if self.sector == "btm":
            # map tariffs
            self.log.info("....running with pre-processed tariffs")
            self.get_rates()

            # get hourly consumption
            self.log.info("....fetching hourly consumption")
            self.get_load()

            if self.config.project.settings.SIZE_SYSTEMS:
                # size btm systems
                self.log.info("....sizing BTM systems")
                self.agents = btm_sizing.sizer(self.agents, self.config)

            # map nem policies
            self.log.info("....processing NEM for BTM systems")
            self.get_nem()

        if self.sector == "fom":
            if self.config.project.settings.SIZE_SYSTEMS:
                # for fom agents, take largest wind turbine
                self.agents.sort_values(
                    by=["wind_turbine_kw", "turbine_height_m"],
                    ascending=[False, False],
                    inplace=True,
                )
                self.agents.drop_duplicates(subset=["gid"], inplace=True)

                # track FOM techpot sizes
                self.agents["solar_size_kw_techpot"] = self.agents["solar_size_kw_fom"]
                self.agents["wind_size_kw_techpot"] = self.agents["wind_size_kw_fom"]

                # handle FOM max system sizes
                if "solar" in self.config.project.settings.TECHS:
                    mask = (
                        self.agents["solar_size_kw_fom"]
                        > self.config.siting["solar"]["max_fom_size_kw"]
                    )
                    self.agents.loc[mask, "solar_size_kw_fom"] = self.config.siting["solar"][
                        "max_fom_size_kw"
                    ]
                    self.agents["solar_aep_fom"] = (
                        self.agents["solar_naep"] * self.agents["solar_size_kw_fom"]
                    )

                if "wind" in self.config.project.settings.TECHS:
                    mask = (
                        self.agents["wind_size_kw_fom"]
                        > self.config.siting["wind"]["max_fom_size_kw"]
                    )
                    self.agents.loc[mask, "wind_size_kw_fom"] = self.config.siting["wind"][
                        "max_fom_size_kw"
                    ]
                    self.agents["wind_aep_fom"] = (
                        self.agents["wind_naep"] * self.agents["wind_size_kw_fom"]
                    )

    def run_valuation(self):
        valuer = valuation.ValueFunctions(self.scenario, self.year, self.config)

        if self.sector == "btm":
            self.agents["application"] = "BTM"

            if len(self.agents) > 0:
                self.log.info("\n")
                self.log.info(f"starting valuation for {len(self.agents)} BTM agents")

                self.agents = valuer.run_multiprocessing(self.agents, sector="btm")

                self.log.info("null counts:")
                self.log.info(self.agents.isnull().sum().sort_values())

                # save pickle
                if self.config.project.settings.SAVE_APP_PARQUET:
                    if "wind_cf_hourly" in self.agents.columns:
                        self.agents.drop(columns=["wind_cf_hourly"], inplace=True, errors="ignore")

                    if "solar_cf_hourly" in self.agents.columns:
                        self.agents.drop(columns=["solar_cf_hourly"], inplace=True, errors="ignore")

                    self.agents.drop(columns=self.tariff_columns, inplace=True, errors="ignore")

                    f_out = self.out_path / f"{self.run_name}.pqt"
                    self.agents.to_parquet(f_out)
            else:
                self.agents = pd.DataFrame()

        if self.sector == "fom":
            self.agents["application"] = "FOM"

            if len(self.agents) > 0:
                self.log.info("\n")
                self.log.info(f"starting valuation for {len(self.agents)} FOM agents")

                self.agents = valuer.run_multiprocessing(self.agents, "fom")

                self.log.info("null counts:")
                self.log.info(self.agents.isnull().sum().sort_values())

                # --- save sector pickle ---
                if self.config.project.settings.SAVE_APP_PARQUET:
                    if "wind_cf_hourly" in self.agents.columns:
                        self.agents.drop(columns=["wind_cf_hourly"], inplace=True, errors="ignore")
                    if "solar_cf_hourly" in self.agents.columns:
                        self.agents.drop(columns=["solar_cf_hourly"], inplace=True, errors="ignore")

                    f_out = self.out_path / f"{self.run_name}.pqt"
                    self.agents.to_parquet(f_out)
            else:
                self.agents = pd.DataFrame()

    def run(self):
        self.prepare_agents()
        self.run_valuation()
