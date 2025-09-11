"""Custom configuration data class to allow for dictionary style and dot notation calling of
attributes and Enums for validating configuration data.
"""

from __future__ import annotations

import re
import sys
from enum import Enum, IntEnum
from typing import Any, Annotated
from pathlib import Path


# fmt: off
if sys.version_info >= (3, 11):  # noqa
    import tomllib
else:
    import tomli as tomllib
# fmt: on


class ValuesMixin:
    """Mixin class providing `.values()` for Enum classes."""

    @staticmethod
    def values() -> list[str]:
        """Generate a list of the valid input strings."""
        return [*Sector._value2member_map_]


class Sector(str, ValuesMixin, Enum):
    """Enum validator for sector inputs."""

    FOM: Annotated[str, "Front-of-meter"] = "fom"
    BTM: Annotated[str, "Behind-the-meter"] = "btm"


class Technology(str, ValuesMixin, Enum):
    """Enum validator for technology inputs."""

    WIND: Annotated[str, "Wind generation model"] = "wind"
    SOLAR: Annotated[str, "Solar generation model"] = "solar"


class Scenario(str, ValuesMixin, Enum):
    """Enum validator for the scenario to run."""

    BASELINE: Annotated[str, "Standard scenario to compare alternatives."] = "baseline"
    METERING: Annotated[str, "TODO."] = "metering"
    BILLING: Annotated[str, "TODO."] = "billing"
    HIGHRECOST: Annotated[str, "High renewable adoption"] = "highrecost"
    RE100: Annotated[str, "100% renewable adoption"] = "highrecost"
    LOWRECOST: Annotated[str, "Low renewable adoption"] = "lowrecost"


class Year(ValuesMixin, IntEnum):
    """Enum validator for analysis year."""

    _2022 = 2022
    _2025 = 2025
    _2035 = 2035
    _2040 = 2040


class Optimization(str, ValuesMixin, Enum):
    """Enum validator for breakeven cost optimization strategies."""

    BISECT = "bisect"
    BRENTQ = "brentq"
    GRID_SEARCH = "grid_search"
    NEWTON = "newton"


class CRBModel(Enum):
    """Convert between integers and "crb_model" data for efficient storage and retrieval."""

    full_service_restaurant = 0
    hospital = 1
    large_hotel = 2
    large_office = 3
    medium_office = 4
    midrise_apartment = 5
    out_patient = 6
    primary_school = 7
    quick_service_restaurant = 8
    reference = 9
    secondary_school = 10
    small_hotel = 11
    small_office = 12
    stand_alone_retail = 13
    strip_mall = 14
    supermarket = 15
    warehouse = 16

    @staticmethod
    def model_map() -> dict[str, int]:
        """Create a dictionary of name: int values for each crb model."""
        return {el.name: el.value for el in CRBModel}

    @staticmethod
    def str_model_map() -> dict[str, str]:
        """Create a dictionary of name: str(int) values for each crb model."""
        return {el.name: str(el.value) for el in CRBModel}

    @staticmethod
    def int_map() -> dict[str, int]:
        """Create a dictionary of int: name for each crb model."""
        return {el.value: el.name for el in CRBModel}


