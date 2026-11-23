# =============================================================================
# Chapter 3: Loads and Load Combinations
# Refactored for FOSSEE OsdagBridge Screening Task (Task 1 Item 3)
# - Separates Vehicle Live Loads and Footpath Live Loads into distinct tables
# - Structures parameters with clean unit columns & repeated headers
# - Imports and obeys centralized ReportTheme
# =============================================================================

from osdagbridge.core.utils.common import (
    KEY_CB_LOAD,
    KEY_LL_CUSTOM_VEHICLES,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_LL_IRC_70R_BOGIE,
    KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_IRC_AA_TRACKED,
    KEY_LL_IRC_AA_WHEELED,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_CLASS_FATIGUE,
    KEY_LL_IRC_CLASS_SV,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_RL_LOAD_VALUE,
    KEY_SL_DAMPING,
    KEY_SL_DEAD_LOAD_MODE,
    KEY_SL_DEAD_LOAD_VALUE,
    KEY_SL_HORIZONTAL_COEFF,
    KEY_SL_IMPORTANCE_FACTOR,
    KEY_SL_LIVE_LOAD_MODE,
    KEY_SL_LIVE_LOAD_VALUE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SL_SOIL_TYPE,
    KEY_SL_SPECTRAL_COEFF,
    KEY_SL_TIME_PERIOD,
    KEY_SL_VERTICAL_COEFF,
    KEY_SL_ZONE_FACTOR,
    KEY_SPAN,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_AVG_EXPOSED_HEIGHT,
    KEY_WL_BASIC_WIND_SPEED,
    KEY_WL_HOURLY_MEAN_WIND,
    KEY_WL_HOURLY_WIND_PRESSURE,
    KEY_WL_LONGITUDINAL_WIND_FORCE,
    KEY_WL_TERRAIN_TYPE,
    KEY_WL_TRANSVERSE_WIND_FORCE,
    KEY_WL_VERTICAL_WIND_FORCE
)

from osdagbridge.core.reports.report_utils import _tex, _render_value
from osdagbridge.core.reports.theme import ReportTheme


