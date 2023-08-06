# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""
Definition of constructors that can be added to the python yaml package
"""

from __future__ import absolute_import, annotations, division, print_function

import logging
import os
from collections import OrderedDict
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

import yaml
from yaml import FullLoader, Loader, Node, UnsafeLoader

from config_builder.utils import prepare_config_path

logger = logging.getLogger(__name__)


def join_string(loader: Union[Loader, FullLoader, UnsafeLoader], node: Node) -> Any:
    """
    Define a custom tag handler that can be added as constructor to
    the python yaml package.

    Concatenates all the strings that are given by the node parameter.

    Args:
        loader: a yaml loader needed to parse the content of the given node into
                a sequence
        node: The node for which to apply this constructor

    Returns:
        The concatenated string
    """

    seq = loader.construct_sequence(node)  # type: ignore[arg-type]

    logger.debug(f"join string for a configuration item: {seq}")

    return "".join([str(i) for i in seq])


def join_string_with_delimiter(
    loader: Union[Loader, FullLoader, UnsafeLoader], node: Node
) -> Any:
    """
    Define a custom tag handler that can be added as constructor to
    the python yaml package.

    Concatenates all the strings that are given by the node parameter. In between
    these strings a delimiter is put. The delimiter is defined by the first
    element of the parsed sequence.

    Args:
        loader: a yaml loader needed to parse the content of the given node into
                a sequence
        node:  The node for which to apply this constructors

    Returns:
        The concatenated string
    """
    seq = loader.construct_sequence(node)  # type: ignore[arg-type]

    delimiter = str(seq[0])

    logger.debug(f"join string with delimiter {delimiter} a configuration item: {seq}")

    joined_string = ""
    for index in range(1, len(seq) - 1):
        joined_string += str(seq[index]) + delimiter

    joined_string += str(seq[-1])

    return joined_string


def join_path(loader: Union[Loader, FullLoader, UnsafeLoader], node: Node) -> Any:
    """
    Define a custom tag handler that can be added as constructor to
    the python yaml package.

    Constructs an path out of all given strings by the given node.

    Args:
        loader: a yaml loader needed to parse the content of the given node into
                a sequence
        node: The node for which to apply this constructors

    Returns:
        The constructed path
    """

    seq = loader.construct_sequence(node)  # type: ignore[arg-type]

    logger.debug(f"join path for a configuration item: {seq}")

    joined_path = ""
    for path in seq:
        joined_path = os.path.join(joined_path, str(path))

    return str(Path(joined_path))


def join_object(loader: Union[Loader, FullLoader, UnsafeLoader], node: Node) -> Any:
    """
    Define a custom tag handler that can be added as constructor to
    the python yaml package.

    Allows to include the content of another yaml file.
    The node has to contain two parameters:
    - 1.: The first defines the name of the attribute whose content should be
      extracted from the given yaml file. When the key is an empty string, the whole
      content of the yaml file will be used
    - 2.: The path to the yaml file from which the content should be extracted

    Args:
        loader: a yaml loader needed to parse the content of the given node into
                a sequence
        node: The node for which to apply this constructors
    Returns:
        An OrderedDict containing the content of the given yaml file
    """

    seq = loader.construct_sequence(node)  # type: ignore[arg-type]

    if len(seq) < 2:
        raise ValueError(
            "You have two provide two parameters when using !join_object:\n"
            " -1.: The first defines the name of the attribute whose content should be "
            " extracted from the given yaml file\n"
            " -2.: The path to the yaml file from which the content should be extracted\n"
        )

    class_type = str(seq[0])

    transformed_data: Union[List[Any], OrderedDict[Any, Any]]

    transformed_data_list: List[Union[List[Any], OrderedDict[Any, Any]]] = []

    for index in range(1, len(seq)):
        config_path = str(Path(str(seq[index])))
        data, config_path = __get_config_data(config_path=config_path)

        if data is not None and class_type != "":
            logger.debug(
                f"Parsed configuration via !join_object "
                f"for class-type '{class_type}' from '{config_path}'"
            )

            _transformed_data = data[class_type]
        else:
            if data is not None and class_type == "":
                logger.debug(
                    f"Parsed configuration via !join_object "
                    f"with emtpy class-type from '{config_path}'"
                )

                _transformed_data = data
            else:
                _transformed_data = OrderedDict(
                    {
                        "FileNotFoundError": f"Could not parse content from the "
                        f"configuration file {config_path} "
                        f"for class '{class_type}'!"
                    }
                )

        transformed_data_list.append(_transformed_data)

    if len(transformed_data_list) > 1:
        # In case of multiple filepaths given by !join_object,
        # we assume that the respective attribute is of type list.
        # Therefore, we concatenate all the entries to one joined list.
        transformed_data = []
        for _transformed_data in transformed_data_list:
            transformed_data.extend(_transformed_data)
    elif len(transformed_data_list) == 1:
        # In case of a single item, take the entry as is.
        transformed_data = transformed_data_list[0]
    else:
        # This is just a fallback. With checking 'len(seq) < 2' above,
        # we normally have at least one entry in the transformed_data_list
        transformed_data = OrderedDict({})

    return transformed_data


def join_object_from_config_dir(
    loader: Union[Loader, FullLoader, UnsafeLoader], node: Node
) -> Any:
    """
    Define a custom tag handler that can be added as constructor to
    the python yaml package.

    Allows to include the content of another yaml file, that is searched in different directories.
    The node has to contain three parameters:
    -1.: the name of the attribute whose content should be extracted from the given yaml file
    -2.: The name of the configuration file
    -3. to n: directories where to search for the given configuration file

    Args:
        loader: a yaml loader needed to parse the content of the given node into
                a sequence
        node: The node for which to apply this constructors

    Returns:
         An OrderedDict containing the content of the given yaml file
    """

    sequences = loader.construct_sequence(node)  # type: ignore[arg-type]

    if len(sequences) < 3:
        raise ValueError(
            "For !join_object_from_config_dir at least 3 Arguments have to be provided!\n"
            " -1.: class_type\n"
            " -2.: config_file_name\n"
            " -3. to n: directories where to search for the config_file_name"
        )

    class_type = str(sequences[0])
    config_file_name = str(sequences[1])
    config_dirs = sequences[2:]

    transformed_data: Optional[OrderedDict[Any, Any]] = None

    for _, config_dir in enumerate(config_dirs):
        if transformed_data is not None:
            break

        data, config_path = __get_config_data(
            config_path=str(Path(os.path.join(str(config_dir), config_file_name)))
        )

        if data is not None and class_type != "":
            logger.debug(
                f"Parsed configuration via !join_object_from_config_dir "
                f"for class-type '{class_type}' from '{config_path}'"
            )

            transformed_data = data[class_type]
        else:
            if data is not None and class_type == "":
                logger.debug(
                    f"Parsed configuration via !join_object_from_config_dir "
                    f"with emtpy class-type from '{config_path}'"
                )

                transformed_data = data

    if transformed_data is None:
        transformed_data = OrderedDict(
            {
                "FileNotFoundError": f"Could not find a valid "
                f"configuration file for class '{class_type}' "
                f"while parsing for config_file_name '{config_file_name}' "
                f"and config_dirs '{config_dirs}'!"
            }
        )

    return transformed_data


# register the tag handlers
yaml.add_constructor("!join_string", join_string)
yaml.add_constructor("!join_string_with_delimiter", join_string_with_delimiter)
yaml.add_constructor("!join_path", join_path)
yaml.add_constructor("!join_object", join_object)
yaml.add_constructor("!join_object_from_config_dir", join_object_from_config_dir)


def __parse_from_config_path(config_path: str) -> Optional[OrderedDict[Any, Any]]:
    parsed_dict: Optional[OrderedDict[Any, Any]] = None

    if os.path.isfile(config_path):
        with open(config_path, encoding="utf8") as config_file:
            parsed_dict = yaml.load(config_file, Loader) or OrderedDict()
    else:
        logger.debug(
            "The given config-path does not exist! Can not parse any data. "
            f"config_path: {config_path}"
        )

    return parsed_dict


def __get_config_data(config_path: str) -> Tuple[Optional[OrderedDict[Any, Any]], str]:
    parsed_dict: Optional[OrderedDict[Any, Any]]

    parsed_dict = __parse_from_config_path(config_path=config_path)

    if parsed_dict is not None:
        return parsed_dict, config_path
    else:
        logger.debug(
            f"Could not parse data from '{config_path}'! "
            f"Trying to build a valid config-path "
            f"by using placeholders as substitutes."
        )

        config_path = prepare_config_path(
            config_path=config_path,
        )

        parsed_dict = __parse_from_config_path(config_path=config_path)

        return parsed_dict, config_path
