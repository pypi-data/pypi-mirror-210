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
PWC and STF signal library nodes.
"""
from qctrlcommons.node.composite.namespace import (
    composite_node,
    set_namespace,
)
from qctrlcommons.node.composite.signals_pwc import PwcSignals
from qctrlcommons.node.composite.signals_stf import StfSignals


@composite_node
@set_namespace("signals")
class SignalsNamespace(PwcSignals, StfSignals):
    """
    Class for the PWC and STF Signal nodes.
    """
