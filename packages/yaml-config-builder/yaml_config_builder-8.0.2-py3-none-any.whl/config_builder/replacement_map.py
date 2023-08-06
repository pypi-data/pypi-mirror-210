# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""
Definition and handling of a replacement-map that is used in the ConfigBuilder
to provide information that is used to apply placeholder replacement in strings.
"""

import copy
import logging
import os
from threading import local
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ReplacementMapLocal(local):
    def __init__(self) -> None:
        local.__init__(self)
        self.replacement_map: Dict[str, str] = {}


__replacement_map_local = ReplacementMapLocal()


def get_current_replacement_map() -> Dict[str, str]:
    """
    Get a copy of the internally used replacement_map.

    Returns:
        copy of the internally used replacement_map
    """

    return copy.deepcopy(__replacement_map_local.replacement_map)


def get_replacement_map_keys() -> List[str]:
    """
    Get the dictionary keys of the internally used replacement_map.

    Returns:
        the list of dictionary keys of the internally used replacement_map
    """

    return list(__replacement_map_local.replacement_map.keys())


def get_replacement_value(key: str) -> Optional[str]:
    """
    Get the value to the given key of the internally used replacement_map.

    Args:
        key: The key for which the value should be returned

    Returns:
        the value to the given key of the internally used replacement_map
    """

    if key in __replacement_map_local.replacement_map:
        return __replacement_map_local.replacement_map[key]

    return None


def set_replacement_map_value(key: str, value: Optional[str]) -> None:
    """
    Add a key value pair to the internally used replacement_map

    Args:
        key: key to be added to the replacement_map
        value: value to be added to the replacement_map

    Returns:
        None
    """

    if (
        key in __replacement_map_local.replacement_map
        and value != __replacement_map_local.replacement_map[key]
    ) or key not in __replacement_map_local.replacement_map:
        if value is not None:
            logger.info(f"Set placeholder value '{key}' to '{value}'")

            __replacement_map_local.replacement_map[key] = value
        else:
            logger.info(f"Reset placeholder value '{key}' to ''")
            __replacement_map_local.replacement_map[key] = ""


def update_replacement_map_value_from_os(key: str) -> None:
    """
    Updates the value of the given key for the internally used replacement_map.
    For the update the value of the os environment variable is used, that matches
    the given key.

    Args:
        key: The key for which to update the value

    Returns:
        None
    """
    if os.getenv(key=key) is not None:
        set_replacement_map_value(key=key, value=os.getenv(key=key))


def update_replacement_map_from_os() -> None:
    """
    Calls the "update_replacement_map_value_from_os" method for every key of the
    internally used replacement map. This realizes the update of the value for any
    key that is set as os environment variable

    Returns:
        None
    """
    logger.debug("Update placeholder values from OS environment variables")
    for key in __replacement_map_local.replacement_map.keys():
        update_replacement_map_value_from_os(key=key)


def clear_replacement_map() -> None:
    """
    Clears the content of the internally used replacement_map

    Returns:
        None
    """
    __replacement_map_local.replacement_map.clear()


def clear_replacement_map_values() -> None:
    """
    Set every value of the internally used replacement_map to None

    Returns:
        None
    """
    for key in __replacement_map_local.replacement_map.keys():
        __replacement_map_local.replacement_map[key] = ""
