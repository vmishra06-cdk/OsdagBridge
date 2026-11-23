"""
sub_structure/builder.py - Unified Parametric 3D Substructure Assembly Builder
=============================================================================
OsdagBridge Substructure Module - FOSSEE IIT Bombay Winter Internship

Assembles the full substructure system:
1. Pier Caps (Hammerhead trapezoidal at each support line)
2. Pier Columns (Circular 800mm dia with rebar cages)
3. Pile Caps (Rectangular footings)
4. 2x2 Piles (400mm dia bored cast-in-situ piles with rebar)

Aligns strictly with the global bridge coordinate system:
- X: Longitudinal direction (along span)
- Y: Transverse direction (across bridge width)
- Z: Vertical direction (Origin at center of span on deck level)
"""

from typing import Dict, Any, List
from .pier.builder import build_pier_parametric_data
from .pier_cap.builder import build_pier_cap_parametric_data
from .pile_cap.builder import build_pile_cap_parametric_data
from .pile.builder import build_pile_group_parametric_data


def build_full_substructure_assembly(
    span_length: float = 24000.0,
    deck_width: float = 8500.0,
    girder_depth: float = 1600.0,
    pier_diameter: float = 800.0,
    pier_height: float = 3000.0,
    pier_cap_depth: float = 600.0,
    pile_cap_depth: float = 600.0,
    pile_length: float = 5000.0
) -> Dict[str, Any]:
    """
    Builds the complete substructure assemblies for both ends of the bridge span
    (X = -span_length / 2 and X = +span_length / 2).
    """
    support_x_positions = [-span_length / 2.0, span_length / 2.0]
    
    # Substructure Z layout below the steel girder bottom flange
    # Deck top = Z=0
    # Girder bottom = -girder_depth (approx -1600mm)
    # Pier Cap top = -girder_depth - 150mm (bearing pedestal allowance)
    # Pier Cap bottom = Pier top = pier_cap_top_z - pier_cap_depth
    # Pier bottom = Pile Cap top = pier_bottom_z - pier_height
    # Pile Cap bottom = Pile top = pile_cap_top_z - pile_cap_depth
    # Pile bottom = pile_top_z - pile_length
    
    pier_cap_top_z = -girder_depth - 150.0
    pier_top_z = pier_cap_top_z - pier_cap_depth
    pier_bottom_z = pier_top_z - pier_height
    pile_cap_top_z = pier_bottom_z
    pile_cap_bottom_z = pile_cap_top_z - pile_cap_depth
    pile_top_z = pile_cap_bottom_z
    
    substructure_components = []
    total_concrete_volume = 0.0
    total_rebar_weight = 0.0
    
    for idx, sx in enumerate(support_x_positions):
        loc_name = "Start Abutment/Pier" if idx == 0 else "End Abutment/Pier"
        
        # 1. Pier Cap
        cap_data = build_pier_cap_parametric_data(
            top_width=3000.0,
            bottom_width=1200.0,
            depth=pier_cap_depth,
            length=deck_width,
            center_x=sx,
            center_y=0.0,
            top_z=pier_cap_top_z
        )
        cap_data["location"] = loc_name
        substructure_components.append(cap_data)
        total_concrete_volume += cap_data["volume_m3"]
        
        # 2. Pier Column
        pier_data = build_pier_parametric_data(
            pier_diameter=pier_diameter,
            pier_height=pier_height,
            center_x=sx,
            center_y=0.0,
            base_z=pier_bottom_z
        )
        pier_data["location"] = loc_name
        substructure_components.append(pier_data)
        total_concrete_volume += (3.14159 * (pier_diameter / 2.0)**2 * pier_height) / 1e9
        total_rebar_weight += pier_data["total_rebar_weight_kg"]
        
        # 3. Pile Cap
        pile_cap_data = build_pile_cap_parametric_data(
            length=2200.0,
            width=1200.0,
            depth=pile_cap_depth,
            center_x=sx,
            center_y=0.0,
            top_z=pile_cap_top_z
        )
        pile_cap_data["location"] = loc_name
        substructure_components.append(pile_cap_data)
        total_concrete_volume += pile_cap_data["volume_m3"]
        
        # 4. 2x2 Piles
        piles_data = build_pile_group_parametric_data(
            n_piles=4,
            pile_diameter=400.0,
            pile_length=pile_length,
            pile_spacing=600.0,
            center_x=sx,
            center_y=0.0,
            top_z=pile_top_z
        )
        piles_data["location"] = loc_name
        substructure_components.append(piles_data)
        total_concrete_volume += piles_data["volume_m3"]
        
    return {
        "components": substructure_components,
        "total_concrete_volume_m3": round(total_concrete_volume, 2),
        "total_rebar_weight_kg": round(total_rebar_weight, 2),
        "elevation_levels": {
            "pier_cap_top_z": pier_cap_top_z,
            "pier_top_z": pier_top_z,
            "pile_cap_top_z": pile_cap_top_z,
            "pile_top_z": pile_top_z,
            "pile_toe_z": pile_top_z - pile_length
        }
    }
