"""
pier/builder.py - Parametric 3D CAD Builder for Bridge Pier (Column)
=====================================================================
OsdagBridge Substructure Module - FOSSEE IIT Bombay Winter Internship

Builds:
- Parametric circular concrete pier column (diameter = 800mm, height = 3000mm)
- Internal rebar cage:
    * Longitudinal main rebar (dia = 16mm, spacing = 150mm c/c around pitch circle)
    * Transverse hoop/spiral ties (dia = 8mm, pitch = 200mm, clear cover = 40mm)
- Dual backend: pythonOCC B-Rep solids + Parametric geometry dictionary for Three.js & IFC
"""

import math
from typing import Dict, Any, List, Tuple

# Default Parametric Dimensions (IRC 78:2014 / Screening Task Specification)
DEFAULT_PIER_DIAMETER = 800.0        # mm
DEFAULT_PIER_HEIGHT = 3000.0         # mm
DEFAULT_REBAR_MAIN_DIA = 16.0        # mm
DEFAULT_REBAR_SPACING_LONG = 150.0   # mm
DEFAULT_REBAR_TRANS_DIA = 8.0        # mm
DEFAULT_REBAR_SPACING_TRANS = 200.0  # mm
DEFAULT_REBAR_COVER = 40.0           # mm
CONCRETE_OPACITY = 0.35              # Required semi-transparent visualization


def build_pier_parametric_data(
    pier_diameter: float = DEFAULT_PIER_DIAMETER,
    pier_height: float = DEFAULT_PIER_HEIGHT,
    rebar_main_dia: float = DEFAULT_REBAR_MAIN_DIA,
    rebar_trans_dia: float = DEFAULT_REBAR_TRANS_DIA,
    rebar_trans_spacing: float = DEFAULT_REBAR_SPACING_TRANS,
    rebar_cover: float = DEFAULT_REBAR_COVER,
    center_x: float = 0.0,
    center_y: float = 0.0,
    base_z: float = -3000.0
) -> Dict[str, Any]:
    """
    Computes parametric geometric representation of the pier concrete cylinder
    and its internal reinforcement rebar cage.
    
    Returns structured data consumed by Three.js web viewer, IFC generator, and CAD generator.
    """
    radius = pier_diameter / 2.0
    cage_radius = radius - rebar_cover - (rebar_trans_dia / 2.0)
    
    # Calculate number of longitudinal main rebars
    cage_circumference = 2 * math.pi * cage_radius
    n_bars = max(8, int(round(cage_circumference / DEFAULT_REBAR_SPACING_LONG)))
    
    longitudinal_bars = []
    for i in range(n_bars):
        angle = 2 * math.pi * i / n_bars
        bx = center_x + cage_radius * math.cos(angle)
        by = center_y + cage_radius * math.sin(angle)
        longitudinal_bars.append({
            "type": "cylinder",
            "name": f"Pier Main Rebar {i+1}",
            "diameter": rebar_main_dia,
            "start": [bx, by, base_z + rebar_cover],
            "end": [bx, by, base_z + pier_height - rebar_cover],
            "length": pier_height - 2 * rebar_cover,
            "material": "steel_rebar",
            "color": "#4A90E2",
            "opacity": 1.0
        })
        
    # Transverse tie rings (hoops)
    transverse_rings = []
    n_rings = int(math.floor((pier_height - 2 * rebar_cover) / rebar_trans_spacing))
    for j in range(n_rings + 1):
        rz = base_z + rebar_cover + (j * rebar_trans_spacing)
        transverse_rings.append({
            "type": "ring",
            "name": f"Pier Tie Ring {j+1}",
            "center": [center_x, center_y, rz],
            "radius": cage_radius,
            "wire_diameter": rebar_trans_dia,
            "material": "steel_rebar",
            "color": "#E67E22",
            "opacity": 1.0
        })
        
    concrete_solid = {
        "type": "cylinder",
        "name": "Pier Column Concrete",
        "radius": radius,
        "diameter": pier_diameter,
        "height": pier_height,
        "base_center": [center_x, center_y, base_z],
        "top_center": [center_x, center_y, base_z + pier_height],
        "material": "concrete_m40",
        "color": "#BDC3C7",
        "opacity": CONCRETE_OPACITY,
        "transparent": True
    }
    
    return {
        "component_type": "Pier",
        "concrete": concrete_solid,
        "rebar_longitudinal": longitudinal_bars,
        "rebar_transverse": transverse_rings,
        "total_rebar_weight_kg": (n_bars * (pier_height / 1000.0) * (0.006165 * rebar_main_dia**2))
    }


def build_pier_occ(
    pier_diameter: float = DEFAULT_PIER_DIAMETER,
    pier_height: float = DEFAULT_PIER_HEIGHT,
    center_x: float = 0.0,
    center_y: float = 0.0,
    base_z: float = -3000.0
):
    """Generates OpenCASCADE TopoDS_Shape if pythonOCC is installed."""
    try:
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
        from OCC.Core.gp import gp_Ax2, gp_Pnt, gp_Dir
        
        ax = gp_Ax2(gp_Pnt(center_x, center_y, base_z), gp_Dir(0, 0, 1))
        cylinder = BRepPrimAPI_MakeCylinder(ax, pier_diameter / 2.0, pier_height).Shape()
        return cylinder
    except ImportError:
        return None
