# apps/pages/ductfittingcoefficients.py
import dash
from dash import register_page, html, dcc, Input, Output, dash_table, callback

register_page(__name__, path="/ductfittings", name="Duct Fitting Coefficients")

# =========================================================================
# SHARED / REUSED TABLES
# These correction tables get used by many different fittings, so we
# define them once here and just reference them below instead of
# retyping the same numbers over and over.
# =========================================================================

BEND_ANGLE_CORRECTION_001 = {
    "title": "Bend Angle Correction (as for Fitting No. 001)",
    "columns": ["Bend Angle (°)", "Correction"],
    "rows": [["20",0.31],["30",0.45],["45",0.60],["60",0.78],["75",0.90],
             ["90",1.00],["110",1.13],["130",1.20],["150",1.28],["180",1.40]],
}

REYNOLDS_CORRECTION_001 = {
    "title": "Reynolds Number Correction k_Re (as for Fitting No. 001)",
    "columns": ["Re × 10⁻⁴", "k_Re"],
    "rows": [["1.0",2.00],["2.0",1.77],["3.0",1.64],["4.0",1.56],["6.0",1.46],
             ["8.0",1.38],["10.0",1.30],["14.0",1.15],["≥20.0",1.00]],
}

BEND_ANGLE_CORRECTION_021 = {
    "title": "Bend Angle Correction (as for Fitting No. 021)",
    "columns": ["Bend Angle (°)", "Correction"],
    "rows": [["90",1.00],["75",0.67],["60",0.46],["45",0.28],["30",0.13],["20",0.06]],
}

REYNOLDS_CORRECTION_021 = {
    "title": "Reynolds Number Correction k_Re (as for Fitting No. 021)",
    "columns": ["Re × 10⁻⁴", "k_Re"],
    "rows": [["1.0",1.40],["2.0",1.26],["3.0",1.19],["4.0",1.14],["6.0",1.09],
             ["8.0",1.06],["10.0",1.04],["≥14.0",1.00]],
}

ANGLE_FACTOR_023 = {
    "title": "Bend Angle Factor (as for Fitting No. 023)",
    "columns": ["Angle θ (°)", "Factor"],
    "rows": [["90",1.20],["75",0.81],["60",0.55],["45",0.34],["30",0.16],["20",0.08]],
}

STRAIGHT_THROUGH_401 = {
    "title": "Straight Through — kT vs Velocity Ratio (V_D/V_U)",
    "columns": ["V_D/V_U", "kT"],
    "rows": [["0.4",0.12],["0.5",0.09],["0.6",0.06],["0.7",0.03],["0.8–1.0",0]],
}

STRAIGHT_THROUGH_405 = {
    "title": "Straight Through — kT vs Velocity Ratio (V_B/V_U)",
    "columns": ["V_B/V_U", "kT"],
    "rows": [["0.2",0.03],["0.4",0.04],["0.6",0.07],["0.8",0.12],["1.0",0.13],
             ["1.2",0.14],["1.4",0.27],["1.6",0.30],["1.8",0.25]],
}

FIG_6_30C_EXPANSION = {
    "title": "Fig. 6-30C — Abrupt Expansion kT (based on V_U) vs Area Ratio (A_U/A_D)",
    "columns": ["A_U/A_D", "kT"],
    "rows": [["0.20",0.64],["0.25",0.56],["0.30",0.49],["0.35",0.43],["0.40",0.36],
              ["0.45",0.30],["0.50",0.25],["0.55",0.20],["0.60",0.16],["0.65",0.12],
              ["0.70",0.09],["0.75",0.06]],
}

FIG_6_30C_CONTRACTION = {
    "title": "Fig. 6-30C — Abrupt Contraction kT vs Area Ratio (A_U/A_D)",
    "columns": ["A_U/A_D", "kT"],
    "rows": [["1.0",0.00],["1.25",0.05],["1.5",0.12],["1.75",0.18],["2.0",0.22],
              ["2.5",0.28],["3.0",0.32],["3.5",0.34],["4.0",0.37],["6.0",0.42],["10.0",0.46]],
}

FIG_6_30M = {
    "title": "Fig. 6-30M — Equivalent Duct Discharge k1 vs Flare Angle θ and L:D",
    "columns": ["θ (°)", "L:D=1", "L:D=2", "L:D=3", "L:D=4", "L:D=6"],
    "rows": [["10",0.75,0.59,0.48,0.41,0.32],
             ["20",0.58,0.42,0.36,0.32,0.30],
             ["30",0.52,0.42,0.40,0.40,0.44],
             ["40",0.51,0.50,0.54,0.58,0.65]],
}

FIG_6_30N = {
    "title": "Fig. 6-30N — Equivalent Duct Entry k1 vs D0/D1 and Flare Angle θ",
    "columns": ["D0/D1", "θ=60°", "θ=90°", "θ=120°"],
    "rows": [["1.1",0.25,0.32,0.40],["1.2",0.17,0.23,0.35],
             ["1.4",0.12,0.21,0.31],["1.6",0.12,0.20,0.30]],
}

