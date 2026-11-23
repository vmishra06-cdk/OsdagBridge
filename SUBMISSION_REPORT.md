# FOSSEE Osdag Winter Internship 2026 - Screening Task Submission Report
**Project Name:** Osdag / OsdagBridge  
**Organization:** FOSSEE, IIT Bombay  
**Candidate Submission & Technical Architecture Report**  

---

## 1. Executive Summary

This project delivers a complete, deployable, full-stack implementation of the **OsdagBridge** software enhancements addressing the official FOSSEE IIT Bombay Winter Internship 2026 screening task categories:

1. **LaTeX Report Generator Refactoring & Enhancements**
2. **UI, 2D CAD Parameter Editing, and Transverse Result Plotting**
3. **Parametric 3D CAD Modeling of Bridge Substructure and IFC Workflow Integration**
4. **OsdagBridge Software Testing, Multi-Run State Verification & Issue Reporting**

The software is accessible immediately via local web deployment at **`http://localhost:8080`** as well as through modular desktop Python packages.

---

## 2. Key Modules & Technical Implementation

### Module I: LaTeX Report Generator Refactoring & Enhancements
- **Centralized Style System (`theme.py`):**
  Established a Single Source of Truth (SSOT) defining document geometry, margin threshold buffers, institutional color palettes (Osdag Navy `#1B365D`, Steel Blue `#006699`, Pass Green `#27AE60`, Fail Red `#C0392B`), table cell paddings, and header/footer configurations.
- **Repeated LongTable Headers Across Page Breaks:**
  Implemented standardized `\endfirsthead`, `\endhead`, `\endfoot`, and `\endlastfoot` headers across all multi-page tables (Chapter 3 Loads, Chapter 5 Design Checks, Chapter 7 Material Take-Off) ensuring table headers repeat on every page transition.
- **Vertical Spacing & Footer Overlap Fixes:**
  Added page-bottom threshold constraints and ragged-bottom buffer controls preventing table rows (such as Girder G4 stiffeners) from bleeding into footer margins.
- **Load & Geometry Table Refactoring:**
  Separated Vehicle Live Loads (IRC 6:2017) and Footpath Live Loads (IRC 6 Cl. 206) into distinct, structured tables with clean unit columns.
- **Programmatic Utilization Ratio (UR) Summary Visualizations:**
  Generated high-resolution (300 DPI) bar charts showing Demand/Capacity Utilization Ratios for Steel Plate Girders, Concrete Deck Slab, Cross Bracing, and End Diaphragms with a prominent horizontal red dashed reference line at $UR = 1.0$ distinguishing passing vs failing checks. Dynamically embedded into Section 5.5.
- **Material Quantity Bar Charts:**
  Generated visual breakdowns of Structural Steel tonnage (Girders, Cross Bracing, End Diaphragms) and Concrete Volume ($m^3$) vs Reinforcement Steel Weight (MT) dynamically embedded into Chapter 7.

---

### Module II: UI, 2D CAD, and Plotting Enhancements
- **Interactive 2D CAD Parameter Editing:**
  Implemented double-click event listeners on dimension labels within the 2D CAD canvas.
  - *Editable Parameters:* Carriageway Width, Girder Spacing, Deck Thickness, Span Length.
  - *Locked Parameters:* Overhang, Overall Bridge Width, and Bracing Spacing remain locked as read-only derived values to prevent geometric inconsistencies.
  - *Behavior:* Double-clicking transforms the label into an in-place input box; confirming pushes the validated value to the state and re-solves layout and CAD graphics.
- **Additional Inputs Pre-Save Validation & State Management:**
  - *Pre-Save Validation:* Intercepts the Save event and iterates all active tabs. If any parameter has its radio/mode set to "Custom" but the field is left empty, save is halted and triggers the exact standard error dialog:
    `Error: The custom value for '[Parameter Name]' cannot be empty.`
  - *Unsaved Changes Guard:* Tracks an `is_modified` flag. Closing the window or navigating with unsaved edits prompts:
    `"You have unsaved changes. Closing this window will discard them. Do you want to proceed?" (Discard / Cancel)`
- **Transverse Member Result Plotting:**
  Expanded the post-analysis plotting module to support **Transverse Members** (End Diaphragms, Intermediate Cross Bracings) alongside Longitudinal Girders, plotting $M_z, M_y, V_y, V_z, F_x,$ and deflections across IRC load cases (DL, SIDL, Class A, Class 70R, ULS-1, SLS-1).

---

### Module III: Parametric 3D CAD Modeling of Bridge Substructure & IFC Integration
- **Parametric Substructure Components:**
  - **Piers (Circular Columns):** Diameter $= 800\text{ mm}$, Height $= 3000\text{ mm}$.
  - **Pier Cap (Hammerhead / Trapezoidal):** Top width $= 3000\text{ mm}$, bottom width $= 1200\text{ mm}$, depth $= 600\text{ mm}$, length $= 8500\text{ mm}$ (matched to deck).
  - **Pile Cap (Rectangular Prism):** Length $= 2200\text{ mm}$, width $= 1200\text{ mm}$, depth $= 600\text{ mm}$.
  - **Piles (2x2 Group):** 4 circular bored piles, diameter $= 400\text{ mm}$, length $= 5000\text{ mm}$, center-to-center spacing $= 600\text{ mm}$.
  - **Reinforcement Details:** $16\text{ mm}$ longitudinal main bars ($150\text{ mm}$ spacing), $8\text{ mm}$ transverse spiral/hoop ties ($200\text{ mm}$ pitch), $40\text{ mm}$ clear cover.
- **Visual Display:**
  Concrete solids rendered with semi-transparency (opacity $= 0.35$); internal steel rebar cages rendered with opaque metallic shading.
- **BIM & IFC Workflow Integration:**
  Export pipeline generates valid IFC 2X3/4 models with complete spatial hierarchy:
  `IfcProject` $\rightarrow$ `IfcSite` $\rightarrow$ `IfcBuilding` $\rightarrow$ `IfcBuildingStorey` (Superstructure & Substructure) containing `IfcBeam`, `IfcSlab`, `IfcColumn`, `IfcFooting`, `IfcPile`, and `IfcReinforcingBar`.

---

### Module IV: Software Testing & Issue Reporting
- **Automated Verification:**
  - Test Suite 1: Material Customization persistence (verifying custom values do not revert to defaults).
  - Test Suite 2: Multi-run state persistence across 3 consecutive analysis runs without stale variables or memory leaks.
  - Test Suite 3: Pre-save validation for empty custom inputs.
  - Test Suite 4: Substructure geometric coordinates and rebar cage alignment.
- **Documented GitHub Issues:**
  Logged structured code-level bug reports with root causes and exact line modifications for upstream OsdagBridge dev repository.

---

## 3. How to Run on Localhost

1. Ensure the server is running:
   ```bash
   python3 OsdagBridge/web/server.py
   ```
2. Open your web browser and navigate to:
   ```
   http://localhost:8080
   ```
3. Interactive Features Available on Localhost:
   - **3D CAD View:** Orbit, pan, zoom, toggle rebar visibility, isolate substructure.
   - **2D CAD View:** Double click Carriageway Width or Girder Spacing to edit and see immediate updates.
   - **Transverse Plots:** Switch member dropdown between Longitudinal Girders, End Diaphragms, and Cross Bracings.
   - **Download .IFC:** Generates and downloads the full 3D BIM model file.
   - **Run Test Suite:** Executes automated test scenarios live.
