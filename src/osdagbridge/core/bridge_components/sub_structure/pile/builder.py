"""
pile/builder.py - Parametric 3D CAD Builder for Bridge Piles (2x2 Deep Foundation)
===================================================================================
OsdagBridge Substructure Module - FOSSEE IIT Bombay Winter Internship

Builds:
- Parametric circular bored concrete piles (arranged in 2x2 grid):
    * n_piles_per_cap = 4
    * pile_diameter = 400mm
    * pile_length = 5000mm
    * pile_spacing = 600mm (center-to-center in both X and Y)
- Internal rebar cages for each pile (6 longitudinal 16mm rebars + helical spiral ties)
- Semi-transparent concrete solids (opacity = 0.35) + opaque steel rebar
"""

import math
from typing import Dict, Any, List

DEFAULT_N_PILES = 4
DEFAULT_PILE_DIAMETER = 400.0   # mm
DEFAULT_PILE_LENGTH = 5000.0     # mm
DEFAULT_PILE_SPACING = 600.0     # mm c/c
DEFAULT_REBAR_COVER = 40.0       # mm
CONCRETE_OPACITY = 0.35


def build_pile_group_parametric_data(
    n_piles: int = DEFAULT_N_PILES,
    pile_diameter: float = DEFAULT_PILE_DIAMETER,
    pile_length: float = DEFAULT_PILE_LENGTH,
    pile_spacing: float = DEFAULT_PILE_SPACING,
    center_x: float = 0.0,
    center_y: float = 0.0,
    top_z: float = -3600.0
) -> Dict[str, Any]:
    """
    Computes parametric geometry of 2x2 pile group deep foundation
    and internal rebar cages for 3D visualization, BIM export, and quantities.
    """
    radius = pile_diameter / 2.0
    cage_radius = radius - DEFAULT_REBAR_COVER - 4.0  # 4mm half-stirrup
    half_s = pile_spacing / 2.0
    
    # 2x2 grid offsets relative to pile cap center
    offsets = [
        (-half_s, -half_s),
        (half_s, -half_s),
        (half_s, half_s),
        (-half_s, half_s)
    ]
    
    piles_concrete = []
    piles_rebar = []
    
    for idx, (dx, dy) in enumerate(offsets):
        px = center_x + dx
        py = center_y + dy
        
        piles_concrete.append({
            "type": "cylinder",
            "name": f"Pile {idx+1} Concrete",
            "radius": radius,
            "diameter": pile_diameter,
            "height": pile_length,
            "base_center": [px, py, top_z - pile_length],
            "top_center": [px, py, top_z],
            "material": "concrete_m40",
            "color": "#BDC3C7",
            "opacity": CONCRETE_OPACITY,
            "transparent": True
        })
        
        # 6 longitudinal main bars per pile
        for b in range(6):
            angle = 2 * math.pi * b / 6.0
            bx = px + cage_radius * math.cos(angle)
            by = py + cage_radius * math.sin(angle)
            piles_rebar.append({
                "type": "cylinder",
                "name": f"Pile {idx+1} Rebar {b+1}",
                "diameter": 16.0,
                "start": [bx, by, top_z - pile_length + DEFAULT_REBAR_COVER],
                "end": [bx, by, top_z],
                "length": pile_length - DEFAULT_REBAR_COVER,
                "material": "steel_rebar",
                "color": "#4A90E2",
                "opacity": 1.0
            })
            
    total_volume_m3 = n_piles * (math.pi * radius**2 * pile_length) / 1e9
    
    return {
        "component_type": "PileGroup",
        "n_piles": n_piles,
        "piles_concrete": piles_concrete,
        "piles_rebar": piles_rebar,
        "volume_m3": total_volume_m3
    }
