# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""Dataclass that holds attributes of Annotation objects"""


class AnnotationAttributes:
    """Class for describing different annotation attributes"""

    def __init__(
        self,
        difficult: bool,
        occluded: bool,
        content: str,
    ):
        self.__difficult: bool = difficult
        self.__occluded: bool = occluded
        self.__content: str = content

    @property
    def difficult(self) -> bool:
        return self.__difficult

    @property
    def occluded(self) -> bool:
        return self.__occluded

    @property
    def content(self) -> str:
        return self.__content
