"""
pier_cap/builder.py - Parametric 3D CAD Builder for Bridge Pier Cap (Hammerhead / Trapezoidal)
==============================================================================================
OsdagBridge Substructure Module - FOSSEE IIT Bombay Winter Internship

Builds:
- Parametric trapezoidal/hammerhead concrete pier cap:
    * pier_cap_top_width = 3000mm
    * pier_cap_bottom_width = 1200mm
    * pier_cap_depth = 600mm
    * pier_cap_length = Parameterized along transverse Y-axis
- Internal reinforcement rebar cage (main flexural rebars + stirrup links)
- Semi-transparent concrete display (opacity = 0.35) + metallic rebar
"""

import math
from typing import Dict, Any, List

DEFAULT_CAP_TOP_WIDTH = 3000.0       # mm (longitudinal X dimension at top)
DEFAULT_CAP_BOTTOM_WIDTH = 1200.0    # mm (longitudinal X dimension at bottom)
DEFAULT_CAP_DEPTH = 600.0            # mm (vertical Z dimension)
DEFAULT_CAP_LENGTH = 8500.0          # mm (transverse Y dimension matching deck)
DEFAULT_REBAR_COVER = 40.0           # mm
CONCRETE_OPACITY = 0.35


def build_pier_cap_parametric_data(
    top_width: float = DEFAULT_CAP_TOP_WIDTH,
    bottom_width: float = DEFAULT_CAP_BOTTOM_WIDTH,
    depth: float = DEFAULT_CAP_DEPTH,
    length: float = DEFAULT_CAP_LENGTH,
    center_x: float = 0.0,
    center_y: float = 0.0,
    top_z: float = 0.0
) -> Dict[str, Any]:
    """
    Computes parametric geometry of the hammerhead/trapezoidal pier cap
    and internal rebar cages for 3D visualization, BIM export, and quantities.
    """
    bottom_z = top_z - depth
    
    # 8 vertices of the trapezoidal prism
    # X: longitudinal, Y: transverse, Z: vertical
    half_L = length / 2.0
    half_top_W = top_width / 2.0
    half_bot_W = bottom_width / 2.0
    
    vertices = [
        # Top 4 vertices (Z = top_z)
        [-half_top_W, -half_L, top_z],
        [half_top_W, -half_L, top_z],
        [half_top_W, half_L, top_z],
        [-half_top_W, half_L, top_z],
        # Bottom 4 vertices (Z = bottom_z)
        [-half_bot_W, -half_L, bottom_z],
        [half_bot_W, -half_L, bottom_z],
        [half_bot_W, half_L, bottom_z],
        [-half_bot_W, half_L, bottom_z],
    ]
    
    # Rebar cage (Longitudinal top and bottom bars along Y axis + stirrups)
    rebar_bars = []
    
    # Top tensile reinforcement bars along transverse length
    n_top_bars = max(6, int(top_width / 200.0))
    for i in range(n_top_bars):
        rx = -half_top_W + DEFAULT_REBAR_COVER + (i * (top_width - 2 * DEFAULT_REBAR_COVER) / max(1, n_top_bars - 1))
        rz = top_z - DEFAULT_REBAR_COVER
        rebar_bars.append({
            "type": "cylinder",
            "name": f"Pier Cap Top Main Bar {i+1}",
            "diameter": 20.0,
            "start": [rx, -half_L + DEFAULT_REBAR_COVER, rz],
            "end": [rx, half_L - DEFAULT_REBAR_COVER, rz],
            "length": length - 2 * DEFAULT_REBAR_COVER,
            "material": "steel_rebar",
            "color": "#4A90E2",
            "opacity": 1.0
        })
        
    # Bottom reinforcement bars along transverse length
    n_bot_bars = max(4, int(bottom_width / 200.0))
    for i in range(n_bot_bars):
        rx = -half_bot_W + DEFAULT_REBAR_COVER + (i * (bottom_width - 2 * DEFAULT_REBAR_COVER) / max(1, n_bot_bars - 1))
        rz = bottom_z + DEFAULT_REBAR_COVER
        rebar_bars.append({
            "type": "cylinder",
            "name": f"Pier Cap Bot Main Bar {i+1}",
            "diameter": 16.0,
            "start": [rx, -half_L + DEFAULT_REBAR_COVER, rz],
            "end": [rx, half_L - DEFAULT_REBAR_COVER, rz],
            "length": length - 2 * DEFAULT_REBAR_COVER,
            "material": "steel_rebar",
            "color": "#4A90E2",
            "opacity": 1.0
        })
        
    concrete_solid = {
        "type": "trapezoidal_prism",
        "name": "Pier Cap Concrete",
        "top_width": top_width,
        "bottom_width": bottom_width,
        "depth": depth,
        "length": length,
        "center": [center_x, center_y, (top_z + bottom_z) / 2.0],
        "vertices": vertices,
        "material": "concrete_m40",
        "color": "#BDC3C7",
        "opacity": CONCRETE_OPACITY,
        "transparent": True
    }
    
    return {
        "component_type": "PierCap",
        "concrete": concrete_solid,
        "rebar": rebar_bars,
        "volume_m3": ((top_width + bottom_width) / 2.0 * depth * length) / 1e9
    }
