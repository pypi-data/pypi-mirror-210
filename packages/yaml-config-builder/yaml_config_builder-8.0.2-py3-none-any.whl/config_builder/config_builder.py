# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

""" Main class for building configuration classes """

import argparse
import logging
import os
from collections import OrderedDict
from pathlib import Path
from typing import Callable, Dict, Optional, Type, cast

import yaml
from related import from_yaml, to_model

from config_builder import BaseConfigClass
from config_builder.replacement_map import (
    clear_replacement_map,
    get_current_replacement_map,
    set_replacement_map_value,
    update_replacement_map_from_os,
)
from config_builder.utils import prepare_config_path
from config_builder.yaml_constructors import (
    join_object,
    join_object_from_config_dir,
    join_path,
    join_string,
    join_string_with_delimiter,
)

logger = logging.getLogger(__name__)


class ConfigBuilder:
    def __init__(
        self,
        class_type: Type[BaseConfigClass],
        yaml_config_path: Optional[str] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
        no_checks: bool = False,
        use_argparse: bool = False,
        configure_argparse: Optional[Callable[[argparse.ArgumentParser], None]] = None,
    ):
        """
        Build a configuration object of the given class type. There are three options:

        - Build a configuration object from the given yaml path
        - Build a configuration object by utilizing the argparse
          parameter "--yaml_config_path" and --replacement-config-path

        After a configuration object is build a post-processing takes place,
        consisting of two parts:

        1. Recursively check the class tree for mutual attributes that are defined via the
           parameter _mutual_attributes function of each BaseConfigClass

        2. Recursively check any string attribute (including strings in lists and dictionaries),
           for placeholders (keys of the string_replacement_map) and replacement them
           (values of the string_replacement_map).

        Args:
            class_type: The type of the configuration object
            yaml_config_path: (Optional) A yaml filepath where to build the configuration
                              object from
            string_replacement_map: (Optional) That defines any string placeholders which can
                                    be used in string attributes
            no_checks: Whether the configuration object should be checked for mutual exclusiveness
                       and the "check_values" method for each attribute of the supertype
                       "BaseConfigClass" should be called
            use_argparse: Whether to parse the relevant parameters from commandline
            configure_argparse: (Optional) Reference to a method that allows additional
                                argparse configurations
        """

        self.class_type = class_type
        self.yaml_config_path: Optional[str] = yaml_config_path
        self.string_replacement_map = string_replacement_map
        self.no_checks = no_checks
        self.args: Optional[argparse.Namespace] = None
        self.parser: Optional[argparse.ArgumentParser] = None

        # The build of a configuration object should not be affected from any side effect,
        # therefore clear the global replacement map before each run
        clear_replacement_map()

        ConfigBuilder.__update_replacement_map(
            string_replacement_map=self.string_replacement_map
        )

        if use_argparse:
            # Ensure that ConfigBuilder specific argparse parameter are set
            self.parser = self.setup_argparse(
                configure_argparse=configure_argparse,
            )
            self.args = self.parser.parse_args()

            logger.info(f"Parsed arguments from command-line: {self.args}")

            self.yaml_config_path = (
                str(Path(self.args.yaml_config_path))
                if self.args.yaml_config_path
                else None
            )

            # Check any placeholder of the replacement-map whether they have
            # an entry in the parsed arguments
            ConfigBuilder.__update_placeholder_from_argparse(args=self.args)

            # Parse a replacement-map if the filepath is given as commandline argument
            ConfigBuilder.__update_replacement_map(
                string_replacement_map=self.__parse_replacement_map(
                    replacement_config_path=str(Path(self.args.replacement_config_path))
                    if self.args.replacement_config_path
                    else None
                )
            )

        if self.yaml_config_path is None:
            raise ValueError(f"Can not build a configuration, yaml-config-path is None")

        # Update the placeholder value in order to be able to prepare the yaml-config-path,
        # in case the path already contains a placeholder value
        update_replacement_map_from_os()
        self.yaml_config_path = prepare_config_path(
            config_path=self.yaml_config_path,
        )

        self.configuration: BaseConfigClass = self.__postprocess_config(
            configuration=ConfigBuilder.__build_from_yaml(
                yaml_config_path=self.yaml_config_path,
                class_type=self.class_type,
            )
        )

    @staticmethod
    def __parse_replacement_map(
        replacement_config_path: Optional[str],
    ) -> Optional[Dict[str, str]]:
        if replacement_config_path is None:
            logger.warning(
                "The replacement_config_path is None, string replacement will not be available!"
            )
            return None

        if not os.path.isfile(replacement_config_path):
            logger.warning(
                "The given replacement_config_path does not exist: %s, "
                "string replacement will not be available!" % replacement_config_path
            )
            return None

        logger.info("Load replacement-map from: %s" % replacement_config_path)
        with open(
            file=replacement_config_path, mode="r", encoding="utf8"
        ) as config_file:
            return cast(
                Dict[str, str], yaml.load(stream=config_file, Loader=yaml.Loader)
            )

    @staticmethod
    def __update_replacement_map(
        string_replacement_map: Optional[Dict[str, str]],
    ) -> None:
        """
        Updates the global replacements map by calling set_replacement_map_value(...)
        for every entry of the given string-replacement-map

        Args:
            string_replacement_map: The replacement map that should be used to update the
                                    global replacement map

        Returns:
            None
        """

        if string_replacement_map is not None:
            logger.debug("Update placeholder values from given string replacement map")
            for key, value in string_replacement_map.items():
                set_replacement_map_value(key=key, value=value)

    @staticmethod
    def __build_from_yaml(
        yaml_config_path: str,
        class_type: Type[BaseConfigClass],
    ) -> BaseConfigClass:
        """
        Build a configuration object of the given type from the given yaml filepath.

        Args:
            yaml_config_path: The yaml filepath where to build the configuration object from
            class_type: The type of the configuration object

        Returns:
            The build configuration object
        """

        logger.info(
            f"Build config for class type '{class_type}' "
            f"from config path '{yaml_config_path}'"
        )

        if not os.path.isfile(yaml_config_path):
            raise ValueError(
                f"Config file path does not exist. The given path is: {yaml_config_path}"
            )

        with open(yaml_config_path, encoding="utf8") as yaml_file:
            original_yaml = yaml_file.read().strip()

        # register the tag handler
        yaml.add_constructor("!join_string", join_string)
        yaml.add_constructor("!join_string_with_delimiter", join_string_with_delimiter)
        yaml.add_constructor("!join_path", join_path)
        yaml.add_constructor("!join_object", join_object)
        yaml.add_constructor(
            "!join_object_from_config_dir", join_object_from_config_dir
        )

        yml_dict = from_yaml(
            yaml_package=yaml, stream=original_yaml, loader_cls=yaml.Loader
        )

        ConfigBuilder.__recursive_check_dict(yml_dict=yml_dict)

        configuration: BaseConfigClass = to_model(class_type, yml_dict)

        return configuration

    def __postprocess_config(self, configuration: BaseConfigClass) -> BaseConfigClass:
        """
        Post process the configuration that has been build with "__build_from_yaml".

        1. Check attributes to be mutual exclusive
        2. Perform replacements of placeholder variables in the following order:
            1. Use the values of the string-replacement-map from the ConfigBuilder constructor
            2. Update the values from configuration attributes that match a placeholder name
            3. Update the values from equivalent os-environment-variables
        3. Call the check_values method of every attribute that is
           an instance of the BaseConfigClass

        Args:
            configuration: The configuration object to post process

        Returns:
            The post processed configuration object
        """
        # run recursive check and fill the update the globally defined replacement map
        configuration.recursive_check_mutuality_and_update_replacements(
            no_checks=self.no_checks,
        )

        # Get values of OS environment variables for all values that are now part of
        # the globally defined replacement map
        update_replacement_map_from_os()

        # Replace any placeholder in strings that are part of the build config object
        configuration.recursive_string_replacement()

        # Save the replacement map that has been used to build this config object
        configuration.string_replacement_map.update(get_current_replacement_map())

        if not self.no_checks:
            configuration.recursive_check_values()

            if not configuration.check_values():
                raise ValueError(
                    f"Check values for configuration class"
                    f"'{configuration.__class__}' failed!"
                )

        return configuration

    @staticmethod
    def setup_argparse(
        configure_argparse: Optional[Callable[[argparse.ArgumentParser], None]] = None
    ) -> argparse.ArgumentParser:
        """
        Init an argparse instance for the config-builder.
        Use the default or provided description for the help message.

        Args:
            configure_argparse:
        Returns:
             The created parser instance
        """

        parser: argparse.ArgumentParser = argparse.ArgumentParser()

        yaml_config_path_option = "yaml_config_path"
        replacement_config_path_option = "replacement-config-path"

        options = [
            item
            for sublist in [a.option_strings for a in parser._actions]
            for item in sublist
        ]

        if yaml_config_path_option not in options:
            parser.add_argument(
                f"{yaml_config_path_option}",
                help="Load all parameters from the given yaml configuration file",
                type=str,
            )

        if replacement_config_path_option not in options:
            parser.add_argument(
                f"--{replacement_config_path_option}",
                help="Path to the string replacement map that defines "
                "placeholders for YAML configuration files",
                type=str,
            )

        for key in get_current_replacement_map().keys():
            parser.add_argument(
                f"--{key}",
                help=f"'{key}': os environment variable, "
                f"which can be used as placeholder",
                type=str,
                default=None,
            )

        if configure_argparse:
            configure_argparse(parser)

        return parser

    @staticmethod
    def __update_placeholder_from_argparse(args: argparse.Namespace) -> None:
        args_dict = vars(args)

        for os_replacement_key in get_current_replacement_map().keys():
            if (
                os_replacement_key in args_dict
                and args_dict[os_replacement_key] is not None
            ):
                set_replacement_map_value(
                    key=os_replacement_key, value=args_dict[os_replacement_key]
                )

    @staticmethod
    def __recursive_check_dict(yml_dict: OrderedDict) -> None:  # type: ignore
        """
        Check the dictionary that has been parsed by a from_yaml(stream=original_yaml),
        whether there have been failures while reading configs
        from file-paths. This indicates either a real wrong configured
        path or that some OS replacements haven't been configured.

        :param yml_dict: OrderedDict parsed from via "from_yaml(stream=original_yaml)"
        :return: None
        """

        for key, value in yml_dict.items():
            if isinstance(value, OrderedDict):
                ConfigBuilder.__recursive_check_dict(yml_dict=value)
            else:
                if "FileNotFoundError" in key:
                    raise FileNotFoundError(value)
