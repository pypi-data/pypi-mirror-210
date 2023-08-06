"""
Unit registry

Allows the user to pick a different registry if a different units system is
needed
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import openscm_units

if TYPE_CHECKING:
    import pint


UNIT_REGISTRY: pint.UnitRegistry = openscm_units.unit_registry
"""
Unit registry used throughout
"""
