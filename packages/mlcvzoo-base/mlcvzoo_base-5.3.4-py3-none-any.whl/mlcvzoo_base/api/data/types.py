# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""
Module for storing types that are shared across the mlcvzoo
"""

from nptyping import Int, NDArray, Shape

ImageType = NDArray[Shape["Height, Width, Any"], Int]