# =========================================================================
# THE FITTINGS DATA
# =========================================================================
FITTINGS = [

    # ---------------------------------------------------------------
    # BENDS
    # ---------------------------------------------------------------
    {
        "id": "001", "name": "Rectangular Radiused Bend", "category": "Bends",
        "image": "duct_fittings/fitting_001.png",
        "notes": ["kT = k'T × (Bend Angle Correction) × k_Re"],
        "tables": [
            {"title": "Base Loss Coefficient k'T — Aspect Ratio (H/W) vs Radius Ratio (R/W)",
             "columns": ["H/W","R/W=0.25","R/W=0.5","R/W=1.0","R/W=1.5"],
             "rows": [["0.25",0.57,0.27,0.22,0.20],["0.50",0.52,0.25,0.20,0.18],
                      ["0.75",0.48,0.23,0.19,0.16],["1.00",0.44,0.21,0.17,0.15],
                      ["1.50",0.40,0.19,0.15,0.14],["2.00",0.39,0.18,0.14,0.13],
                      ["3.00",0.39,0.18,0.14,0.13],["4.00",0.40,0.19,0.15,0.14],
                      ["5.00",0.42,0.20,0.16,0.14],["6.00",0.43,0.21,0.17,0.15],
                      ["8.00",0.44,0.21,0.17,0.15]]},
            BEND_ANGLE_CORRECTION_001, REYNOLDS_CORRECTION_001,
        ],
    },
    {
        "id": "002", "name": "Rectangular Radiused Bend with 1 Splitter", "category": "Bends",
        "image": "duct_fittings/fitting_002.png",
        "notes": ["R = throat radius, R1 = splitter vane radius = R/CR.",
                  "Bend angle correction is applied as for Fitting No. 001.",
                  "kT = k'T × (Bend Angle Correction) × k_Re"],
        "tables": [
            {"title": "Base Loss Coefficient k'T — Radius Ratio (R/W) vs Aspect Ratio (H/W)",
             "columns": ["R/W","0.25","0.5","1.0","1.5","2.0","3.0","4.0","5.0","6.0","7.0","8.0"],
             "rows": [
                ["0.05",0.52,0.40,0.43,0.49,0.55,0.66,0.75,0.84,0.93,1.00,1.10],
                ["0.10",0.36,0.27,0.25,0.28,0.30,0.35,0.39,0.42,0.46,0.49,0.52],
                ["0.15",0.28,0.21,0.18,0.19,0.19,0.22,0.25,0.26,0.28,0.30,0.32],
                ["0.20",0.22,0.16,0.14,0.14,0.15,0.16,0.17,0.18,0.19,0.20,0.21],
                ["0.25",0.18,0.13,0.11,0.11,0.11,0.12,0.13,0.14,0.14,0.15,0.15],
                ["0.30",0.15,0.11,0.09,0.09,0.09,0.09,0.10,0.10,0.11,0.11,0.12],
                ["0.35",0.13,0.09,0.08,0.07,0.07,0.08,0.08,0.08,0.08,0.09,0.09],
                ["0.40",0.11,0.08,0.07,0.06,0.06,0.06,0.06,0.07,0.07,0.07,0.07],
                ["0.45",0.10,0.07,0.06,0.05,0.05,0.05,0.05,0.06,0.06,0.06,0.06],
                ["0.50",0.09,0.06,0.05,0.05,0.04,0.04,0.04,0.05,0.05,0.05,0.05],
             ]},
            BEND_ANGLE_CORRECTION_001, REYNOLDS_CORRECTION_001,
        ],
    },
    {
        "id": "003", "name": "Rectangular Mitre Bend with Single Skin Turning Vanes", "category": "Bends",
        "image": "duct_fittings/fitting_003.png",
        "tables": [
            {"title": "Loss Coefficient kT vs Vane Spacing",
             "columns": ["Spacing (mm)","kT"],
             "rows": [["40",0.12],["60",0.15],["80",0.18],["100",0.25],[">100",0.30]]},
        ],
    },
    {
        "id": "004", "name": "Rectangular Radiused Bend with 2 Splitters", "category": "Bends",
        "image": "duct_fittings/fitting_004.png",
        "notes": ["R = throat radius, R1 = splitter #1 radius = R/CR, R2 = splitter #2 radius = R/CR².",
                  "Bend angle correction is applied as for Fitting No. 001.",
                  "kT = k'T × (Bend Angle Correction) × k_Re"],
        "tables": [
            {"title": "Base Loss Coefficient k'T — Radius Ratio (R/W) vs Aspect Ratio (H/W)",
             "columns": ["R/W","0.25","0.5","1.0","1.5","2.0","3.0","4.0","5.0","6.0","7.0","8.0"],
             "rows": [
                ["0.05",0.26,0.20,0.22,0.25,0.28,0.33,0.37,0.41,0.45,0.48,0.51],
                ["0.10",0.17,0.13,0.11,0.12,0.13,0.15,0.16,0.17,0.19,0.20,0.21],
                ["0.15",0.12,0.09,0.08,0.08,0.08,0.09,0.10,0.10,0.11,0.11,0.11],
                ["0.20",0.09,0.07,0.06,0.05,0.06,0.06,0.06,0.06,0.07,0.07,0.07],
                ["0.25",0.08,0.05,0.04,0.04,0.04,0.04,0.05,0.05,0.05,0.05,0.05],
                ["0.30",0.06,0.04,0.03,0.03,0.03,0.03,0.03,0.03,0.04,0.04,0.04],
             ]},
            BEND_ANGLE_CORRECTION_001, REYNOLDS_CORRECTION_001,
        ],
    },
    {
        "id": "005", "name": "Rectangular Mitre Bend, Single Skin Vane + Trailing Edge Extension", "category": "Bends",
        "image": "duct_fittings/fitting_003.png",
        "notes": ["Pressure drop as for Fitting No. 003, but no interaction on next fitting."],
        "tables": [
            {"title": "Loss Coefficient kT vs Vane Spacing",
             "columns": ["Spacing (mm)","kT"],
             "rows": [["40",0.12],["60",0.15],["80",0.18],["100",0.25],[">100",0.30]]},
        ],
    },
    {
        "id": "006", "name": "Rectangular Radiused Bend with 3 Splitters", "category": "Bends",
        "image": "duct_fittings/fitting_006.png",
        "notes": ["R = throat radius, R1/R2/R3 = splitter radii = R/CR, R/CR², R/CR³.",
                  "Bend angle correction is applied as for Fitting No. 001.",
                  "kT = k'T × (Bend Angle Correction) × k_Re"],
        "tables": [
            {"title": "Base Loss Coefficient k'T — Radius Ratio (R/W) vs Aspect Ratio (H/W)",
             "columns": ["R/W","0.25","0.5","1.0","1.5","2.0","3.0","4.0","5.0","6.0","7.0","8.0"],
             "rows": [
                ["0.05",0.11,0.10,0.12,0.13,0.14,0.16,0.18,0.19,0.21,0.22,0.23],
                ["0.10",0.07,0.05,0.06,0.06,0.06,0.07,0.07,0.08,0.08,0.08,0.09],
             ]},
            BEND_ANGLE_CORRECTION_001, REYNOLDS_CORRECTION_001,
        ],
    },
    {
        "id": "007", "name": "Rectangular Mitre Bend, Double Skin Turning Vanes (Embossed Vane Runner)", "category": "Bends",
        "image": "duct_fittings/fitting_003.png",
        "notes": ["Pressure drop as for Fitting No. 003, but no interaction on next fitting."],
        "tables": [
            {"title": "Loss Coefficient kT vs Vane Spacing",
             "columns": ["Spacing (mm)","kT"],
             "rows": [["40",0.12],["60",0.15],["80",0.18],["100",0.25],[">100",0.30]]},
        ],
    },
    {
        "id": "011", "name": "Circular Radiused Bend", "category": "Bends",
        "image": "duct_fittings/fitting_011.png",
        "notes": ["Bend angle correction is applied as for Fitting No. 001."],
        "tables": [
            {"title": "Loss Coefficient kT — Radius Ratio (R/D)",
             "columns": ["R/D","kT"],
             "rows": [["0.25",0.45],["0.50",0.34],["1.0",0.24],["1.5",0.23],["2.5",0.22]]},
            BEND_ANGLE_CORRECTION_001,
        ],
    },
    {
        "id": "012", "name": "Circular Three Piece Bend", "category": "Bends",
        "image": "duct_fittings/fitting_012.png",
        "notes": ["Bend angle correction is applied as for Fitting No. 001."],
        "tables": [
            {"title": "Loss Coefficient kT — Radius Ratio (R/D)",
             "columns": ["R/D","kT"],
             "rows": [["0.25",0.58],["0.50",0.46],["1.0",0.40],["1.5",0.42],["2.5",0.46]]},
            BEND_ANGLE_CORRECTION_001,
        ],
    },
    {
        "id": "013", "name": "Circular Four Piece Bend", "category": "Bends",
        "image": "duct_fittings/fitting_013.png",
        "notes": ["Bend angle correction is applied as for Fitting No. 001."],
        "tables": [
            {"title": "Loss Coefficient kT — Radius Ratio (R/D)",
             "columns": ["R/D","kT"],
             "rows": [["0.25",0.56],["0.50",0.42],["1.0",0.34],["1.5",0.32],["2.5",0.34]]},
            BEND_ANGLE_CORRECTION_001,
        ],
    },
    {
        "id": "014", "name": "Circular Five Piece Bend", "category": "Bends",
        "image": "duct_fittings/fitting_014.png",
        "notes": ["Bend angle correction is applied as for Fitting No. 001."],
        "tables": [
            {"title": "Loss Coefficient kT — Radius Ratio (R/D)",
             "columns": ["R/D","kT"],
             "rows": [["0.25",0.50],["0.50",0.36],["1.0",0.30],["1.5",0.26],["2.5",0.26]]},
            BEND_ANGLE_CORRECTION_001,
        ],
    },
    {
        "id": "021", "name": "Rectangular Mitre Bend without Buffer", "category": "Bends",
        "image": "duct_fittings/fitting_021.png",
        "notes": ["kT = k'T × (Bend Angle Correction) × k_Re"],
        "tables": [
            {"title": "Base Loss Coefficient k'T — Aspect Ratio (H/W)",
             "columns": ["H/W","k'T"],
             "rows": [["0.25",1.30],["0.5",1.27],["1.0",1.19],["2.0",1.07],["4.0",0.92],["6.0",0.85],["8.0",0.81]]},
            BEND_ANGLE_CORRECTION_021, REYNOLDS_CORRECTION_021,
        ],
    },
    {
        "id": "022", "name": "Rectangular Mitre Bend with Buffer", "category": "Bends",
        "image": "duct_fittings/fitting_022.png",
        "notes": ["Bend angle correction is applied as for Fitting No. 021.",
                  "kT = k'T × (Bend Angle Correction) × k_Re"],
        "tables": [
            {"title": "Base Loss Coefficient k'T — Aspect Ratio (H/W)",
             "columns": ["H/W","k'T"],
             "rows": [["0.25",1.57],["0.5",1.52],["1.0",1.43],["2.0",1.29],["4.0",1.10],["6.0",1.02],["8.0",0.98]]},
            BEND_ANGLE_CORRECTION_021, REYNOLDS_CORRECTION_021,
        ],
    },

    # ---------------------------------------------------------------
    # BENDS & TEES
    # ---------------------------------------------------------------
    {
        "id": "023", "name": "Circular Mitre Bend", "category": "Bends & Tees",
        "image": "duct_fittings/fitting_023.png",
        "tables": [
            {"title": "Loss Coefficient kT vs Bend Angle θ",
             "columns": ["Angle θ (°)","kT"],
             "rows": [["90",1.20],["75",0.81],["60",0.55],["45",0.34],["30",0.16],["20",0.08]]},
        ],
    },
    {
        "id": "024", "name": "Circular Mitre Bend with Throat Gore", "category": "Bends & Tees",
        "image": "duct_fittings/fitting_024.png",
        "notes": ["Base loss coefficient kT = 0.86, multiplied by the bend angle factor (as for Fitting No. 023)."],
        "tables": [ANGLE_FACTOR_023],
    },
    {
        "id": "025", "name": "Circular Mitre Bend with Heel Gore", "category": "Bends & Tees",
        "image": "duct_fittings/fitting_025.png",
        "notes": ["Base loss coefficient kT = 1.05, multiplied by the bend angle factor (as for Fitting No. 023)."],
        "tables": [ANGLE_FACTOR_023],
    },
    {
        "id": "tees", "name": "Tees / Tees with Splitter Dampers (Fitting Nos. 1ab / 2ab)", "category": "Bends & Tees",
        "image": "duct_fittings/fitting_808.png",
        "notes": [
            "'ab' denotes the bend number in the flow path being considered (e.g. No. 201 in both flow paths, or No. 203 in both flow paths).",
            "kT is taken as for a single bend, applied at each leg of the tee, when V_U = V_D for that flow path.",
            "If a splitter damper is included, add kTD = 0.08 (single blade damper fully open) to that flow path's total.",
            "Refer to the single bend fitting tables (Fitting No. 001 series) matching each leg's geometry.",
        ],
        "tables": [],
    },
    {
        "id": "100", "name": "Circular Wye", "category": "Bends & Tees",
        "image": "duct_fittings/fitting_100.png",
        "notes": ["kT = loss coefficient for a circular radiused bend with radius ratio R1/D1 ≈ ½ × (L1/tan(θ1/2) − 1).",
                  "Bend angle correction is applied as for Fitting No. 001."],
        "tables": [
            {"title": "Loss Coefficient kT — Radius Ratio (R/D) (as for Fitting No. 011)",
             "columns": ["R/D","kT"],
             "rows": [["0.25",0.45],["0.50",0.34],["1.0",0.24],["1.5",0.23],["2.5",0.22]]},
            BEND_ANGLE_CORRECTION_001,
        ],
    },

    # ---------------------------------------------------------------
    # EXPANSIONS & CONTRACTIONS
    # ---------------------------------------------------------------
    {
        "id": "301", "name": "Abrupt Expansion", "category": "Expansions & Contractions",
        "image": "duct_fittings/fitting_301.png",
        "notes": ["kT based on V_U.", "For short length of downstream duct, kT = 1.0."],
        "tables": [FIG_6_30C_EXPANSION],
    },
    {
        "id": "302", "name": "Abrupt Contraction", "category": "Expansions & Contractions",
        "image": "duct_fittings/fitting_302.png",
        "tables": [FIG_6_30C_CONTRACTION],
    },
    {
        "id": "303", "name": "Gradual Rectangular Expansion", "category": "Expansions & Contractions",
        "image": "duct_fittings/fitting_607.png",
        "notes": ["kT based on V_U. Values assume long downstream duct.",
                  "For asymmetrical configurations, take θ as the mean angle. For a 1 in 7 expansion, θ = 16°."],
        "tables": [
            {"title": "Loss Coefficient kT — Angle θ vs Velocity Ratio (V_D:V_U)",
             "columns": ["θ (°)","0.2","0.3","0.4","0.5","0.6"],
             "rows": [["10",0.20,0.15,0.12,0.08,0.06],["20",0.39,0.30,0.22,0.15,0.10],
                      ["30",0.52,0.40,0.29,0.20,0.13],["40",0.67,0.51,0.38,0.26,0.17],
                      ["50",0.70,0.54,0.40,0.28,0.18]]},
        ],
    },
    {
        "id": "304", "name": "Gradual Eccentric (One Sided) Rectangular Expansion", "category": "Expansions & Contractions",
        "image": "duct_fittings/fitting_607.png",
        "notes": ["kT based on V_U. Values assume long downstream duct.",
                  "For a 1 in 7 eccentric expansion, θ = 8°. Multiply the base kT (as for Fitting No. 303) by the correction multiplier below."],
        "tables": [
            {"title": "Base Loss Coefficient — Angle θ vs Velocity Ratio (V_D:V_U)",
             "columns": ["θ (°)","0.2","0.3","0.4","0.5","0.6"],
             "rows": [["10",0.20,0.15,0.12,0.08,0.06],["20",0.39,0.30,0.22,0.15,0.10],
                      ["30",0.52,0.40,0.29,0.20,0.13],["40",0.67,0.51,0.38,0.26,0.17],
                      ["50",0.70,0.54,0.40,0.28,0.18]]},
            {"title": "Correction Multiplier for Eccentric Expansion",
             "columns": ["θ (°)","Multiplier"],
             "rows": [["5",1.23],["10",1.69],["15",2.23],["20",2.00],["25",1.61],
                      ["30",1.31],["35",1.25],["40",1.20],["45",1.10]]},
        ],
    },
    {
        "id": "305", "name": "Gradual Circular Expansion", "category": "Expansions & Contractions",
        "image": "duct_fittings/fitting_911.png",
        "notes": ["kT based on V_U. Values assume long downstream duct.",
                  "For a 1 in 7 expansion, θ = 16°."],
        "tables": [
            {"title": "Loss Coefficient kT — Angle θ vs Velocity Ratio (V_D:V_U)",
             "columns": ["θ (°)","0.2","0.3","0.4","0.5","0.6"],
             "rows": [["10",0.18,0.13,0.11,0.08,0.06],["20",0.31,0.25,0.18,0.13,0.09],
                      ["30",0.41,0.31,0.23,0.16,0.10],["40",0.52,0.40,0.33,0.23,0.15],
                      ["50",0.70,0.52,0.39,0.27,0.18]]},
        ],
    },
    {
        "id": "306", "name": "Gradual Eccentric Circular Expansion", "category": "Expansions & Contractions",
        "image": "duct_fittings/fitting_911.png",
        "notes": ["kT based on V_U. Values assume long downstream duct.",
                  "For a 1 in 7 eccentric expansion, θ = 8°. Multiply the base kT (as for Fitting No. 305) by the correction multiplier below."],
        "tables": [
            {"title": "Base Loss Coefficient — Angle θ vs Velocity Ratio (V_D:V_U)",
             "columns": ["θ (°)","0.2","0.3","0.4","0.5","0.6"],
             "rows": [["10",0.18,0.13,0.11,0.08,0.06],["20",0.31,0.25,0.18,0.13,0.09],
                      ["30",0.41,0.31,0.23,0.16,0.10],["40",0.52,0.40,0.33,0.23,0.15],
                      ["50",0.70,0.52,0.39,0.27,0.18]]},
            {"title": "Correction Multiplier for Eccentric Expansion",
             "columns": ["θ (°)","Multiplier"],
             "rows": [["5",1.23],["10",1.69],["15",2.23],["20",2.00],["25",1.61],
                      ["30",1.31],["35",1.25],["40",1.20],["45",1.10]]},
        ],
    },
    {
        "id": "307", "name": "Gradual Rectangular Contraction", "category": "Expansions & Contractions",
        "image": "duct_fittings/fitting_616.png",
        "notes": ["For asymmetrical configurations, take θ as the mean angle. For a 1 in 4 contraction, θ = 28°."],
        "tables": [{"title": "Loss Coefficient kT vs Angle θ",
             "columns": ["θ (°)","kT"], "rows": [["15",0.008],["30",0.02],["45",0.04],["60",0.07]]}],
    },
    {
        "id": "309", "name": "Gradual Circular Contraction", "category": "Expansions & Contractions",
        "image": "duct_fittings/fitting_616.png",
        "notes": ["For a 1 in 4 contraction, θ = 28°."],
        "tables": [{"title": "Loss Coefficient kT vs Angle θ",
             "columns": ["θ (°)","kT"], "rows": [["15",0.008],["30",0.02],["45",0.04],["60",0.07]]}],
    },
    {
        "id": "308", "name": "Gradual Rectangular Eccentric (One Sided) Contraction", "category": "Expansions & Contractions",
        "image": "duct_fittings/fitting_618.png",
        "notes": ["For a 1 in 4 contraction, θ = 14°."],
        "tables": [{"title": "Loss Coefficient kT vs Angle θ",
             "columns": ["θ (°)","kT"], "rows": [["15",0.014],["30",0.07],["45",0.20],["60",0.40]]}],
    },
    {
        "id": "310", "name": "Gradual Circular Eccentric Contraction", "category": "Expansions & Contractions",
        "image": "duct_fittings/fitting_618.png",
        "notes": ["For a 1 in 4 contraction, θ = 14°."],
        "tables": [{"title": "Loss Coefficient kT vs Angle θ",
             "columns": ["θ (°)","kT"], "rows": [["15",0.014],["30",0.07],["45",0.20],["60",0.40]]}],
    },

    # ---------------------------------------------------------------
    # AREA TRANSITIONS
    # ---------------------------------------------------------------
    {
        "id": "311", "name": "Constant Velocity Area Transition", "category": "Area Transitions",
        "image": "duct_fittings/fitting_311.png",
        "notes": ["Conditions: V_U = V_D, θ ≤ 15°.", "kT = 0.15 (constant)."],
        "tables": [],
    },
    {
        "id": "312", "name": "Bend with Expanding or Contracting Flow", "category": "Area Transitions",
        "image": "duct_fittings/fitting_312.png",
        "notes": ["kT = k'T × k_Re (Reynolds correction as for Fitting No. 021)."],
        "tables": [
            {"title": "Base Loss Coefficient k'T — Aspect Ratio (HU/WU) vs Width Ratio (WD/WU)",
             "columns": ["HU/WU","0.6","0.8","1.2","1.4","1.6","2.0"],
             "rows": [["0.25",1.8,1.4,1.1,1.1,1.1,1.1],["1.0",1.7,1.4,1.0,0.95,0.90,0.84],
                      ["4.0",1.5,1.1,0.81,0.76,0.72,0.66],["6.0",1.5,1.0,0.69,0.63,0.60,0.55]]},
            REYNOLDS_CORRECTION_021,
        ],
    },

    # ---------------------------------------------------------------
    # DAMPERS
    # ---------------------------------------------------------------
    {
        "id": "321", "name": "Single Blade Butterfly Damper", "category": "Dampers",
        "image": "duct_fittings/fitting_645.png",
        "tables": [{"title": "Loss Coefficient kT vs Approximate Blade Angle",
             "columns": ["Angle (°)","kT"],
             "rows": [["0",0.08],["10",0.28],["15",0.54],["20",0.90],["30",2.8],["40",7.0],["50",20.0]]}],
    },
    {
        "id": "324", "name": "Single Blade Fire Damper", "category": "Dampers",
        "image": "duct_fittings/fitting_645.png",
        "tables": [{"title": "Loss Coefficient kT vs Approximate Blade Angle",
             "columns": ["Angle (°)","kT"],
             "rows": [["0",0.08],["10",0.28],["15",0.54],["20",0.90],["30",2.8],["40",7.0],["50",20.0]]}],
    },
    {
        "id": "323", "name": "Parallel Multi-Blade Dampers", "category": "Dampers",
        "image": "duct_fittings/fitting_645.png",
        "tables": [{"title": "Loss Coefficient kT vs Approximate Blade Angle",
             "columns": ["Angle (°)","kT"],
             "rows": [["0",0.23],["10",0.52],["15",0.75],["20",1.2],["30",1.75],["40",3.2],["50",5.0]]}],
    },
    {
        "id": "322", "name": "Opposed Multi-Blade Damper", "category": "Dampers",
        "image": "duct_fittings/fitting_645.png",
        "tables": [{"title": "Loss Coefficient kT vs Approximate Blade Angle",
             "columns": ["Angle (°)","kT"],
             "rows": [["0",0.23],["10",0.66],["15",1.1],["20",1.85],["30",4.7],["40",11.6],["50",33.0]]}],
    },
    {
        "id": "325", "name": "Multi-Blade Fire Dampers", "category": "Dampers",
        "image": "duct_fittings/fitting_645.png",
        "tables": [{"title": "Loss Coefficient kT vs Approximate Blade Angle",
             "columns": ["Angle (°)","kT"],
             "rows": [["0",0.23],["10",0.66],["15",1.1],["20",1.85],["30",4.7],["40",11.6],["50",33.0]]}],
    },

    # ---------------------------------------------------------------
    # FAN DISCHARGES
    # ---------------------------------------------------------------
    {
        "id": "331", "name": "Plane Symmetric Diffuser at Fan Discharge", "category": "Fan Discharges",
        "image": "duct_fittings/fitting_331.png",
        "tables": [{"title": "Loss Coefficient kT — Angle θ vs Area Ratio (A_D/A_U)",
             "columns": ["θ (°)","1.5","2.0","2.5","3.0","3.5","4.0"],
             "rows": [["10",0.05,0.07,0.09,0.10,0.11,0.11],["15",0.06,0.09,0.11,0.13,0.13,0.14],
                      ["20",0.07,0.10,0.13,0.15,0.16,0.16],["25",0.08,0.13,0.16,0.19,0.21,0.23],
                      ["30",0.16,0.24,0.29,0.32,0.34,0.35],["35",0.24,0.34,0.39,0.44,0.48,0.50]]}],
    },
    {
        "id": "332", "name": "Plane Asymmetric Diffuser at Fan Discharge", "category": "Fan Discharges",
        "image": "duct_fittings/fitting_332.png",
        "tables": [{"title": "Loss Coefficient kT — Angle θ vs Area Ratio (A_D/A_U)",
             "columns": ["θ (°)","1.5","2.0","2.5","3.0","3.5","4.0"],
             "rows": [["10",0.08,0.09,0.10,0.10,0.11,0.11],["15",0.10,0.11,0.12,0.13,0.14,0.15],
                      ["20",0.12,0.14,0.15,0.16,0.17,0.18],["25",0.15,0.18,0.21,0.23,0.25,0.26],
                      ["30",0.18,0.25,0.30,0.33,0.35,0.35],["35",0.21,0.31,0.38,0.41,0.43,0.44]]}],
    },
    {
        "id": "333", "name": "Eccentric Plane Asymmetric Diffuser at Fan Discharge", "category": "Fan Discharges",
        "image": "duct_fittings/fitting_333.png",
        "tables": [{"title": "Loss Coefficient kT — Angle θ vs Area Ratio (A_D/A_U)",
             "columns": ["θ (°)","1.5","2.0","2.5","3.0","3.5","4.0"],
             "rows": [["10",0.05,0.08,0.11,0.13,0.13,0.14],["15",0.06,0.10,0.12,0.14,0.15,0.15],
                      ["20",0.07,0.11,0.14,0.15,0.16,0.16],["25",0.09,0.14,0.18,0.20,0.21,0.22],
                      ["30",0.13,0.18,0.23,0.26,0.28,0.29],["35",0.15,0.23,0.28,0.33,0.35,0.36]]}],
    },
    {
        "id": "334", "name": "Offset Plane Diffuser at Fan Discharge", "category": "Fan Discharges",
        "image": "duct_fittings/fitting_334.png",
        "tables": [{"title": "Loss Coefficient kT — Angle θ vs Area Ratio (A_D/A_U)",
             "columns": ["θ (°)","1.5","2.0","2.5","3.0","3.5","4.0"],
             "rows": [["10",0.25,0.52,0.14,0.14,0.14,0.14],["15",0.29,0.60,0.16,0.17,0.18,0.18],
                      ["20",0.43,0.88,0.24,0.26,0.28,0.30],["25",0.65,1.28,0.35,0.37,0.39,0.40],
                      ["30",0.81,1.68,0.46,0.49,0.51,0.51],["35",1.00,2.16,0.61,0.64,0.66,0.66]]}],
    },
    {
        "id": "335", "name": "Pyramidal Diffuser at Fan Discharge", "category": "Fan Discharges",
        "image": "duct_fittings/fitting_335.png",
        "tables": [{"title": "Loss Coefficient kT — Angle θ vs Area Ratio (A_D/A_U)",
             "columns": ["θ (°)","1.5","2.0","2.5","3.0","3.5","4.0"],
             "rows": [["10",0.10,0.18,0.21,0.23,0.24,0.25],["15",0.23,0.33,0.38,0.40,0.42,0.44],
                      ["20",0.31,0.43,0.48,0.53,0.56,0.58],["25",0.36,0.49,0.55,0.58,0.62,0.64],
                      ["30",0.42,0.53,0.59,0.64,0.67,0.69]]}],
    },

    # ---------------------------------------------------------------
    # DIVIDED FLOW FITTINGS
    # ---------------------------------------------------------------
    {
        "id": "401", "name": "Rectangular 90° Take-Off", "category": "Divided Flow Fittings",
        "image": "duct_fittings/fitting_401.png",
        "notes": ["Branch path kT based on V_U."],
        "tables": [
            {"title": "Branch Path — Velocity Ratio (V_B/V_U) vs Area Ratio (A_B:A_D)",
             "columns": ["V_B/V_U","0.2","0.3","0.5","0.7","1.0"],
             "rows": [["0.4",9.69,8.75,6.88,5.94,5.31],["0.6",4.58,4.31,3.33,2.64,2.5],
                      ["0.8",3.13,2.81,2.03,1.72,1.72],["1.0",2.40,2.00,1.40,1.25,1.25],
                      ["1.2",1.88,1.74,1.11,0.97,None],["1.5",1.56,1.56,0.84,None,None],
                      ["2.0",1.50,1.50,0.88,None,None],["2.5",1.28,1.44,None,None,None]]},
            STRAIGHT_THROUGH_401,
        ],
    },
    {
        "id": "411", "name": "Circular 90° Take-Off", "category": "Divided Flow Fittings",
        "image": "duct_fittings/fitting_411.png",
        "notes": ["Branch path kT based on V_U."],
        "tables": [
            {"title": "Branch Path — Velocity Ratio (V_B/V_U) vs Area Ratio (A_B:A_D)",
             "columns": ["V_B/V_U","0.2","0.3","0.5","0.7","1.0"],
             "rows": [["0.4",9.69,8.75,6.88,5.94,5.31],["0.6",4.58,4.31,3.33,2.64,2.5],
                      ["0.8",3.13,2.81,2.03,1.72,1.72],["1.0",2.40,2.00,1.40,1.25,1.25],
                      ["1.2",1.88,1.74,1.11,0.97,None],["1.5",1.56,1.56,0.84,None,None],
                      ["2.0",1.50,1.50,0.88,None,None],["2.5",1.28,1.44,None,None,None]]},
            STRAIGHT_THROUGH_401,
        ],
    },
    {
        "id": "402", "name": "Rectangular Sweep Take-Off", "category": "Divided Flow Fittings",
        "image": "duct_fittings/fitting_402.png",
        "tables": [
            {"title": "Branch Path — Velocity Ratio (V_B/V_U)",
             "columns": ["V_B/V_U","kT"],
             "rows": [["0.6",1.70],["0.7",0.90],["0.8",0.50],["0.9",0.35],["1.0",0.26],["1.1",0.25],["1.2",0.30]]},
            {"title": "Straight Through — Velocity Ratio (V_D/V_U)",
             "columns": ["V_D/V_U","kT"],
             "rows": [["0.6",0.78],["0.7",0.41],["0.8",0.20],["0.9",0.12],["1.0",0.08],["1.1",0.05],["1.2",0.03]]},
        ],
    },
    {
        "id": "403", "name": "Rectangular Radiused 90° Take-Off with Splitter Damper", "category": "Divided Flow Fittings",
        "image": "duct_fittings/fitting_403.png",
        "notes": ["Branch: take as equivalent to 90° rectangular take-off with 45° haunch (Fitting Nos. 405/406).",
                  "Note: for this fitting the velocity ratio is V_B/V_U."],
        "tables": [
            {"title": "Straight Through — Velocity Ratio (V_B/V_U)",
             "columns": ["V_B/V_U","kT"],
             "rows": [["0.2",0.03],["0.4",0.04],["0.6",0.07],["0.8",0.12],["1.0",0.13],
                      ["1.2",0.14],["1.4",0.27],["1.6",0.30],["1.8",0.25]]},
        ],
    },
    {
        "id": "404", "name": "Rectangular Sweep with Splitter Damper", "category": "Divided Flow Fittings",
        "image": "duct_fittings/fitting_404.png",
        "notes": ["Branch/straight taken as equivalent to sweep take-off (Fitting No. 402) plus single blade damper fully open (add kT = 0.08)."],
        "tables": [
            {"title": "Branch Path — Velocity Ratio (V_B/V_U)",
             "columns": ["V_B/V_U","kT"],
             "rows": [["0.6",1.70],["0.7",0.90],["0.8",0.50],["0.9",0.35],["1.0",0.26],["1.1",0.25],["1.2",0.30]]},
            {"title": "Straight Through — Velocity Ratio (V_D/V_U)",
             "columns": ["V_D/V_U","kT"],
             "rows": [["0.6",0.78],["0.7",0.41],["0.8",0.20],["0.9",0.12],["1.0",0.08],["1.1",0.05],["1.2",0.03]]},
        ],
    },
    {
        "id": "405", "name": "Rectangular 90° Take-Off with Scoop Damper", "category": "Divided Flow Fittings",
        "image": "duct_fittings/fitting_405.png",
        "notes": ["Branch path kT based on V_U. Note: velocity ratio is V_B/V_U."],
        "tables": [
            {"title": "Branch Path — Velocity Ratio (V_B/V_U) vs Area Ratio (A_B/A_D)",
             "columns": ["V_B/V_U","0.2","0.3","0.5"],
             "rows": [["0.4",3.75,3.94,4.30],["0.6",2.08,2.19,2.28],["0.8",1.66,1.63,1.41],
                      ["1.0",1.12,1.41,1.21],["1.2",0.95,1.03,1.14],["1.4",0.87,1.03,1.26],
                      ["1.6",0.96,0.92,1.27],["1.8",0.95,0.95,1.27]]},
            STRAIGHT_THROUGH_405,
        ],
    },
    {
        "id": "406", "name": "Rectangular 90° Take-Off with Pivoted Scoop Damper", "category": "Divided Flow Fittings",
        "image": "duct_fittings/fitting_406.png",
        "notes": ["Branch path kT based on V_U. Note: velocity ratio is V_B/V_U."],
        "tables": [
            {"title": "Branch Path — Velocity Ratio (V_B/V_U) vs Area Ratio (A_B/A_D)",
             "columns": ["V_B/V_U","0.2","0.3","0.5"],
             "rows": [["0.4",3.75,3.94,4.30],["0.6",2.08,2.19,2.28],["0.8",1.66,1.63,1.41],
                      ["1.0",1.12,1.41,1.21],["1.2",0.95,1.03,1.14],["1.4",0.87,1.03,1.26],
                      ["1.6",0.96,0.92,1.27],["1.8",0.95,0.95,1.27]]},
            STRAIGHT_THROUGH_405,
        ],
    },
    {
        "id": "407", "name": "90° Rectangular Take-Off with 45° Haunch", "category": "Divided Flow Fittings",
        "image": "duct_fittings/fitting_407.png",
        "tables": [
            {"title": "Branch Path — Velocity Ratio (V_B/V_U)",
             "columns": ["V_B/V_U","kT"],
             "rows": [["0.4",4.4],["0.5",2.5],["0.6",1.6],["0.7",1.0],["0.8",0.78],["0.9",0.62],["1.0",0.55]]},
            {"title": "Straight Through — Velocity Ratio (V_D/V_U)",
             "columns": ["V_D/V_U","kT"],
             "rows": [["0.4",2.30],["0.5",1.00],["0.6",0.44],["0.7",0.20],["0.8",0.09],["0.9",0.06],["1.0",0.04]]},
        ],
    },
    {
        "id": "408", "name": "90° Rectangular Take-Off with 45° Haunch and Splitter Damper", "category": "Divided Flow Fittings",
        "image": "duct_fittings/fitting_408.png",
        "notes": ["Branch: take as equivalent to 45° circular take-off (Fitting No. 414)."],
        "tables": [STRAIGHT_THROUGH_405],
    },
    {
        "id": "409", "name": "Rectangular Diverging Wye", "category": "Divided Flow Fittings",
        "image": "duct_fittings/fitting_409.png",
        "notes": ["Branch path kT based on V_U."],
        "tables": [
            {"title": "30° Take-Off — Branch Path, V_B/V_U vs Area Ratio (A_B/A_U)",
             "columns": ["V_B/V_U","0.2","0.3","0.5","0.7","0.8"],
             "rows": [["0.4",None,3.10,2.56,2.44,2.35],["0.5",1.60,1.66,1.34,1.22,1.12],
                      ["0.6",1.03,0.93,0.72,1.66,0.62],["0.7",0.70,0.56,0.46,0.38,0.37],
                      ["0.8",0.49,0.41,0.30,0.28,0.24],["0.9",0.36,0.31,0.23,0.19,0.19],
                      ["1.0",0.26,0.24,0.18,0.16,0.16],["1.5",0.26,0.25,0.18,None,None],
                      ["2.0",0.33,0.33,None,None,None]]},
            {"title": "45° Take-Off — Branch Path, V_B/V_U vs Area Ratio (A_B/A_U)",
             "columns": ["V_B/V_U","0.2","0.3","0.5","0.7","0.8"],
             "rows": [["0.4",None,3.90,3.25,3.09,2.95],["0.5",2.24,2.28,1.86,1.70,1.60],
                      ["0.6",1.56,1.43,1.14,1.03,0.98],["0.7",1.14,0.99,0.81,0.70,0.66],
                      ["0.8",0.88,0.78,0.59,0.51,0.49],["0.9",0.69,0.63,0.48,0.41,0.40],
                      ["1.0",0.56,0.52,0.40,0.35,0.35],["1.5",0.44,0.30,None,None,None],
                      ["2.0",0.45,0.45,None,None,None]]},
            {"title": "60° Take-Off — Branch Path, V_B/V_U vs Area Ratio (A_B/A_U)",
             "columns": ["V_B/V_U","0.2","0.3","0.5","0.7","0.8"],
             "rows": [["0.4",None,4.94,4.13,3.90,3.80],["0.5",3.08,3.10,2.54,2.34,2.24],
                      ["0.6",2.24,2.11,1.69,1.54,1.47],["0.7",1.73,1.56,1.26,1.11,1.04],
                      ["0.8",1.38,1.26,0.97,0.84,0.85],["0.9",1.14,1.05,0.80,0.69,0.67],
                      ["1.0",0.96,0.89,0.68,0.60,0.60],["1.5",0.71,0.67,0.44,None,None],
                      ["2.0",0.83,0.65,None,None,None]]},
            {"title": "90° Take-Off — Branch Path, V_B/V_U vs Area Ratio (A_B/A_U)",
             "columns": ["V_B/V_U","0.2","0.3","0.5","0.7","0.8"],
             "rows": [["0.4",None,7.25,6.25,5.93,5.76],["0.5",8.13,4.60,4.20,3.86,3.72],
                      ["0.6",3.94,3.72,3.00,2.73,2.61],["0.7",3.14,2.94,2.35,2.04,1.93],
                      ["0.8",2.59,2.44,1.88,1.66,1.52],["0.9",2.20,2.12,1.60,1.40,1.38],
                      ["1.0",1.90,1.80,1.40,1.20,1.20],["1.5",1.29,None,None,None,None]]},
            {"title": "Straight Through — Velocity Ratio (V_D/V_U)",
             "columns": ["V_D/V_U","0.3","0.4","0.5","0.6","0.8","1.0"],
             "rows": [["kT",1.89,0.81,0.36,0.17,0.03,0.0]]},
        ],
    },
    {
        "id": "419", "name": "Circular Diverging Wye", "category": "Divided Flow Fittings",
        "image": "duct_fittings/fitting_419.png",
        "notes": ["Branch path kT based on V_U. Data identical to Fitting No. 409."],
        "tables": [
            {"title": "30° Take-Off — Branch Path, V_B/V_U vs Area Ratio (A_B/A_U)",
             "columns": ["V_B/V_U","0.2","0.3","0.5","0.7","0.8"],
             "rows": [["0.4",None,3.10,2.56,2.44,2.35],["0.5",1.60,1.66,1.34,1.22,1.12],
                      ["0.6",1.03,0.93,0.72,1.66,0.62],["0.7",0.70,0.56,0.46,0.38,0.37],
                      ["0.8",0.49,0.41,0.30,0.28,0.24],["0.9",0.36,0.31,0.23,0.19,0.19],
                      ["1.0",0.26,0.24,0.18,0.16,0.16],["1.5",0.26,0.25,0.18,None,None],
                      ["2.0",0.33,0.33,None,None,None]]},
            {"title": "45° Take-Off — Branch Path, V_B/V_U vs Area Ratio (A_B/A_U)",
             "columns": ["V_B/V_U","0.2","0.3","0.5","0.7","0.8"],
             "rows": [["0.4",None,3.90,3.25,3.09,2.95],["0.5",2.24,2.28,1.86,1.70,1.60],
                      ["0.6",1.56,1.43,1.14,1.03,0.98],["0.7",1.14,0.99,0.81,0.70,0.66],
                      ["0.8",0.88,0.78,0.59,0.51,0.49],["0.9",0.69,0.63,0.48,0.41,0.40],
                      ["1.0",0.56,0.52,0.40,0.35,0.35],["1.5",0.44,0.30,None,None,None],
                      ["2.0",0.45,0.45,None,None,None]]},
            {"title": "60° Take-Off — Branch Path, V_B/V_U vs Area Ratio (A_B/A_U)",
             "columns": ["V_B/V_U","0.2","0.3","0.5","0.7","0.8"],
             "rows": [["0.4",None,4.94,4.13,3.90,3.80],["0.5",3.08,3.10,2.54,2.34,2.24],
                      ["0.6",2.24,2.11,1.69,1.54,1.47],["0.7",1.73,1.56,1.26,1.11,1.04],
                      ["0.8",1.38,1.26,0.97,0.84,0.85],["0.9",1.14,1.05,0.80,0.69,0.67],
                      ["1.0",0.96,0.89,0.68,0.60,0.60],["1.5",0.71,0.67,0.44,None,None],
                      ["2.0",0.83,0.65,None,None,None]]},
            {"title": "90° Take-Off — Branch Path, V_B/V_U vs Area Ratio (A_B/A_U)",
             "columns": ["V_B/V_U","0.2","0.3","0.5","0.7","0.8"],
             "rows": [["0.4",None,7.25,6.25,5.93,5.76],["0.5",8.13,4.60,4.20,3.86,3.72],
                      ["0.6",3.94,3.72,3.00,2.73,2.61],["0.7",3.14,2.94,2.35,2.04,1.93],
                      ["0.8",2.59,2.44,1.88,1.66,1.52],["0.9",2.20,2.12,1.60,1.40,1.38],
                      ["1.0",1.90,1.80,1.40,1.20,1.20],["1.5",1.29,None,None,None,None]]},
            {"title": "Straight Through — Velocity Ratio (V_D/V_U)",
             "columns": ["V_D/V_U","0.3","0.4","0.5","0.6","0.8","1.0"],
             "rows": [["kT",1.89,0.81,0.36,0.17,0.03,0.0]]},
        ],
    },
    {
        "id": "412", "name": "Circular Long Cone Take-Off", "category": "Divided Flow Fittings",
        "image": "duct_fittings/fitting_412.png",
        "tables": [
            {"title": "Branch Path — Velocity Ratio (V_B/V_U)",
             "columns": ["V_B/V_U","kT"],
             "rows": [["0.4",5.2],["0.5",3.1],["0.6",1.9],["0.7",1.3],["0.8",0.89],
                      ["0.9",0.64],["1.0",0.48],["1.2",0.32],["1.4",0.25],["2.0",0.25]]},
            STRAIGHT_THROUGH_401,
        ],
    },
    {
        "id": "413", "name": "Circular Short Cone Take-Off", "category": "Divided Flow Fittings",
        "image": "duct_fittings/fitting_412.png",
        "tables": [
            {"title": "Branch Path — Velocity Ratio (V_B/V_U)",
             "columns": ["V_B/V_U","kT"],
             "rows": [["0.4",5.0],["0.5",3.0],["0.6",2.0],["0.7",1.5],["0.8",1.2],
                      ["0.9",1.0],["1.0",0.8],["1.2",0.6],["1.6",0.3],["2.0",0.3]]},
            STRAIGHT_THROUGH_401,
        ],
    },
    {
        "id": "414", "name": "Angled Circular Branch Take-Off", "category": "Divided Flow Fittings",
        "image": "duct_fittings/fitting_414.png",
        "tables": [
            {"title": "45° Take-Off — Branch Path, V_B/V_U",
             "columns": ["V_B/V_U","kT"],
             "rows": [["0.4",4.0],["0.5",2.2],["0.6",1.5],["0.7",1.0],["0.8",0.7],["0.9",0.55],["1.0",0.4]]},
            {"title": "45° Take-Off — Straight Through, V_D/V_U", **{k:v for k,v in STRAIGHT_THROUGH_401.items() if k!="title"}},
            {"title": "60° Take-Off — Branch Path, V_B/V_U",
             "columns": ["V_B/V_U","kT"],
             "rows": [["0.4",4.2],["0.5",2.6],["0.6",1.9],["0.7",1.4],["0.8",1.1],
                      ["0.9",0.82],["1.0",0.65],["1.2",0.56],["1.6",0.50],["2.0",0.49]]},
            {"title": "60° Take-Off — Straight Through, V_D/V_U", **{k:v for k,v in STRAIGHT_THROUGH_401.items() if k!="title"}},
        ],
    },
    {
        "id": "421", "name": "90° Rectangular Main and Tap", "category": "Divided Flow Fittings",
        "image": "duct_fittings/fitting_421.png",
        "notes": ["Straight through: as for Fitting Nos. 401 & 411."],
        "tables": [
            {"title": "Branch Path — Velocity Ratio (V_B/V_U) vs Area Ratio (A_B/A_D)",
             "columns": ["V_B/V_U","0.2","0.3","0.4","0.5"],
             "rows": [["0.4",6.60,6.46,6.39,6.31],["0.6",3.03,2.92,2.89,2.92],["0.8",1.86,1.86,1.81,1.75],
                      ["1.0",1.80,1.30,1.36,1.27],["1.2",1.14,1.26,1.09,1.15],["1.4",0.98,1.18,1.14,0.99],
                      ["1.6",0.88,1.14,0.99,0.86],["1.8",0.90,1.12,0.69,0.79]]},
            STRAIGHT_THROUGH_401,
        ],
    },
    {
        "id": "422", "name": "90° Rectangular Main with Circular Tap", "category": "Divided Flow Fittings",
        "image": "duct_fittings/fitting_422.png",
        "notes": ["Straight through: as for Fitting Nos. 401 & 411."],
        "tables": [
            {"title": "Branch Path — Velocity Ratio (V_B/V_U) vs Area Ratio (A_B/A_D)",
             "columns": ["V_B/V_U","0.2","0.3","0.4","0.5"],
             "rows": [["0.4",6.24,6.39,6.54,6.69],["0.6",3.14,3.08,3.03,3.00],["0.8",1.97,1.93,1.75,1.77],
                      ["1.0",1.38,1.20,1.23,1.26],["1.2",1.06,0.95,0.95,1.03],["1.4",0.83,0.76,0.82,0.87],
                      ["1.6",0.77,0.68,0.69,0.73],["1.8",0.67,0.63,0.61,0.64]]},
            STRAIGHT_THROUGH_401,
        ],
    },
    {
        "id": "423", "name": "90° Rectangular Main and Tap with Damper", "category": "Divided Flow Fittings",
        "image": "duct_fittings/fitting_423.png",
        "notes": ["Straight through: as for Fitting Nos. 405 & 406."],
        "tables": [
            {"title": "Branch Path — Velocity Ratio (V_B/V_U) vs Area Ratio (A_B/A_D)",
             "columns": ["V_B/V_U","0.2","0.3","0.4","0.5"],
             "rows": [["0.4",2.69,3.06,3.44,3.81],["0.6",1.23,1.35,1.43,1.50],["0.8",0.65,0.79,0.94,0.83],
                      ["1.0",0.57,0.77,0.73,0.68],["1.2",0.50,0.64,0.73,0.58],["1.4",0.35,0.63,0.73,0.60],
                      ["1.6",0.50,0.63,0.77,0.57],["1.8",0.88,0.65,0.82,0.59]]},
            STRAIGHT_THROUGH_405,
        ],
    },
    {
        "id": "427", "name": "90° Rectangular Main and Tap with 45° Haunch", "category": "Divided Flow Fittings",
        "image": "duct_fittings/fitting_427.png",
        "notes": ["Straight through: as for Fitting Nos. 401 & 411."],
        "tables": [
            {"title": "Branch Path — Velocity Ratio (V_B/V_U) vs Area Ratio (A_B/A_D)",
             "columns": ["V_B/V_U","0.2","0.3","0.4","0.5"],
             "rows": [["0.4",5.06,5.04,5.03,4.94],["0.6",2.12,2.03,1.97,1.94],["0.8",1.17,1.12,1.07,1.03],
                      ["1.0",0.98,0.85,0.79,0.74],["1.2",0.78,0.84,0.74,0.60],["1.4",0.64,0.68,0.70,0.47],
                      ["1.6",0.61,0.63,0.56,0.43],["1.8",0.54,0.47,0.49,0.36]]},
            STRAIGHT_THROUGH_401,
        ],
    },
    {
        "id": "428", "name": "90° Rectangular Main and Tap with 45° Haunch Plus Damper", "category": "Divided Flow Fittings",
        "image": "duct_fittings/fitting_428.png",
        "notes": ["Straight through: as for Fitting Nos. 405 & 406."],
        "tables": [
            {"title": "Branch Path — Velocity Ratio (V_B/V_U) vs Area Ratio (A_B/A_D)",
             "columns": ["V_B/V_U","0.2","0.3","0.4","0.5"],
             "rows": [["0.4",2.69,3.06,3.44,3.81],["0.6",1.23,1.35,1.43,1.50],["0.8",0.65,0.79,0.94,0.83],
                      ["1.0",0.57,0.77,0.73,0.68],["1.2",0.50,0.64,0.73,0.58],["1.4",0.50,0.63,0.73,0.60],
                      ["1.6",0.50,0.63,0.77,0.57],["1.8",0.58,0.65,0.82,0.59]]},
            STRAIGHT_THROUGH_405,
        ],
    },

    # ---------------------------------------------------------------
    # PLENUM FITTINGS
    # ---------------------------------------------------------------
    {
        "id": "501", "name": "Rectangular or Circular Abrupt Entry", "category": "Plenum Fittings",
        "image": "duct_fittings/fitting_501.png",
        "notes": ["k1 = 1.0 → kT = 1.0 × (Fig. 6-30C abrupt expansion value at the relevant area ratio)."],
        "tables": [FIG_6_30C_EXPANSION],
    },
    {
        "id": "502", "name": "Rectangular Flared Entry", "category": "Plenum Fittings",
        "image": "duct_fittings/fitting_502.png",
        "notes": ["kT = k1 × (Fig. 6-30C abrupt expansion value at V_P/V_U). k1 from Fig. 6-30M using θ and L:D.",
                  "θ = mean of θ1, θ2. D = 2(H×W)/(H+W)."],
        "tables": [FIG_6_30M, FIG_6_30C_EXPANSION],
    },
    {
        "id": "503", "name": "Circular Flared Entry", "category": "Plenum Fittings",
        "image": "duct_fittings/fitting_503.png",
        "notes": ["kT = k1 × (Fig. 6-30C abrupt expansion value at V_P/V_U). k1 from Fig. 6-30M using θ and L:D."],
        "tables": [FIG_6_30M, FIG_6_30C_EXPANSION],
    },
    {
        "id": "511", "name": "Rectangular or Circular Abrupt Exit", "category": "Plenum Fittings",
        "image": "duct_fittings/fitting_511.png",
        "notes": ["k1 = 0.5 → kT = (Fig. 6-30C abrupt contraction value at the relevant area ratio), unadjusted."],
        "tables": [FIG_6_30C_CONTRACTION],
    },
    {
        "id": "512", "name": "Rectangular Flared Exit", "category": "Plenum Fittings",
        "image": "duct_fittings/fitting_512.png",
        "notes": ["kT = (k1/0.5) × (Fig. 6-30C abrupt contraction value at V_D/V_P). k1 from Fig. 6-30N using D0/D1 and θ."],
        "tables": [FIG_6_30N, FIG_6_30C_CONTRACTION],
    },
    {
        "id": "513", "name": "Circular Flared Exit", "category": "Plenum Fittings",
        "image": "duct_fittings/fitting_513.png",
        "notes": ["kT = (k1/0.5) × (Fig. 6-30C abrupt contraction value at V_D/V_P). k1 from Fig. 6-30N."],
        "tables": [FIG_6_30N, FIG_6_30C_CONTRACTION],
    },
    {
        "id": "514", "name": "Bellmouth Exit", "category": "Plenum Fittings",
        "image": "duct_fittings/fitting_514.png",
        "notes": ["kT = (k1/0.5) × (Fig. 6-30C abrupt contraction value at V_D/V_P). k1 from Fig. 6-30N (bellmouth geometry)."],
        "tables": [FIG_6_30N, FIG_6_30C_CONTRACTION],
    },

    # ---------------------------------------------------------------
    # COMBINED FLOW FITTINGS
    # ---------------------------------------------------------------
    {
        "id": "601", "name": "Rectangular Combined Flow", "category": "Combined Flow Fittings",
        "image": "duct_fittings/fitting_601.png",
        "notes": ["Branch path kT based on V_C."],
        "tables": [
            {"title": "Branch Path — Velocity Ratio (V_B:V_C) vs Area Ratio (A_B/A_C)",
             "columns": ["V_B:V_C","0.2","0.3","0.5","0.7","1.0"],
             "rows": [["0.4",0.15,0.2,0.27,0.35,0.45],["0.6",0.20,0.27,0.40,0.48,0.52],
                      ["0.8",0.25,0.35,0.50,0.56,0.54],["1.0",0.30,0.42,0.60,0.63,0.55],
                      ["1.2",0.35,0.50,0.67,0.67,None],["1.5",0.45,0.60,0.77,None,None],
                      ["2.0",0.60,0.75,0.90,None,None],["2.5",0.70,0.90,None,None,None]]},
            {"title": "Straight Through — Velocity Ratio (V_U/V_C)",
             "columns": ["V_U/V_C","kT"],
             "rows": [["0.4",0.12],["0.5",0.09],["0.6",0.06],["0.7",0.03],["0.8–1.0",0]]},
        ],
    },
    {
        "id": "602", "name": "Radiused Rectangular Combined Flow", "category": "Combined Flow Fittings",
        "image": "duct_fittings/fitting_602.png",
        "notes": ["Branch/Straight kT based on V_C. Column labels combine both area ratios that apply to that column."],
        "tables": [
            {"title": "Branch Path — V_B/V_C vs [A_B/A_U, A_B/A_C] combos",
             "columns": ["V_B/V_C","AbAu.25/AbAc.25","AbAu.33/AbAc.25","AbAu.5/AbAc.5","AbAu.67/AbAc.5",
                          "AbAu1/AbAc.5","AbAu1/AbAc1","AbAu1.33/AbAc1","AbAu2/AbAc1"],
             "rows": [
                ["0.2",None,None,-0.50,-1.0,-2.2,-0.30,-0.80,-1.40],
                ["0.4",-0.50,-1.20,-0.20,-0.60,-1.5,-0.40,-0.20,-0.50],
                ["0.6",-0.25,-0.80,0,-0.20,-0.95,0.21,0.16,0],
                ["0.8",0,-0.40,0.25,0.10,-0.50,0.36,0.32,0.25],
                ["1.0",0.25,0,0.45,0.30,0,0.48,0.44,0.35],
                ["1.4",0.85,1.00,1.00,1.00,0.80,None,None,None],
                ["1.8",1.70,2.30,2.00,2.00,1.90,None,None,None],
                ["2.0",2.20,3.00,None,None,None,None,None,None],
                ["2.4",3.70,4.80,None,None,None,None,None,None],
             ]},
            {"title": "Straight Through — V_B/V_C vs [A_U/A_C, A_B/A_C] combos",
             "columns": ["V_B/V_C","AuAc.75/AbAc.25","AuAc1/AbAc.5","AuAc.75/AbAc.5","AuAc.5/AbAc.5",
                          "AuAc1/AbAc1","AuAc.75/AbAc1","AuAc.5/AbAc1"],
             "rows": [
                ["0.2",0.22,0.17,0.27,1.20,0.24,0.36,0.87],
                ["0.4",0.30,0.16,0.35,1.10,0.26,0.35,0.68],
                ["0.6",0.33,0.10,0.32,0.90,0.18,0.18,0.40],
                ["0.8",0.30,0,0.25,0.65,0,-0.08,0.08],
                ["1.0",0.26,-0.08,0.12,0.35,-0.24,-0.36,-0.12],
                ["1.4",0.06,-0.27,-0.23,-0.40,None,None,None],
                ["1.8",-0.28,-0.46,-0.58,-1.30,None,None,None],
                ["2.0",-0.45,None,None,None,None,None,None],
                ["2.4",-0.92,None,None,None,None,None,None],
             ]},
        ],
    },
    {
        "id": "611", "name": "Circular 90° Combined Flow with No Area Change", "category": "Combined Flow Fittings",
        "image": "duct_fittings/fitting_611.png",
        "notes": ["Branch path kT based on V_C."],
        "tables": [
            {"title": "Branch Path — Velocity Ratio (V_B/V_C) vs Area Ratio (A_B/A_C)",
             "columns": ["V_B/V_C","0.1","0.2","0.3","0.4","0.6","0.8","1.0"],
             "rows": [
                ["0.4",-0.04,-0.5,-0.37,-0.20,0,0.17,0.32],
                ["0.5",-0.03,-0.37,-0.17,-0.02,0.21,0.40,0.42],
                ["0.6",-0.02,-0.15,0.03,0.16,0.41,0.47,0.57],
                ["0.7",0,0.07,0.25,0.35,0.56,0.61,0.72],
                ["0.8",0.12,0.28,0.50,0.54,0.64,0.77,0.86],
                ["0.9",0.26,0.50,0.75,0.74,0.76,0.92,0.99],
                ["1.0",0.40,0.72,1.0,0.94,0.92,1.1,1.1],
                ["1.5",2.1,2.3,2.7,1.6,1.8,None,None],
                ["2.0",3.8,4.3,4.7,2.7,None,None,None],
                ["2.5",6.5,6.8,7.1,4.0,None,None,None],
                ["3.0",9.2,9.7,9.7,None,None,None,None],
                ["4.0",16.0,17.0,None,None,None,None,None],
                ["5.0",26.0,26.0,None,None,None,None,None],
             ]},
            {"title": "Straight Through — Velocity Ratio (V_U/V_C)",
             "columns": ["V_U/V_C","kT"],
             "rows": [["0.1",0.59],["0.2",0.60],["0.3",0.59],["0.4",0.57],["0.5",0.53],
                      ["0.6",-0.46],["0.7",0.38],["0.8",0.27],["0.9",0.16]]},
        ],
    },
    {
        "id": "612", "name": "Angled Conical Combined Flow", "category": "Combined Flow Fittings",
        "image": "duct_fittings/fitting_612.png",
        "notes": ["Very large lookup — selected using take-off angle θ, area ratios (A_U/A_C, A_B/A_C), and air flow ratio Q_B/Q_U.",
                  "Row = [A_U/A_C, A_B/A_C], Columns = Q_B/Q_U from 0.2 to 2.0."],
        "tables": [
            {"title": "θ=30° Branch Path",
             "columns": ["A_U/A_C","A_B/A_C","0.2","0.4","0.6","0.8","1.0","1.2","1.4","1.6","1.8","2.0"],
             "rows": [
                [0.3,0.2,-2.4,-0.11,1.8,3.4,4.8,6.0,7.1,8.0,8.9,9.7],
                [0.3,0.3,-2.8,-1.3,0.14,0.72,1.4,2.0,2.4,2.8,3.2,3.5],
                [0.4,0.2,-1.4,0.61,2.3,3.8,5.2,6.3,7.3,8.3,9.1,9.8],
                [0.4,0.3,-1.8,-0.54,0.42,1.2,1.8,2.3,2.7,3.1,3.4,3.7],
                [0.4,0.4,-1.9,-0.89,-0.17,0.36,0.76,1.1,1.3,1.5,1.7,1.9],
                [0.5,0.2,-0.82,0.97,2.6,4.0,5.3,6.4,7.4,8.3,9.1,9.9],
                [0.5,0.3,-1.2,-0.15,0.71,1.4,2.0,2.5,2.9,3.3,3.6,3.9],
                [0.5,0.4,-1.4,-0.54,0.06,0.50,0.85,1.1,1.3,1.5,1.7,1.8],
                [0.5,0.5,-1.4,-0.66,-0.15,0.21,0.48,0.68,0.84,0.97,1.1,1.2],
                [0.6,0.2,-0.52,1.2,2.7,4.1,5.3,6.4,7.4,8.3,9.1,9.9],
                [0.6,0.3,-0.93,0.06,0.85,1.5,2.1,2.6,3.0,3.4,3.7,4.0],
                [0.6,0.4,-1.1,-0.37,0.16,0.55,0.86,1.1,1.3,1.5,1.6,1.8],
                [0.6,0.5,-1.1,-0.49,-0.06,0.25,0.48,0.66,0.79,0.90,1.0,1.1],
                [0.6,0.6,-1.2,-0.55,-0.15,0.12,0.31,0.45,0.56,0.65,0.71,0.77],
                [0.8,0.2,-0.27,1.3,2.7,4.0,5.2,6.3,7.3,8.2,9.0,9.7],
                [0.8,0.3,-0.67,0.18,0.90,1.5,2.0,2.5,2.9,3.3,3.6,4.0],
                [0.8,0.4,-0.85,-0.27,0.16,0.49,0.75,0.97,1.2,1.3,1.4,1.6],
                [0.8,0.5,-0.90,-0.40,-0.07,0.18,0.36,0.50,0.61,0.70,0.78,0.84],
                [0.8,0.6,-0.92,-0.46,-0.16,0.04,0.18,0.29,0.37,0.44,0.49,0.53],
                [0.8,0.7,-0.93,-0.49,-0.21,-0.03,0.10,0.19,0.25,0.30,0.34,0.37],
                [0.8,0.8,-0.93,-0.50,-0.24,-0.07,0.05,0.13,0.19,0.23,0.27,0.29],
                [1.0,0.2,-0.26,1.2,2.6,3.9,5.1,6.1,7.1,8.0,8.8,9.5],
                [1.0,0.3,-0.65,0.12,0.79,1.4,1.9,2.4,2.8,3.1,3.5,3.8],
                [1.0,0.4,-0.83,-0.34,0.04,0.33,0.58,0.78,0.95,1.1,1.2,1.3],
                [1.0,0.5,-0.89,-0.48,-0.20,0,0.15,0.27,0.37,0.45,0.51,0.57],
                [1.0,0.6,-0.91,-0.54,-0.31,-0.14,-0.03,0.06,0.12,0.18,0.22,0.25],
                [1.0,0.8,-0.93,-0.59,-0.38,-0.25,-0.16,-0.10,-0.06,-0.03,-0.01,0.01],
                [1.0,1.0,-0.93,-0.60,-0.40,-0.28,-0.20,-0.14,-0.11,-0.08,-0.07,-0.06],
             ]},
            {"title": "θ=30° Straight Through",
             "columns": ["A_U/A_C","A_B/A_C","0.2","0.4","0.6","0.8","1.0","1.2","1.4","1.6","1.8","2.0"],
             "rows": [
                [0.3,0.2,4.5,2.8,1.5,0.56,-0.17,-0.74,-1.2,-1.6,-1.9,-2.1],
                [0.3,0.3,4.6,3.1,2.0,1.2,0.57,0.08,-0.30,-0.62,-0.89,-1.1],
                [0.4,0.2,1.6,0.85,0.16,-0.43,-0.92,-1.3,-1.7,-1.9,-2.2,-2.4],
                [0.4,0.3,1.7,1.1,0.58,0.13,-0.24,-0.56,-0.82,-1.1,-1.3,-1.4],
                [0.4,0.4,1.8,1.3,0.80,0.42,0.11,-0.15,-0.37,-0.55,-0.72,-0.86],
                [0.5,0.2,0.67,0.18,-0.33,-0.79,-1.2,-1.5,-1.8,-2.1,-2.4,-2.5],
                [0.5,0.3,0.75,0.42,0.07,-0.25,-0.54,-0.80,-1.0,-1.2,-1.4,-1.5],
                [0.5,0.4,0.80,0.55,0.28,0.03,-0.20,-0.40,-0.57,-0.73,-0.86,-0.98],
                [0.5,0.5,0.82,0.62,0.41,0.20,0.02,-0.15,-0.29,-0.42,-0.53,-0.63],
                [0.6,0.2,0.26,-0.11,-0.54,-0.95,-1.3,-1.6,-1.9,-2.1,-2.4,-2.5],
                [0.6,0.3,0.34,0.13,-0.14,-0.42,-0.67,-0.90,-1.1,-1.3,-1.4,-1.6],
                [0.6,0.4,0.39,0.25,0.06,-0.14,-0.33,-0.51,-0.66,-0.80,-0.93,-1.0],
                [0.6,0.5,0.41,0.32,0.18,0.03,-1.2,-0.26,-0.38,-0.50,-0.60,-0.69],
                [0.6,0.6,0.43,0.37,0.26,0.14,0.02,-0.09,-0.19,-0.29,-0.37,-0.45],
                [0.8,0.2,-0.01,-0.30,-0.67,-1.1,-1.4,-1.7,-2.0,-2.2,-2.4,-2.6],
                [0.8,0.3,0.07,-0.07,-0.29,-0.58,-0.76,-0.97,-1.2,-1.3,-1.5,-1.6],
                [0.8,0.4,0.11,0.05,-0.09,-0.26,-0.42,-0.58,-0.72,-0.85,-0.97,-1.1],
                [0.8,0.5,0.14,0.12,0.03,-0.09,-0.21,-0.34,-0.45,-0.55,-0.64,-0.73],
                [0.8,0.6,0.15,0.17,0.11,0.02,-0.07,-0.17,-0.26,-0.34,-0.42,-0.49],
                [0.8,0.7,0.17,0.21,0.17,0.11,0.03,-0.05,-0.12,-0.19,-0.26,-0.32],
                [0.8,0.8,0.17,0.23,0.22,0.17,0.11,0.05,-0.02,-0.07,-0.13,-0.18],
                [1.0,0.2,-0.05,-0.33,-0.70,-1.1,-1.4,-1.7,-2.0,-2.2,-2.4,-2.6],
                [1.0,0.3,0.03,-0.10,-0.31,-0.55,-0.78,-0.98,-1.2,-1.3,-1.5,-1.6],
                [1.0,0.4,0.07,0.02,-0.12,-0.28,-0.44,-0.59,-0.73,-0.86,-0.98,-1.1],
                [1.0,0.5,0.09,0.09,0.01,-0.11,-0.23,-0.35,-0.46,-0.56,-0.65,-0.74],
                [1.0,0.6,0.11,0.14,0.09,0,-0.09,-0.18,-0.27,-0.35,-0.43,-0.50],
                [1.0,0.8,0.13,0.20,0.19,0.15,0.09,0.03,-0.03,-0.08,-0.14,-0.19],
                [1.0,1.0,0.14,0.24,0.25,0.24,0.20,0.16,0.12,0.08,0.04,0],
             ]},
            {"title": "θ=45° Branch Path",
             "columns": ["A_U/A_C","A_B/A_C","0.2","0.4","0.6","0.8","1.0","1.2","1.4","1.6","1.8","2.0"],
             "rows": [
                [0.3,0.2,-2.4,-0.01,2.0,3.8,5.3,6.6,7.8,8.9,9.8,11.0],
                [0.3,0.3,-2.8,-1.2,0.12,1.1,1.9,2.6,3.2,3.7,4.2,4.6],
                [0.4,0.2,-1.2,0.93,2.8,4.5,5.9,7.2,8.4,9.5,10.0,11.0],
                [0.4,0.3,-1.6,-0.27,0.81,1.7,2.4,3.0,3.6,4.1,4.5,4.9],
                [0.4,0.4,-1.8,-0.72,0.07,0.66,1.1,1.5,1.8,2.1,2.3,2.5],
                [0.5,0.2,-0.46,1.5,3.3,4.9,6.4,7.7,8.8,9.9,11.0,12.0],
                [0.5,0.3,-0.94,0.25,1.2,2.0,2.7,3.3,3.8,4.2,4.7,5.0],
                [0.5,0.4,-1.1,-0.24,0.42,0.92,1.3,1.6,1.9,2.1,2.3,2.5],
                [0.5,0.5,-1.2,-0.38,0.18,0.58,0.88,1.1,1.3,1.5,1.6,1.7],
                [0.6,0.2,-0.55,1.3,3.1,4.7,6.1,7.4,8.6,9.6,11.0,12.0],
                [0.6,0.3,-1.1,0,0.88,1.6,2.3,2.8,3.3,3.7,4.1,4.5],
                [0.6,0.4,-1.2,-0.48,0.10,0.54,0.89,1.2,1.4,1.6,1.8,2.0],
                [0.6,0.5,-1.3,-0.62,-0.14,0.21,0.47,0.68,0.85,0.99,1.1,1.2],
                [0.6,0.6,-1.3,-0.69,-0.26,0.04,0.26,0.42,0.57,0.66,0.75,0.82],
                [0.8,0.2,0.06,1.8,3.5,5.1,6.5,7.3,8.9,10.0,11.0,12.0],
                [0.8,0.3,-0.52,0.35,1.1,1.7,2.3,2.8,3.2,3.6,3.9,4.2],
                [0.8,0.4,-0.67,-0.05,0.43,0.80,1.1,1.4,1.6,1.8,1.9,2.1],
                [0.8,0.6,-0.75,-0.27,0.05,0.28,0.45,0.58,0.68,0.76,0.83,0.88],
                [0.8,0.7,-0.77,-0.31,-0.02,0.18,0.32,0.43,0.50,0.56,0.61,0.65],
                [0.8,0.8,-0.78,-0.34,-0.07,0.12,0.24,0.33,0.39,0.44,0.47,0.50],
                [1.0,0.2,0.40,2.1,3.7,5.2,6.6,7.8,9.0,11.0,11.0,12.0],
                [1.0,0.3,-0.21,0.54,1.2,1.8,2.3,2.7,3.1,3.7,3.7,4.0],
                [1.0,0.4,-0.33,0.21,0.62,0.96,1.2,1.5,1.7,2.0,2.0,2.1],
                [1.0,0.5,-0.38,0.05,0.37,0.60,0.79,0.93,1.1,1.2,1.2,1.3],
                [1.0,0.6,-0.41,-0.02,0.23,0.42,0.55,0.66,0.73,0.80,0.85,0.89],
                [1.0,0.8,-0.44,-0.10,0.11,0.24,0.33,0.39,0.43,0.46,0.47,0.48],
                [1.0,1.0,-0.46,-0.14,0.05,0.16,0.23,0.27,0.29,0.30,0.30,0.29],
             ]},
            {"title": "θ=45° Straight Through",
             "columns": ["A_U/A_C","A_B/A_C","0.2","0.4","0.6","0.8","1.0","1.2","1.4","1.6","1.8","2.0"],
             "rows": [
                [0.3,0.2,5.3,-0.01,2.0,1.1,0.34,-0.20,-0.61,-0.93,-1.2,-1.4],
                [0.3,0.3,5.4,3.7,2.5,1.6,1.0,0.53,0.16,-0.14,-0.38,-0.58],
                [0.4,0.2,1.9,1.1,0.46,-0.07,-0.49,-0.83,-1.1,-1.3,-1.5,-1.7],
                [0.4,0.3,2.0,1.4,0.81,0.42,0.08,-0.20,-0.43,-0.62,-0.78,-0.92],
                [0.4,0.4,2.0,1.5,1.0,0.68,0.39,0.16,-0.04,-0.21,-0.35,-0.47],
                [0.5,0.2,0.77,0.34,-0.09,-0.48,-0.81,-1.1,1.3,-1.5,-1.7,-1.8],
                [0.5,0.3,0.85,0.56,0.25,-0.03,-0.27,-0.48,-0.67,-0.82,-0.96,-1.1],
                [0.5,0.4,0.88,0.66,0.43,0.21,0.02,-0.15,-0.30,-0.42,-0.54,-0.64],
                [0.5,0.5,0.91,0.73,0.54,0.36,0.21,0.06,-0.06,-0.17,-0.26,-0.35],
                [0.6,0.2,0.30,0,-0.34,-0.67,-0.96,-1.2,-1.4,-1.6,-1.8,-1.9],
                [0.6,0.3,0.37,0.21,-0.02,-0.24,-0.44,-0.63,-0.79,-0.93,-1.1,-1.2],
                [0.6,0.4,0.40,0.31,0.16,-0.1,-0.16,-0.30,-0.43,-0.54,-0.64,-0.73],
                [0.6,0.5,0.43,0.37,0.26,0.14,0.02,-0.09,-0.20,-0.29,-0.37,-0.45],
                [0.6,0.6,0.44,0.41,0.33,0.24,0.14,0.05,-0.03,-0.11,-0.18,-0.25],
                [0.8,0.2,-0.06,-0.27,-0.57,-0.86,-1.1,-1.4,-1.6,-1.7,-1.9,-2.0],
                [0.8,0.3,0,-0.08,-0.25,-0.43,-0.62,-0.78,-0.93,-1.1,-1.2,-1.3],
                [0.8,0.4,0.04,0.02,-0.08,-0.21,-0.34,-0.46,-0.57,-0.67,-0.77,-0.85],
                [0.8,0.6,0.08,0.15,0.14,0.10,0.05,-0.01,-0.07,-0.12,-0.17,-0.22],
                [0.8,0.7,0.09,0.17,0.18,0.16,0.11,0.07,0.02,-0.02,-0.07,-0.11],
                [1.0,0.2,-0.19,-0.39,-0.67,-0.96,-1.2,-1.5,-1.6,-1.8,-2.0,-2.1],
                [1.0,0.3,-0.12,-0.19,-0.35,-0.54,-0.71,-0.87,-1.0,-1.2,-1.3,-1.4],
                [1.0,0.4,-0.09,-0.10,-0.19,-0.31,-0.43,-0.55,-0.66,-0.77,-0.86,-0.94],
                [1.0,0.5,-0.07,-0.04,-0.09,-0.17,-0.26,-0.35,-0.44,-0.52,-0.59,-0.66],
                [1.0,0.6,-0.06,0,-0.02,-0.07,-0.14,-0.21,-0.28,-0.34,-0.40,-0.46],
                [1.0,0.8,-0.04,0.06,0.07,0.05,0.02,-0.03,-0.07,-0.12,-0.16,-0.20],
                [1.0,1.0,-0.03,0.09,0.13,0.13,0.11,0.08,0.06,0.03,-0.01,-0.03],
             ]},
        ],
    },
    {
        "id": "613", "name": "Angled Circular Combined Flow with No Area Change", "category": "Combined Flow Fittings",
        "image": "duct_fittings/fitting_613.png",
        "notes": ["Columns are Area Ratio (A_B/A_C). Row label is V_B/V_C for Branch Path and 30° Straight Through, but V_U/V_C for 45° Straight Through — note the difference."],
        "tables": [
            {"title": "θ=30° Branch Path — Velocity Ratio (V_B/V_C) vs Area Ratio (A_B/A_C)",
             "columns": ["V_B/V_C","0.1","0.2","0.3","0.4","0.6","0.8","1.0"],
             "rows": [
                [0.4,-0.52,-0.57,-0.48,-0.44,-0.19,-0.03,0.16],[0.5,-0.41,-0.46,-0.35,-0.20,-0.05,0.18,0.27],
                [0.6,-0.27,-0.29,-0.19,-0.04,0.14,0.32,0.31],[0.7,-0.15,-0.13,-0.02,0.12,0.30,0.42,0.40],
                [0.8,-0.03,0.04,0.12,0.28,0.40,0.48,0.45],[0.9,0.10,0.20,0.33,0.43,0.52,0.51,0.40],
                [1.0,0.21,0.37,0.50,0.59,0.64,0.53,0.27],[1.5,1.7,1.5,1.5,1.5,1.4,0.89,None],
                [2.0,3.1,3.0,3.0,2.6,2.1,None,None],[2.5,5.4,4.6,3.8,2.9,None,None,None],
                [3.0,7.6,6.4,5.3,None,None,None,None],[4.0,14.0,12.0,None,None,None,None,None],
                [5.0,21.0,17.0,None,None,None,None,None],
             ]},
            {"title": "θ=45° Branch Path — Velocity Ratio (V_B/V_C) vs Area Ratio (A_B/A_C)",
             "columns": ["V_B/V_C","0.1","0.2","0.3","0.4","0.6","0.8","1.0"],
             "rows": [
                [0.4,-0.56,-0.44,-0.35,-0.28,-0.15,-0.04,0.05],[0.5,-0.48,-0.37,-0.28,-0.21,-0.09,0.02,0.11],
                [0.6,-0.38,-0.27,-0.19,-0.12,0,0.10,0.18],[0.7,-0.26,-0.16,-0.08,-0.01,0.10,0.20,0.28],
                [0.8,-0.21,-0.02,0.05,0.12,0.23,0.32,0.40],[0.9,0.09,0.13,0.21,0.27,0.37,0.46,0.53],
                [1.0,0.22,0.31,0.38,0.44,0.53,0.62,0.69],[1.5,1.4,1.5,1.5,1.6,1.7,1.7,1.9],
                [2.0,3.1,3.2,3.2,3.2,3.3,3.3,3.3],[2.5,5.3,5.3,5.3,5.4,5.4,5.4,5.4],
                [3.0,8.0,8.0,8.0,8.0,8.0,8.0,8.0],
             ]},
            {"title": "θ=30° Straight Through — Velocity Ratio (V_B/V_C) vs Area Ratio (A_B/A_C)",
             "columns": ["V_B/V_C","0.1","0.2","0.3","0.4","0.6","0.8","1.0"],
             "rows": [
                [0.4,0.01,0.09,0.13,0.17,0.23,0.29,0.36],[0.5,0.01,0.11,0.13,0.19,0.22,0.26,0.32],
                [0.6,0.01,0.09,0.13,0.15,0.19,0.22,0.25],[0.7,0.01,0.07,0.12,0.12,0.14,0.12,0.10],
                [0.8,0.02,0.05,0.07,0.07,0.03,-0.02,-0.15],[0.9,0.02,0.03,0.03,0.01,-0.10,-0.09,-0.45],
                [1.0,0.02,0.01,-0.01,-0.05,-0.20,-0.43,-0.75],[1.5,-0.16,-0.25,-0.50,-0.70,-1.4,None,None],
                [2.0,-0.33,-0.75,-1.3,-1.8,None,None,None],[2.5,-0.72,-1.4,-2.4,-3.4,None,None,None],
                [3.0,-1.1,-2.4,-3.7,None,None,None,None],[4.0,-2.2,-4.6,None,None,None,None,None],
                [5.0,-5.6,-7.7,None,None,None,None,None],
             ]},
            {"title": "θ=45° Straight Through — Velocity Ratio (V_U/V_C) vs Area Ratio (A_B/A_C)",
             "columns": ["V_U/V_C","0.1","0.2","0.3","0.4","0.6","0.8","1.0"],
             "rows": [
                [0.1,-8.6,-4.1,-2.5,-1.7,-0.97,-0.58,-0.34],[0.2,-6.7,-3.1,-1.9,-1.3,-0.67,-0.36,-0.18],
                [0.3,-5.0,-2.2,-1.3,-0.88,-0.42,-0.19,-0.05],[0.4,-3.5,-1.5,-0.88,-0.55,-0.21,-0.05,0.05],
                [0.5,-2.3,-0.95,-0.51,-0.28,-0.06,0.06,0.13],[0.6,-1.3,-0.50,-0.22,-0.09,0.05,0.12,0.17],
                [0.7,-0.63,-0.18,-0.03,0.04,0.12,0.16,0.18],[0.8,-0.18,0.01,0.07,0.10,0.13,0.15,0.17],
                [0.9,0.03,0.07,0.08,0.09,0.10,0.11,0.13],[1.0,-0.01,0,0,0.10,0.02,0.04,0.05],
             ]},
        ],
    },

    # ---------------------------------------------------------------
    # DUCT PENETRATIONS & ELIMINATORS
    # ---------------------------------------------------------------
    {
        "id": "pipe_through", "name": "Pipe Through Circular or Rectangular Duct", "category": "Duct Penetrations & Eliminators",
        "image": "duct_fittings/fitting_p_through_corr_duct_1.png",
        "notes": ["kT = k1 × k2."],
        "tables": [
            {"title": "k1 — Diameter Ratio (d:D or d:H)",
             "columns": ["d:D or d:H","H","D"],
             "rows": [["0.01",0.01,0.02],["0.05",0.08,0.11],["0.12",0.23,0.34],["0.14",0.30,0.44],
                      ["0.16",0.37,0.56],["0.18",0.45,0.69],["0.20",0.54,0.85],["0.25",0.82,1.40]]},
            {"title": "k2 — Offset Ratio (y:D or y:H)",
             "columns": ["y:D or y:H","0","0.05","0.1","0.15","0.2","0.25"],
             "rows": [["k2",1.0,0.97,0.93,0.88,0.84,0.80]]},
        ],
    },
    {
        "id": "eliminators-1", "name": "Eliminators — Configuration 1", "category": "Duct Penetrations & Eliminators",
        "image": "duct_fittings/fitting_eliminators_1.png",
        "tables": [{"title": "Loss Coefficient kT — Blade Angle θ vs Number of Rows",
             "columns": ["θ (°)","2 Rows","3 Rows"], "rows": [["30",4,9],["45",9,18]]}],
    },
    {
        "id": "eliminators-2", "name": "Eliminators — Configuration 2", "category": "Duct Penetrations & Eliminators",
        "image": "duct_fittings/fitting_eliminators_2.png",
        "notes": ["kT = 11 (constant)."], "tables": [],
    },
    {
        "id": "eliminators-3", "name": "Eliminators — Configuration 3", "category": "Duct Penetrations & Eliminators",
        "image": "duct_fittings/fitting_eliminators_3.png",
        "tables": [{"title": "Loss Coefficient kT vs Blade Angle θ",
             "columns": ["θ (°)","kT"], "rows": [["30",9.0],["45",17.0]]}],
    },

    # ---------------------------------------------------------------
    # DISCHARGES
    # ---------------------------------------------------------------
    {
        "id": "disc_abrupt", "name": "Abrupt Duct Discharge", "category": "Discharges",
        "image": "duct_fittings/fitting_discharges_abruptduct.png",
        "notes": ["kT = 1.0 (constant)."], "tables": [],
    },
    {
        "id": "disc_r_flared", "name": "Rectangular Flared Duct Discharge", "category": "Discharges",
        "image": "duct_fittings/fitting_discharges_r_flaredduct.png",
        "notes": ["θ = mean flare angle = (θ1+θ2)/2. D = 2(H×W)/(H+W)."],
        "tables": [{"title": "Loss Coefficient kT — Flare Angle θ vs L:D",
             "columns": ["θ (°)","L:D=1","L:D=2","L:D=3","L:D=4","L:D=6"],
             "rows": [["10",0.75,0.59,0.48,0.41,0.32],["20",0.58,0.42,0.36,0.32,0.30],
                      ["30",0.52,0.42,0.40,0.40,0.44],["40",0.51,0.50,0.54,0.58,0.65]]}],
    },
    {
        "id": "disc_c_flared", "name": "Circular Flared Duct Discharge", "category": "Discharges",
        "image": "duct_fittings/fitting_discharges_c_flaredduct.png",
        "tables": [{"title": "Loss Coefficient kT — Flare Angle θ vs L:D",
             "columns": ["θ (°)","L:D=1","L:D=2","L:D=3","L:D=4","L:D=6"],
             "rows": [["10",1.00,0.83,0.62,0.51,0.38],["20",0.84,0.57,0.47,0.40,0.35],
                      ["30",0.74,0.57,0.52,0.50,0.55],["40",0.74,0.57,0.70,0.72,0.77]]}],
    },
    {
        "id": "disc_r_bend", "name": "Rectangular Bend Discharge", "category": "Discharges",
        "image": "duct_fittings/fitting_discharges_r_bend.png",
        "notes": ["Valid for ¼ ≤ H1/W ≤ 4."],
        "tables": [{"title": "Loss Coefficient kT — L/H1 vs Height Ratio (H0:H1)",
             "columns": ["L/H1","H0:H1=1.0","H0:H1=1.4","H0:H1=2.0"],
             "rows": [["0",3.0,2.5,1.5],["1.0",2.0,2.0,1.6],["10.0",1.5,1.4,1.1]]}],
    },
    {
        "id": "disc_c_bend", "name": "Circular Bend Discharge", "category": "Discharges",
        "image": "duct_fittings/fitting_discharges_c_bend.png",
        "tables": [{"title": "Loss Coefficient kT — Radius Ratio (R/D) vs L:D",
             "columns": ["R/D","L:D=0","L:D=2","L:D=10"],
             "rows": [["0",3.0,2.7,2.0],["0.2",2.2,1.7,1.5],["0.5",1.8,1.3,1.2],["1.0",1.5,1.1,1.1]]}],
    },
    {
        "id": "disc_exhausthood-1", "name": "Exhaust Hood — Configuration 1", "category": "Discharges",
        "image": "duct_fittings/fitting_discharges_exhausthood_1.png",
        "tables": [{"title": "Loss Coefficient kT vs Height Ratio (H/D)",
             "columns": ["H/D","0.1","0.2","0.4","0.6","1.0"],
             "rows": [["kT",4.0,2.3,1.4,1.1,1.0]]}],
    },
    {
        "id": "disc_exhausthood-2", "name": "Exhaust Hood — Configuration 2", "category": "Discharges",
        "image": "duct_fittings/fitting_discharges_exhausthood_2.png",
        "tables": [{"title": "Loss Coefficient kT vs Height Ratio (H/D)",
             "columns": ["H/D","0.25","0.3","0.4","0.6","1.0"],
             "rows": [["kT",3.4,2.6,1.7,1.2,1.0]]}],
    },
    {
        "id": "disc_r_planeexpanding", "name": "Rectangular Plane Expanding Discharge", "category": "Discharges",
        "image": "duct_fittings/fitting_discharges_r_planeexpanding.png",
        "notes": ["Valid for 0.5 ≤ H/W ≤ 2.0."],
        "tables": [{"title": "Loss Coefficient kT — Flare Angle θ vs L:H",
             "columns": ["θ (°)","L:H=1","L:H=2","L:H=3","L:H=4","L:H=6"],
             "rows": [["10",1.00,0.83,0.62,0.51,0.38],["20",0.84,0.57,0.47,0.40,0.35],
                      ["30",0.74,0.57,0.52,0.50,0.55],["40",0.74,0.57,0.70,0.72,0.77]]}],
    },

    # ---------------------------------------------------------------
    # INTAKES
    # ---------------------------------------------------------------
    {
        "id": "int_abrupt", "name": "Abrupt Duct Entry, Circular or Rectangular", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_abruptduct.png",
        "notes": ["kT = 0.5 (constant)."], "tables": [],
    },
    {
        "id": "int_bellmouth", "name": "Circular Bellmouth Entry", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_c_bellmouthentry.png",
        "notes": ["kT = 0.05 (constant)."], "tables": [],
    },
    {
        "id": "int_r_flared", "name": "Rectangular Flared Duct Entry", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_r_flaredductentry.png",
        "notes": ["θ = mean of θ1, θ2. D0 = 2(H0×W0)/(H0+W0), D1 = 2(H1×W1)/(H1+W1)."],
        "tables": [FIG_6_30N],
    },
    {
        "id": "int_c_flared", "name": "Circular Flared Duct Entry", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_c_flaredductentry.png",
        "tables": [FIG_6_30N],
    },
    {
        "id": "int_projecting", "name": "Projecting Rectangular or Circular Duct Entries", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_projectingductentries.png",
        "notes": ["kT = 0.95 (constant)."], "tables": [],
    },
    {
        "id": "int_flanged", "name": "Flanged Rectangular or Circular Duct Entries", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_flanged_ductentries.png",
        "notes": ["D = 2(H×W)/(H+W). kT = 0.5 for t ≥ D/25."], "tables": [],
    },
    {
        "id": "int_louvred", "name": "Louvred Duct Entry", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_louvredductentry.png",
        "notes": ["JR = (Number of inlets × a × b) / (W × H)."],
        "tables": [{"title": "Loss Coefficient kT vs Louvre Ratio (JR)",
             "columns": ["JR","Without Louvre","Vane 30°","Vane 45°"],
             "rows": [["0.4",13.7,19.5,None],["0.6",7.5,12.5,21.0],["0.8",4.5,7.5,14.0],
                      ["1.0",3.0,4.5,8.5],["1.2",2.0,3.5,5.5],["1.4",1.5,3.0,4.5],
                      ["1.6",1.2,2.5,4.0],["1.8",1.2,2.5,4.0]]}],
    },
    {
        "id": "int_hooded-1", "name": "Hooded Duct Entry — Configuration 1", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_hoodedentry_1.png",
        "tables": [{"title": "Loss Coefficient kT vs H/D",
             "columns": ["H/D","0.2","0.4","0.6","0.8","1.0"], "rows": [["kT",4.4,1.8,1.4,1.2,1.1]]}],
    },
    {
        "id": "int_hooded-2", "name": "Hooded Duct Entry — Configuration 2", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_hoodedentry_2.png",
        "tables": [{"title": "Loss Coefficient kT vs H/D",
             "columns": ["H/D","0.2","0.4","0.6","0.8","1.0"], "rows": [["kT",4.8,2.7,1.5,1.2,1.1]]}],
    },
    {
        "id": "int_hooded-3", "name": "Hooded Duct Entry — Configuration 3", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_hoodedentry_3.png",
        "tables": [{"title": "Loss Coefficient kT vs H/D",
             "columns": ["H/D","0.2","0.4","0.6","0.8","1.0"], "rows": [["kT",1.8,1.4,1.2,1.1,1.1]]}],
    },
    {
        "id": "int_inletlouvres-1", "name": "Inlet Louvres — Configuration 1", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_inletlouvres_1.png",
        "notes": ["Free area ratio = Open area of duct / Total area of duct."],
        "tables": [{"title": "Loss Coefficient kT vs Free Area Ratio",
             "columns": ["Free Area Ratio","0.4","0.5","0.6","0.7","0.8"], "rows": [["kT",10.5,6.0,3.6,2.35,1.6]]}],
    },
    {
        "id": "int_inletlouvres-2", "name": "Inlet Louvres — Configuration 2", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_inletlouvres_2.png",
        "notes": ["Free area ratio = Open area of duct / Total area of duct."],
        "tables": [{"title": "Loss Coefficient kT vs Free Area Ratio",
             "columns": ["Free Area Ratio","0.4","0.5","0.6","0.7","0.8"], "rows": [["kT",6.3,3.6,2.2,1.4,0.9]]}],
    },
    {
        "id": "int_open-1", "name": "Open Duct Entries — Configuration 1", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_openductentries_1.png",
        "notes": ["kT = 0.92 (constant)."], "tables": [],
    },
    {
        "id": "int_open-2", "name": "Open Duct Entries — In Corner (Config 2)", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_openductentries_incorner_2.png",
        "notes": ["kT = 0.77 (constant)."], "tables": [],
    },
    {
        "id": "int_open-3", "name": "Open Duct Entries — One Side Extended (Config 3)", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_openductentries_onesideextended_3.png",
        "notes": ["kT = 0.68 (constant)."], "tables": [],
    },
    {
        "id": "int_open-4", "name": "Open Duct Entries — Two Sides Extended (Config 4)", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_openductentries_twosidesextended_4.png",
        "notes": ["kT = 0.82 (constant)."], "tables": [],
    },
    {
        "id": "int_open-5", "name": "Open Duct Entries — Configuration 5", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_openductentries_5.png",
        "notes": ["kT = 0.63 (constant)."], "tables": [],
    },
    {
        "id": "int_open-6", "name": "Open Duct Entries — Between Two Walls (Config 6)", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_openductentries_6.png",
        "notes": ["kT = 0.72 (constant)."], "tables": [],
    },
    {
        "id": "int_screen_sq1", "name": "Screens — Square Holes (Config 1)", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_screen_squareholes_1.png",
        "notes": ["F = Free area ratio = Open area of duct / Total area of duct."],
        "tables": [{"title": "Loss Coefficient kT vs Free Area Ratio (F)",
             "columns": ["F","0.2","0.3","0.4","0.5","0.6","0.7","0.8"],
             "rows": [["kT",17.0,6.2,3.0,1.7,1.0,0.6,0.32]]}],
    },
    {
        "id": "int_screen_rd2", "name": "Screens — Round Holes (Config 2)", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_screen_roundholes_2.png",
        "tables": [{"title": "Loss Coefficient kT vs Free Area Ratio (F)",
             "columns": ["F","0.2","0.3","0.4","0.5","0.6","0.7","0.8"],
             "rows": [["kT",51.0,18.0,8.3,4.0,2.0,1.0,0.42]]}],
    },
    {
        "id": "int_screen_sq3", "name": "Screens — Square Holes (Config 3)", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_screen_squareholes_3.png",
        "tables": [{"title": "Loss Coefficient kT vs Free Area Ratio (F)",
             "columns": ["F","0.2","0.3","0.4","0.5","0.6","0.7","0.8"],
             "rows": [["kT",18.0,7.2,4.0,2.7,2.0,1.6,1.3]]}],
    },
    {
        "id": "int_screen_rd4", "name": "Screens — Round Holes (Config 4)", "category": "Intakes",
        "image": "duct_fittings/fitting_intake_screen_roundholes_4.png",
        "tables": [{"title": "Loss Coefficient kT vs Free Area Ratio (F)",
             "columns": ["F","0.2","0.3","0.4","0.5","0.6","0.7","0.8"],
             "rows": [["kT",57.0,24.0,11.0,5.8,3.5,2.0,1.3]]}],
    },
]

