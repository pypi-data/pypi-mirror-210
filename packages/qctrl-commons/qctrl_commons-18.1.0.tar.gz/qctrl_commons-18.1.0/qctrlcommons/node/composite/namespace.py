# Copyright 2023 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
"""
Namespaces for functions, nodes, and classes.
"""

from functools import partial
from typing import Any

NAMESPACE_ATTR = "namespace"
COMPOSITE_ATTR = "composite_node"


def composite_node(obj: Any) -> Any:
    """
    Define a decorator that sets a new attribute `composite_node` to True.
    """
    setattr(obj, COMPOSITE_ATTR, True)
    return obj


def set_namespace(namespace: str):
    """
    Define a decorator that sets a new attribute `namespace` to a given value.
    """
    assert isinstance(namespace, str), "The namespace must be a string."

    def _set_namespace(obj, attr):
        setattr(obj, NAMESPACE_ATTR, attr)
        return obj

    return partial(_set_namespace, attr=namespace)