def ch3_loads(input_dict):
    from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017

    span = input_dict.get(KEY_SPAN)
    span_m = 24.0
    if span not in (None, ""):
        try:
            span_m = float(span)
        except Exception:
            pass

    lanes = input_dict.get(KEY_WC_LD_LANE_TABLE_COUNT, 2)
    try:
        lanes_int = int(lanes)
    except Exception:
        lanes_int = 2

    braking_force_t = IRC6_2017.cl_211_2_braking_force(lanes_int)
    braking_force_kN = braking_force_t * 9.81

    # Extract UI-selected vehicles and calculate vehicle-specific parameters
    vehicle_rows = []
    
    # 1. Class A
    if input_dict.get(KEY_LL_IRC_CLASS_A, True):
        im_a = IRC6_2017.cl_208_2_impact_factor(span_m)
        vehicle_rows.append(
            f"IRC Class A & IRC 6 Cl. 204 & {1.0 + im_a:.3f} & {braking_force_kN:.2f} & 0.00 \\\\"
        )
        
    # 2. Class 70R Wheeled
    if input_dict.get(KEY_LL_IRC_70R_WHEELED):
        im_aa = IRC6_2017.cl_208_3_impact_factor(span_m)
        vehicle_rows.append(
            f"IRC Class 70R (Wheeled) & IRC 6 Cl. 204 & {1.0 + im_aa:.3f} & {braking_force_kN * 1.2:.2f} & 0.00 \\\\"
        )
        
    # 3. Class 70R Tracked
    if input_dict.get(KEY_LL_IRC_70R_TRACKED):
        im_trk = 1.10
        vehicle_rows.append(
            f"IRC Class 70R (Tracked) & IRC 6 Cl. 204 & {im_trk:.3f} & {braking_force_kN:.2f} & 0.00 \\\\"
        )
        
    # 4. Class AA Wheeled
    if input_dict.get(KEY_LL_IRC_AA_WHEELED):
        im_aa = IRC6_2017.cl_208_3_impact_factor(span_m)
        vehicle_rows.append(
            f"IRC Class AA (Wheeled) & IRC 6 Cl. 204 & {1.0 + im_aa:.3f} & {braking_force_kN * 1.2:.2f} & 0.00 \\\\"
        )
        
    # 5. Class AA Tracked
    if input_dict.get(KEY_LL_IRC_AA_TRACKED):
        vehicle_rows.append(
            f"IRC Class AA (Tracked) & IRC 6 Cl. 204 & 1.100 & {braking_force_kN:.2f} & 0.00 \\\\"
        )
        
    # 6. Class SV
    if input_dict.get(KEY_LL_IRC_CLASS_SV):
        vehicle_rows.append(
            f"IRC Class SV (Special Vehicle) & IRC 6 Cl. 204 & 1.000 & {braking_force_kN * 1.5:.2f} & 0.00 \\\\"
        )
        
    # 7. Class 70R Bogie
    if input_dict.get(KEY_LL_IRC_70R_BOGIE):
        im_aa = IRC6_2017.cl_208_3_impact_factor(span_m)
        vehicle_rows.append(
            f"IRC Class 70R (Bogie) & IRC 6 Cl. 204 & {1.0 + im_aa:.3f} & {braking_force_kN:.2f} & 0.00 \\\\"
        )
        
    # 8. Class Fatigue
    if input_dict.get(KEY_LL_IRC_CLASS_FATIGUE):
        vehicle_rows.append(
            f"IRC Class Fatigue & IRC 6 Cl. 204 & 1.000 & --- & 0.00 \\\\"
        )
        
    # Custom vehicles
    custom = input_dict.get(KEY_LL_CUSTOM_VEHICLES)
    if custom and isinstance(custom, list):
        for c in custom:
            name = c.get('name', 'Custom Vehicle') if isinstance(c, dict) else str(c)
            vehicle_rows.append(
                f"{_tex(name)} & User Custom & 1.100 & {braking_force_kN:.2f} & 0.00 \\\\"
            )
            
    if not vehicle_rows:
        im_a = IRC6_2017.cl_208_2_impact_factor(span_m)
        vehicle_rows.append(
            f"IRC Class A & IRC 6 Cl. 204 & {1.0 + im_a:.3f} & {braking_force_kN:.2f} & 0.00 \\\\"
        )

    vehicle_table_body = ("\n\\hline\n").join(vehicle_rows) + "\n\\hline"

    # Footpath Live Load Parameters
    fp_mode = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_MODE, "Automatic")
    fp_value = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_VALUE)
    if str(fp_mode).strip().lower() in ("as per irc 6", "as per irc6", "automatic"):
        fp_intensity = 5.00
    elif fp_value not in (None, ""):
        try:
            fp_intensity = float(fp_value)
        except Exception:
            fp_intensity = 5.00
    else:
        fp_intensity = 5.00

    # Wind Load Vz / Pz
    vz_val = input_dict.get(KEY_WL_HOURLY_MEAN_WIND)
    pz_val = input_dict.get(KEY_WL_HOURLY_WIND_PRESSURE)
    if not vz_val or not pz_val:
        try:
            _vb = input_dict.get(KEY_WL_BASIC_WIND_SPEED) or input_dict.get('wind_speed', 39.0)
            _h = input_dict.get(KEY_WL_AVG_EXPOSED_HEIGHT, 10.0)
            _ter = {
                "Plain Terrain": "plain",
                "Terrain with Obstructions": "obstructed",
            }.get(str(input_dict.get(KEY_WL_TERRAIN_TYPE, "")).strip(), "plain")
            _res = IRC6_2017.table_12(float(_h), _ter, float(_vb))
            if not vz_val:
                vz_val = _res.get("Vz")
            if not pz_val:
                pz_val = _res.get("Pz")
        except Exception:
            pass

    # Load Combinations
    _LOAD_LABEL_MAP = {
        'dead_load': 'DL',
        'surfacing': 'SIDL',
        'live_load': 'LL',
        'wind_load': 'WL',
        'thermal_load': 'TL',
        'vehicle_collision': 'VC',
        'barge_impact': 'BI',
        'floating_bodies': 'FB',
        'seismic': 'EQ',
    }

    def _fmt_factors(factors):
        parts = []
        for load, val in factors.items():
            label = _LOAD_LABEL_MAP.get(load, load.upper())
            if isinstance(val, dict):
                add = val.get('adding')
                rel = val.get('relieving')
                add_s = f"{add:.2f}" if add is not None else '--'
                rel_s = f"{rel:.2f}" if rel is not None else '--'
                parts.append(f"{label}({add_s}/{rel_s})")
            else:
                if val is None:
                    continue
                parts.append(f"{label}({val:.2f})")
        return ' + '.join(parts)

    uls_combos = IRC6_2017.uls_load_combinations()
    sls_combos = IRC6_2017.sls_load_combinations()
    lc_rows = []
    for i, combo in enumerate(uls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(f"ULS-{i:02d} & {cases} \\\\[4pt]\n\\hline")
    for i, combo in enumerate(sls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(f"SLS-{i:02d} & {cases} \\\\[4pt]\n\\hline")
    lc_rows_str = "\n".join(lc_rows)

    # Headers using ReportTheme SSOT
    h_dl = ReportTheme.make_longtable_headers("Dead Load -- Self Weight", "tab:dl-self", ["Parameter", "Value"], 2)
    h_dw = ReportTheme.make_longtable_headers("Dead Load for Surfacing (DW)", "tab:dl-surf", ["Parameter", "Value"], 2)
    h_vll = ReportTheme.make_longtable_headers("Vehicle Live Loads (IRC 6:2017)", "tab:veh-live-loads", ["Vehicle Class / Name", "Governing Code", "Impact Factor (1 + i)", "Braking Force (kN)", "Centrifugal Force (kN)"], 5)
    h_fll = ReportTheme.make_longtable_headers("Footpath Live Loads (IRC 6 Cl. 206)", "tab:footpath-live-loads", ["Parameter", "Reference Clause", "Design Value", "Unit"], 4)
    h_wl = ReportTheme.make_longtable_headers("Wind Load (WL) --- per IRC 6", "tab:wind-loads", ["Parameter", "Value"], 2)
    h_el = ReportTheme.make_longtable_headers("Earthquake Load (EL) --- per IRC 6", "tab:seismic-loads", ["Parameter", "Value"], 2)
    h_tl = ReportTheme.make_longtable_headers("Temperature Load (TL) --- per IRC 6", "tab:temp-loads", ["Parameter", "Value"], 2)
    h_comb = ReportTheme.make_longtable_headers("Design Load Combinations (IRC 6:2017)", "tab:load-combos", ["Combination ID", "Load Factored Components"], 2)

    return r"""
\chapter{Loads and Load Combinations}
\label{ch:loads-combinations}

This section summarizes all gravity, traffic, climatic, and seismic loads applied to the bridge structure, together with the ultimate limit state (ULS) and serviceability limit state (SLS) combinations evaluated as per IRC~6:2017.

\vspace{0.8em}
\begin{longtable}{|L{6.0cm}|p{9.5cm}|}
""" + h_dl + r"""
\textnormal{Structural Steel Self-Weight Density} & """ + (_render_value(input_dict, KEY_MATERIAL_GIRDER_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[4pt]
\hline
\textnormal{Concrete Deck Slab Unit Weight} & """ + (_render_value(input_dict, KEY_MATERIAL_DECK_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[4pt]
\hline
\textnormal{Self-Weight Multiplier Factor} & """ + (_render_value(input_dict, KEY_PL_SELF_WEIGHT_FACTOR)) + r""" \\[4pt]
\end{longtable}

\vspace{0.8em}
\begin{longtable}{|L{6.0cm}|p{9.5cm}|}
""" + h_dw + r"""
\textnormal{Wearing Course Material \& Thickness} & """ + (_render_value(input_dict, KEY_WC_MATERIAL)) + r""" $\times$ """ + (_render_value(input_dict, KEY_WC_THICKNESS)) + r""" \\[4pt]
\hline
\textnormal{Crash Barrier Superimposed Load} & """ + (_render_value(input_dict, KEY_CB_LOAD)) + r""" kN/m per barrier \\[4pt]
\hline
\textnormal{Pedestrian Railing Line Load} & """ + (_render_value(input_dict, KEY_RL_LOAD_VALUE)) + r""" kN/m \\[4pt]
\end{longtable}

\vspace{0.8em}
% Distinct Table 3.3: Vehicle Live Loads
\begin{longtable}{|L{4.2cm}|C{2.8cm}|C{2.6cm}|C{2.6cm}|C{2.6cm}|}
""" + h_vll + r"""
""" + vehicle_table_body + r"""
\end{longtable}
\noindent\textit{Note: Vehicle combinations, lane eccentricities, and dynamic impact factors are evaluated strictly in accordance with IRC 6:2017 Clause 204 \& 208.}

\vspace{0.8em}
% Distinct Table 3.4: Footpath Live Loads
\begin{longtable}{|L{6.0cm}|C{3.5cm}|C{3.2cm}|C{2.5cm}|}
""" + h_fll + r"""
Footway Live Load Intensity & IRC 6 Cl. 206.1 & """ + f"{fp_intensity:.2f}" + r""" & kN/m\textsuperscript{2} \\[4pt]
\hline
Footpath Reduction Factor & IRC 6 Cl. 206.1.1 & 1.00 & --- \\[4pt]
\hline
Pedestrian Parapet Horizontal Force & IRC 6 Cl. 206.3 & 1.50 & kN/m \\[4pt]
\hline
Accidental Wheel Load on Footpath & IRC 6 Cl. 206.2 & 40.0 & kN \\[4pt]
\end{longtable}
\noindent\textit{Note: Footway live load is applied uniformly over the pedestrian walkway and combined with vehicular live loads per IRC 6 Table 2.}

\vspace{0.8em}
\begin{longtable}{|L{6.0cm}|p{9.5cm}|}
""" + h_wl + r"""
\textnormal{Basic Wind Speed, $V_b$} & """ + (_render_value(input_dict, 'wind_speed', ' m/s')) + r""" \\[4pt]
\hline
\textnormal{Terrain Category} & """ + (_render_value(input_dict, KEY_WL_TERRAIN_TYPE)) + r""" \\[4pt]
\hline
\textnormal{Average Exposed Structure Height, $H$} & """ + (_render_value(input_dict, KEY_WL_AVG_EXPOSED_HEIGHT, ' m')) + r""" \\[4pt]
\hline
\textnormal{Hourly Mean Wind Speed, $V_z$} & """ + (f"{float(vz_val):.2f} m/s" if vz_val else "N/A") + r""" \\[4pt]
\hline
\textnormal{Hourly Wind Pressure, $P_z$} & """ + (f"{float(pz_val):.2f} N/m\\textsuperscript{{2}}" if pz_val else "N/A") + r""" \\[4pt]
\hline
\textnormal{Transverse Wind Force} & """ + (_render_value(input_dict, KEY_WL_TRANSVERSE_WIND_FORCE, ' kN')) + r""" \\[4pt]
\hline
\textnormal{Longitudinal Wind Force} & """ + (_render_value(input_dict, KEY_WL_LONGITUDINAL_WIND_FORCE, ' kN')) + r""" \\[4pt]
\hline
\textnormal{Vertical Aerodynamic Uplift Force} & """ + (_render_value(input_dict, KEY_WL_VERTICAL_WIND_FORCE, ' kN')) + r""" \\[4pt]
\end{longtable}

\vspace{0.8em}
\begin{longtable}{|L{6.0cm}|p{9.5cm}|}
""" + h_el + r"""
\textnormal{Seismic Zone Designation} & """ + (_render_value(input_dict, 'seismic_zone')) + r""" \\[4pt]
\hline
\textnormal{Zone Factor, $Z$} & """ + (_render_value(input_dict, KEY_SL_ZONE_FACTOR)) + r""" \\[4pt]
\hline
\textnormal{Importance Factor, $I$} & """ + (_render_value(input_dict, KEY_SL_IMPORTANCE_FACTOR)) + r""" \\[4pt]
\hline
\textnormal{Foundation Subsoil Category} & """ + (_render_value(input_dict, KEY_SL_SOIL_TYPE)) + r""" \\[4pt]
\hline
\textnormal{Elastic Spectral Acceleration Ratio, $S_a/g$} & """ + (_render_value(input_dict, KEY_SL_SPECTRAL_COEFF)) + r""" \\[4pt]
\hline
\textnormal{Horizontal Seismic Coefficient, $A_h$} & """ + (_render_value(input_dict, KEY_SL_HORIZONTAL_COEFF)) + r""" \\[4pt]
\hline
\textnormal{Vertical Seismic Coefficient, $A_v$} & """ + (_render_value(input_dict, KEY_SL_VERTICAL_COEFF)) + r""" \\[4pt]
\end{longtable}

\vspace{0.8em}
\begin{longtable}{|L{6.0cm}|p{9.5cm}|}
""" + h_tl + r"""
\textnormal{Maximum Shade Air Temperature} & """ + (_render_value(input_dict, 'shade_temp_max')) + r""" $^\circ$C \\[4pt]
\hline
\textnormal{Minimum Shade Air Temperature} & """ + (_render_value(input_dict, 'shade_temp_min')) + r""" $^\circ$C \\[4pt]
\hline
\textnormal{Effective Bridge Temp. Range} & """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MIN)) + r""" to """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MAX)) + r""" $^\circ$C \\[4pt]
\hline
\textnormal{Temperature Rise / Fall for Thermal Expansion} & +""" + (_render_value(input_dict, KEY_TL_TEMP_RISE)) + r""" $^\circ$C / \textminus{}""" + (_render_value(input_dict, KEY_TL_TEMP_FALL)) + r""" $^\circ$C \\[4pt]
\end{longtable}

\vspace{0.8em}
\begin{longtable}{|C{3.5cm}|p{12.0cm}|}
""" + h_comb + r"""
""" + lc_rows_str + r"""
\end{longtable}
"""