CATEGORY_ORDER = [
    "Bends", "Bends & Tees", "Expansions & Contractions", "Area Transitions",
    "Dampers", "Fan Discharges", "Divided Flow Fittings", "Plenum Fittings",
    "Combined Flow Fittings", "Duct Penetrations & Eliminators", "Discharges", "Intakes",
]
CATEGORIES = [c for c in CATEGORY_ORDER if any(f["category"] == c for f in FITTINGS)]

# =========================================================================
# LAYOUT
# =========================================================================
layout = html.Div(
    style={"width": "100%", "maxWidth": "1000px", "margin": "20px auto",
           "fontFamily": "Segoe UI, Inter, Arial"},
    children=[
        html.H1("Duct Fitting Total Loss Coefficients"),
        html.P("Select a category, then click a fitting's picture to view its KT tables."),

        dcc.Dropdown(
            id="category-select",
            options=[{"label": c, "value": c} for c in CATEGORIES],
            value=CATEGORIES[0],
            clearable=False,
            style={"width": "300px", "marginBottom": "18px"},
        ),

        html.Div(
            id="fitting-cards",
            style={"display": "flex", "flexWrap": "wrap", "gap": "14px", "marginBottom": "28px"},
        ),

        dcc.Store(id="selected-fitting"),
        html.Div(id="fitting-tables"),
    ],
)

