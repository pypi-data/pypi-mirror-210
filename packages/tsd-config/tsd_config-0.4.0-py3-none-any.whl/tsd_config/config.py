"""Module for loading package configuration."""
import os
import pathlib
import re
import sys
from typing import Union

from deepmerge import Merger
from schema import Schema
from schema import SchemaError

from tsd_config.exceptions import ConfigurationFileUnavailable
from tsd_config.exceptions import ConfigurationValidationError

DEFAULT_TYPE_SPECIFIC_MERGE_STRATEGIES = [
    (list, "append_unique"),
    (dict, "merge"),
    (set, "union"),
]
DEFAULT_MERGER = Merger(
    type_strategies=DEFAULT_TYPE_SPECIFIC_MERGE_STRATEGIES,
    fallback_strategies=["override"],
    type_conflict_strategies=["override"],
)


def _merge_config(
    config: dict,
    *,
    base: dict = {},
    merger: Merger = None,
) -> dict:
    """Merge config object on top of base configuration."""
    if merger is None:
        merger = DEFAULT_MERGER
    return merger.merge(base, config)


def validate_config(config: dict, schema: Schema) -> dict:
    """Validate that the required package configuration is present in what
    has been loaded in using schema validation.

    Args:
        config (dict): an object containing the package configuration

    Raises:
        ConfigurationValidationError: if a required key was missing, or the
        provided value for a key was not found to be valid
    Returns:
        dict: validated dictionary object containing program configuration
    """
    try:
        return schema.validate(config)
    except SchemaError as exception:
        raise ConfigurationValidationError(
            "The configuration is invalid."
        ) from exception


def load_config(
    name: str,
    *,
    config_path: Union[pathlib.Path, str] = None,
    defaults: dict = None,
    schema: Schema = None,
    merger: Merger = None,
    no_file: bool = False,
) -> dict:
    """Load in the package configuration from a file.


    Defaults can be provided by passing a dict to the `defaults` argument
    but values from the config file will take presedence.

    Args:
        name (str): the name of the package we are loading configuration for
        config_path (Union[pathlib.Path, str], optional): The path to a
            configuration file to be loaded. If not provided, configuration will
            be loaded from the TOML config file
            /etc/tsd-name-of-package/config.toml by default. This path can be
            overridden by setting the environment variable
            TSD_NAME_OF_PACKAGE_CONFIG_FILE (tsd_name_of_package here being the
            value provided in the name argument).
        defaults (dict, optional): Default values can be provided by this
            argument. File configuration will get priority over values set here.
        schema (Schema, optional): schema definition to be used for validating
            the loaded configuration. If no schema is provided, configuration
            will not be validated. Defaults to None.
        merger (Merger, optional): a configured deepmerge Merger class instance
            to be used when merging configuration on top of defaults.
        no_file (bool, optional): whether to load configuration from a file
            or not.
    Raises:
        ConfigurationFileUnavailable: if the provided config file doesn't exist

    Returns:
        dict: dictionary object containing configuration data
    """
    if no_file is True:
        config = {}
    else:
        if isinstance(config_path, str):
            config_path = pathlib.Path(config_path)
        if not config_path:
            config_path = pathlib.Path(
                os.getenv(
                    key=f"{name.upper().replace('-', '_')}_CONFIG_FILE",
                    default=f"/etc/{name.lower().replace('_', '-')}/config.toml",
                )
            )

        if not config_path.is_file():
            raise ConfigurationFileUnavailable(
                f"No file at path '{config_path}'."
            )

        with open(config_path, "rb") as fp:
            if config_path.suffix == ".toml":
                if sys.version_info >= (3, 11):
                    import tomllib as toml
                else:
                    import tomli as toml

                config = toml.load(fp)
            elif re.match(r".ya?ml$", config_path.suffix):
                import yaml

                try:
                    from yaml import CLoader as Loader
                except ImportError:
                    from yaml import Loader

                config = yaml.load(fp, Loader=Loader)

    # merging of configuration when defaults are provided
    if defaults is not None:
        config = _merge_config(config, base=defaults, merger=merger)

    # optional schema validation
    if schema is not None:
        config = validate_config(config, schema=schema)

    return config
