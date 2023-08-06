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
"""Module for custom Graph."""
import inspect
import logging
from functools import partial
from typing import (
    Any,
    Dict,
)

from qctrlcommons.node.composite.namespace import (
    COMPOSITE_ATTR,
    NAMESPACE_ATTR,
)
from qctrlcommons.node.composite.registry import COMPOSITE_NODE_REGISTRY
from qctrlcommons.node.registry import NODE_REGISTRY

LOGGER = logging.getLogger(__name__)


class Graph:
    """
    Utility class for representing and building a Q-CTRL data flow graph.

    You can call methods to add nodes to the graph, and use the `operations` attribute to get a
    dictionary representation of the graph.
    """

    def __init__(self):
        self.operations = {}
        self._add_composite_nodes()

    def __getattr__(self, attr):
        # We override getattr to stop pylint from complaining about missing attributes for methods
        # that are added dynamically.
        raise AttributeError(f"'Graph' object has no attribute '{attr}'.")

    def _add_composite_nodes(self):
        # We add the composite nodes to the graph in this way since the composite node namespaces
        # need access to the initialized class object.
        for composite_node in COMPOSITE_NODE_REGISTRY:
            _add_composite_method(self, composite_node)

    @classmethod
    def _from_operations(cls, operations: Dict[str, Any]):
        """
        Create a new graph from an existing set of operations.

        Parameters
        ----------
        operations : dict[str, Any]
            The initial dictionary of operations for the graph.
        """
        graph = cls()
        graph.operations = operations
        return graph


def _add_composite_method(obj, composite_node):
    """
    Extends the specified object by adding methods as attributes.

    Parameters
    ----------
    obj : Any
        The object to which the node should be added.
    composite_node : Any
        The composite node to be added to the object as a method.
    """
    assert hasattr(composite_node, COMPOSITE_ATTR)

    if inspect.isfunction(composite_node):
        # Add composite node function.
        _extend_method(obj, partial(composite_node, obj), composite_node.__name__)

    else:
        assert inspect.isclass(composite_node)
        if hasattr(composite_node, NAMESPACE_ATTR):
            # Add composite node namespace.
            _extend_method(
                obj, composite_node(obj), getattr(composite_node, NAMESPACE_ATTR)
            )

        else:
            # Add composite node dataclass.
            _extend_method(obj, composite_node, composite_node.__name__)


def _extend_method(obj, method, method_name):
    """
    Extends the specified object by adding methods as attributes.

    Parameters
    ----------
    obj : Any
        The object to which the node should be added.
    method : Any
        Method to be added to the object.
    method_name : str
        Name of the method to be added.
    """
    if hasattr(obj, method_name):
        LOGGER.debug("existing attr %s on namespace: %s", method_name, obj)
    else:
        LOGGER.debug("adding attr %s to namespace: %s", method_name, obj)
        setattr(obj, method_name, method)


# set nodes to Graph
for node_cls in NODE_REGISTRY.as_list():
    node = node_cls.create_graph_method()
    _extend_method(Graph, node, node.__name__)