# =========================================================================
# CALLBACKS
# =========================================================================
def fitting_label(f):
    # Numbered fittings (id starts with a digit, e.g. "001", "613") show the
    # number for cross-reference to the handbook. Everything else (Discharges,
    # Intakes, Eliminators, etc. -- which never had a "Fitting No.") just
    # shows the proper name, no internal programming ID.
    if f["id"] and f["id"][0].isdigit():
        return f"{f['id']} — {f['name']}"
    return f["name"]


@callback(
    Output("fitting-cards", "children"),
    Output("selected-fitting", "data"),
    Input("category-select", "value"),
    Input({"type": "fitting-card", "index": dash.ALL}, "n_clicks"),
)
def update_cards_and_selection(category, n_clicks_list):
    triggered_id = dash.ctx.triggered_id
    matches = [f for f in FITTINGS if f["category"] == category]

    cards = []
    for f in matches:
        cards.append(
            html.Button(
                id={"type": "fitting-card", "index": f["id"]},
                n_clicks=0,
                style={
                    "border": "1px solid #ddd", "borderRadius": "10px", "padding": "10px",
                    "cursor": "pointer", "background": "#fff", "textAlign": "center",
                    "width": "220px",
                },
                children=[
                    html.Img(
                        src=dash.get_asset_url(f["image"]),
                        style={"width": "100%", "height": "140px", "objectFit": "contain"},
                    ),
                    html.Div(fitting_label(f),
                              style={"marginTop": "8px", "fontSize": "13px", "fontWeight": "600"}),
                ],
            )
        )

    if isinstance(triggered_id, dict) and triggered_id.get("type") == "fitting-card":
        selected = triggered_id["index"]
    else:
        selected = matches[0]["id"] if matches else None

    return cards, selected