class Mapping(dict):
    """Dict-like class that allows for the use of dictionary style attribute calls on class
    attributes.
    """

    def __setitem__(self, key: Any, item: Any):
        """Creates a new key, value pair in :py:attr:`__dict__`.

        Args:
            key (Any): A hashable dictionary key.
            item (Any): A value to be retrieved when the :py:attr:`key` is called.
        """
        self.__dict__[key] = item

    def __getitem__(self, key: Any) -> Any:
        """Retrieve :py:attr:`key`'s value from :py:attr:`__dict__`.

        Args:
            key (Any): An existing key in :py:attr:`__dict__`.

        Returns:
            Any: The value paired to :py:attr:`key`.
        """
        return self.__dict__[key]

    def __repr__(self):
        """Returns the ``repr(self.__dict__)``."""
        return repr(self.__dict__)

    def __len__(self) -> int:
        """Returns the number of keys in :py:attr:`__dict__`.

        Returns:
            int: The number of keys in :py:attr:`__dict__`.
        """
        return len(self.__dict__)

    def __delitem__(self, key: Any):
        """Delete's :py:attr:`key` from :py:attr:`__dict__`."""
        del self.__dict__[key]

    def clear(self):
        """Deletes all entries in :py:attr:`__dict__`."""
        return self.__dict__.clear()

    def copy(self) -> dict:
        """Returns an unlinked copy of :py:attr:`__dict__`."""
        return self.__dict__.copy()

    def update(self, *args, **kwargs):
        """Updates the provided args and keyword arguments of :py:attr:`__dict__`.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        """Returns the keys of :py:attr:`__dict__`."""
        return self.__dict__.keys()

    def values(self):
        """Returns the :py:attr:`__dict__` values."""
        return self.__dict__.values()

    def items(self):
        """Returns the keys and values of :py:attr:`__dict__`."""
        return self.__dict__.items()

    def pop(self, *args):
        """Removes and returns the desired argments from :py:attr:`__dict__` if they exist.

        Args:
            *args: Variable length argument list.

        Returns:
            Any: values of :py:attr:`__dict__` from keys :py:attr:`*args`.
        """
        return self.__dict__.pop(*args)

    def __cmp__(self, dict_):
        """Compares :py:attr:`_dict` to :py:attr:`__dict__`.

        Args:
            dict_ (dict): Dictionary for object comparison.

        Returns:
            bool: Result of the comparison between :py:attr:`_dict` and :py:attr:`__dict__`.
        """
        return self.__cmp__(self.__dict__, dict_)

    def __contains__(self, item):
        """Checks if :py:attr:`item` is in :py:attr:`__dict__`."""
        return item in self.__dict__

    def __iter__(self):
        """Custom iterator return the :py:attr:`__dict__`."""
        return iter(self.__dict__)


class Configuration(Mapping):
    """Configuration class for reading and converting nested dictionaries to allow for both
    namespace style and dot notation when collecting attributes.

    Customizations of the input data:
      - All fields containing "DIR" will be converted to a ``pathlib.Path`` object.
      - All nested data will be able to be called with dot notation and dictionary-style calls.
      - The `rev.turbine_class_dict` is converted to float data automatically.
      - All data in the `[sql]` section will get converted to proper constructor strings with the
        associated username and password data autopopulated with the match ``{USER}`` and
        ``PASSWORD`` fields in the same configuration section.
    """

    def __init__(self, config: str | Path | dict, *, initial: bool = True):
        """Create a hybrid dictionary and name space object for a given :py:attr:`config` and
        where all keys (including nested) are acessible with dictionary-style and dot notation.

        Args:
            config (str | Path | dict): A configuration dictionary or filename to the dictionary
                to read and convert. If passing a filename, it must be a TOML file.
            initial (bool, optional): Option to disable post-processing of configuration data.
        """
        if isinstance(config, (str, Path)):  # noqa: UP038
            config = Path(config).resolve()
            with config.open("rb") as f:
                config = tomllib.load(f)

        for key, value in config.items():
            if isinstance(value, dict):
                self.__setattr__(key, Configuration(value, initial=False))
            else:
                if "DIR" in key:
                    self.__setattr__(key, Path(value).resolve())
                else:
                    self.__setattr__(key, value)

        if initial:
            self._convert_sql()
            self._convert_rev()

    def _convert_sql(self):
        """Replaces the "{USER}" and "{PASSWORD} portions of the sql constructor strings with
        the actual user and password information for ease of configuration reuse between users.
        """
        if "sql" in self:
            for key, value in self.sql.items():
                if key.startswith(("USER", "PASSWORD")):
                    continue
                for target in re.findall(r"\{(.*?)\}", value):
                    value = value.replace(target, self.sql[target])
                value = re.sub("[{}]", "", value)
                self.sql[key] = value

    def _convert_rev(self):
        if "rev" in self:
            self.rev.turbine_class_dict = {
                float(k): v for k, v in self.rev.turbine_class_dict.items()
            }
