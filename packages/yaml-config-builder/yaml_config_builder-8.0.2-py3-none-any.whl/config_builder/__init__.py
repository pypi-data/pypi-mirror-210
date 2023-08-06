# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

""" Top-level YAML Config Builder package """

# -*- coding: utf-8 -*-
from .base_config_class import BaseConfigClass
from .config_builder import ConfigBuilder

__all__ = ["BaseConfigClass", "ConfigBuilder"]
__version__ = "8.0.2"
__license__ = "OLFL-1.3"