@callback(
    Output("fitting-tables", "children"),
    Input("selected-fitting", "data"),
)
def show_tables(fitting_id):
    if not fitting_id:
        return html.Div("Select a fitting above.")

    fitting = next((f for f in FITTINGS if f["id"] == fitting_id), None)
    if fitting is None:
        return html.Div("Fitting not found.")

    children = [html.H2(f"{fitting['id']} — {fitting['name']}")]

    for note in fitting.get("notes", []):
        children.append(html.P(note, style={"fontStyle": "italic", "color": "#444", "marginBottom": "4px"}))

    for table in fitting["tables"]:
        children.append(html.H4(table["title"], style={"marginTop": "16px", "marginBottom": "6px"}))
        children.append(
            dash_table.DataTable(
                columns=[{"name": str(c), "id": str(c)} for c in table["columns"]],
                data=[dict(zip([str(c) for c in table["columns"]], row)) for row in table["rows"]],
                style_cell={"textAlign": "center", "padding": "8px", "fontSize": "13px"},
                style_header={"fontWeight": "600", "backgroundColor": "#f2f2f2"},
                style_table={"marginBottom": "26px", "maxWidth": "900px", "overflowX": "auto"},
            )
        )

    if not fitting["tables"] and not fitting.get("notes"):
        children.append(html.P("No tabulated data for this fitting."))

    return children