import bpy
import math
from mathutils import Vector

# ============================================================
# TERMINAL VELOCITY
# COMPLETE INTERIOR SYSTEMS ARCHITECTURE
#
# VISUAL / CONCEPTUAL MODEL ONLY
# No operational propulsion calculations.
#
# X = longitudinal axis
# -X = forward / inlet
# +X = aft / exhaust
# ============================================================

# ------------------------------------------------------------
# CLEAN
# ------------------------------------------------------------

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

for col in list(bpy.data.collections):
    bpy.data.collections.remove(col)

# ------------------------------------------------------------
# COLLECTIONS
# ------------------------------------------------------------

def make_collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c

C = {
    "STRUCT": make_collection("00_STRUCTURE"),
    "INTAKE": make_collection("01_AIR_INTAKE"),
    "ION": make_collection("02_IONIZATION_AND_SEEDING"),
    "MHD": make_collection("03_MHD_MAGNET_MODULE"),
    "POWER": make_collection("04_POWER_AND_CONTROL"),
    "CRYO": make_collection("05_CRYO_SYSTEM"),
    "LH2": make_collection("06_LH2_SYSTEM"),
    "LOX": make_collection("07_LOX_SYSTEM"),
    "COMB": make_collection("08_COMBUSTION_MODULE"),
    "NOZZLE": make_collection("09_AEROSPIKE_MODULE"),
    "THERMAL": make_collection("10_THERMAL_MANAGEMENT"),
    "AVIONICS": make_collection("11_AVIONICS"),
    "FLOW": make_collection("12_FLOW_VISUALIZATION"),
    "LABEL": make_collection("13_LABELS"),
}

# ------------------------------------------------------------
# MATERIALS
# ------------------------------------------------------------

def M(name, color, metallic=0.0, rough=.4,
      emission=None, strength=0):

    m = bpy.data.materials.new(name)
    m.use_nodes = True

    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough

    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1)
        bsdf.inputs["Emission Strength"].default_value = strength

    return m


MAT = {
    "frame": M("Titanium Structure", (.20,.24,.29), .9,.22),
    "dark": M("Dark Alloy", (.025,.035,.05), .85,.20),
    "ceramic": M("Ceramic Insulator", (.14,.16,.18), .05,.65),
    "copper": M("Copper", (.55,.16,.035), .92,.17),
    "super": M("Superconductor", (.025,.16,.30), .92,.14),
    "anode": M("Anode", (.90,.035,.015), .80,.18),
    "cathode": M("Cathode", (.015,.10,.85), .75,.18),
    "lh2": M("LH2 System", (.38,.72,1.0), .25,.15),
    "lox": M("LOX System", (.46,.61,.86), .35,.18),
    "plasma": M(
        "Plasma",
        (.02,.12,1.0),
        0,.18,(.02,.10,1.0),12
    ),
    "hot": M(
        "Hot Gas",
        (1.0,.07,.005),
        0,.18,(1.0,.02,.001),12
    ),
    "coolant": M(
        "Cryogenic Coolant",
        (.25,.75,1.0),
        .1,.18,(.05,.35,1.0),4
    ),
    "tech": M(
        "Technical Highlight",
        (.04,.34,1.0),
        0,.2,(.02,.24,1.0),5
    ),
    "label": M(
        "Label",
        (.55,.78,1.0),
        0,.35,(.10,.4,1.0),4
    ),
}

# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

def link(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)


def cube(name, loc, scale, mat,
         col, bevel=.05):

    bpy.ops.mesh.primitive_cube_add(location=loc)

    o = bpy.context.object
    o.name = name
    o.scale = scale

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True
    )

    o.data.materials.append(mat)

    if bevel:
        b = o.modifiers.new("Bevel","BEVEL")
        b.width = bevel
        b.segments = 3

    link(o,col)
    return o


def cyl(name, radius, depth, loc, mat, col):

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64,
        radius=radius,
        depth=depth,
        location=loc,
        rotation=(0,math.pi/2,0)
    )

    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)

    link(o,col)
    return o


def torus(name, major, minor, loc, mat, col):

    bpy.ops.mesh.primitive_torus_add(
        major_radius=major,
        minor_radius=minor,
        major_segments=96,
        minor_segments=20,
        location=loc,
        rotation=(0,math.pi/2,0)
    )

    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)

    link(o,col)
    return o


def sphere(name, radius, loc, mat, col):

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=48,
        ring_count=24,
        radius=radius,
        location=loc
    )

    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)

    link(o,col)
    return o


def tube(name, points, radius, mat, col):

    curve = bpy.data.curves.new(name,"CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = radius
    curve.bevel_resolution = 5
    curve.resolution_u = 24

    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points)-1)

    for bp,p in zip(spline.bezier_points,points):
        bp.co = p
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"

    obj = bpy.data.objects.new(name,curve)
    col.objects.link(obj)
    obj.data.materials.append(mat)

    return obj


def label(name, body, loc, size=.25):

    curve = bpy.data.curves.new(name,"FONT")
    curve.body = body
    curve.size = size
    curve.align_x = "CENTER"
    curve.extrude = .008

    obj = bpy.data.objects.new(name,curve)
    C["LABEL"].objects.link(obj)

    obj.location = loc
    obj.rotation_euler = (math.pi/2,0,0)

    obj.data.materials.append(MAT["label"])

    return obj


# ============================================================
# MASTER FRAME
# ============================================================

# Central structural spine
cube(
    "PRIMARY_SPINE",
    (15,0,0),
    (15,.25,.25),
    MAT["frame"],
    C["STRUCT"],
    .08
)

# Main equipment frames
for i,x in enumerate([2,6,9,16,20,24,28]):

    torus(
        f"BULKHEAD_{i+1}",
        2.8 if x < 20 else 3.0,
        .12,
        (x,0,0),
        MAT["frame"],
        C["STRUCT"]
    )

# Longitudinal equipment rails
for y,z in [
    (2.2,1.5),
    (-2.2,1.5),
    (2.2,-1.5),
    (-2.2,-1.5)
]:

    tube(
        f"LOAD_RAIL_{y}_{z}",
        [
            (1,y,z),
            (8,y,z),
            (16,y,z),
            (24,y,z),
            (30,y,z)
        ],
        .10,
        MAT["frame"],
        C["STRUCT"]
    )

# ============================================================
# 1 — AIR INTAKE
# ============================================================

for x,r in [
    (.5,.18),
    (1.5,.35),
    (2.7,.58),
    (4.0,.90),
    (5.2,1.20),
    (6.0,1.42)
]:

    torus(
        f"INTAKE_RING_{x}",
        r,
        .08,
        (x,0,0),
        MAT["frame"],
        C["INTAKE"]
    )

# Variable intake guide structures
for i in range(8):

    a = i/8 * 2*math.pi

    y = 1.25*math.cos(a)
    z = 1.25*math.sin(a)

    tube(
        f"INTAKE_GUIDE_{i+1}",
        [
            (4.8,y*.7,z*.7),
            (5.8,y,z)
        ],
        .045,
        MAT["dark"],
        C["INTAKE"]
    )

# Centerbody
cyl(
    "INTAKE_CENTERBODY",
    .28,
    4.5,
    (3.0,0,0),
    MAT["dark"],
    C["INTAKE"]
)

# ============================================================
# 2 — IONIZATION + SEEDING
# ============================================================

cyl(
    "IONIZATION_CHAMBER",
    1.28,
    1.8,
    (6.7,0,0),
    MAT["ceramic"],
    C["ION"]
)

# Ionizer electrodes
for i in range(7):

    x = 6.0 + i*.25

    torus(
        f"IONIZER_ELECTRODE_{i+1}",
        1.22,
        .045,
        (x,0,0),
        MAT["tech"],
        C["ION"]
    )

# Conceptual seeding manifold
torus(
    "SEED_MANIFOLD",
    1.05,
    .07,
    (7.55,0,0),
    MAT["copper"],
    C["ION"]
)

# Seed injection ports
for i in range(12):

    a = i/12*2*math.pi

    y = 1.0*math.cos(a)
    z = 1.0*math.sin(a)

    tube(
        f"SEED_PORT_{i+1:02d}",
        [
            (7.55,y*.7,z*.7),
            (7.55,y,z)
        ],
        .035,
        MAT["copper"],
        C["ION"]
    )

# ============================================================
# 3 — MHD CORE
# ============================================================

# Ceramic channel
cyl(
    "MHD_CHANNEL",
    1.38,
    8.2,
    (12.5,0,0),
    MAT["ceramic"],
    C["MHD"]
)

# Plasma volume
cyl(
    "MHD_ACTIVE_FLOW_VOLUME",
    .62,
    7.6,
    (12.5,0,0),
    MAT["plasma"],
    C["FLOW"]
)

# Channel support collars
for i in range(9):

    x = 8.7+i*.9

    torus(
        f"MHD_CHANNEL_COLLAR_{i+1}",
        1.52,
        .10,
        (x,0,0),
        MAT["frame"],
        C["MHD"]
    )

# ============================================================
# 4 — SUPERCONDUCTING MAGNET ASSEMBLY
# ============================================================

# Outer magnet structures
for x in [9.0,16.0]:

    torus(
        f"MAGNET_HOUSING_{x}",
        2.45,
        .25,
        (x,0,0),
        MAT["super"],
        C["MHD"]
    )

    torus(
        f"MAGNET_POLE_RING_{x}",
        1.75,
        .15,
        (x,0,0),
        MAT["frame"],
        C["MHD"]
    )

# Coil pack
for i in range(16):

    x = 9.1 + i*.44

    torus(
        f"SUPERCONDUCTING_COIL_{i+1:02d}",
        2.12,
        .085,
        (x,0,0),
        MAT["copper"],
        C["MHD"]
    )

# Helical conductor
pts=[]

N=320

for i in range(N):

    t=i/(N-1)

    x=9.1+6.6*t
    a=t*5.5*2*math.pi

    y=2.13*math.cos(a)
    z=2.13*math.sin(a)

    pts.append((x,y,z))

tube(
    "CONTINUOUS_HELICAL_CONDUCTOR",
    pts,
    .055,
    MAT["super"],
    C["MHD"]
)

# Pole shoes
for z in [-1.75,1.75]:

    cube(
        f"MAGNET_POLE_SHOE_{z}",
        (12.5,0,z),
        (3.0,1.0,.24),
        MAT["frame"],
        C["MHD"],
        .10
    )

# Side return yokes
for y in [-2.30,2.30]:

    cube(
        f"MAGNET_RETURN_YOKE_{y}",
        (12.5,y,0),
        (3.1,.26,1.45),
        MAT["super"],
        C["MHD"],
        .10
    )

# ============================================================
# 5 — ELECTRODE SYSTEM
# ============================================================

cube(
    "MHD_ANODE",
    (12.5,0,1.23),
    (2.55,.18,.25),
    MAT["anode"],
    C["MHD"],
    .08
)

cube(
    "MHD_CATHODE",
    (12.5,0,-1.23),
    (2.55,.18,.25),
    MAT["cathode"],
    C["MHD"],
    .08
)

# Insulating backs
cube(
    "ANODE_INSULATOR",
    (12.5,0,1.47),
    (2.60,.25,.10),
    MAT["ceramic"],
    C["MHD"],
    .04
)

cube(
    "CATHODE_INSULATOR",
    (12.5,0,-1.47),
    (2.60,.25,.10),
    MAT["ceramic"],
    C["MHD"],
    .04
)

# ============================================================
# 6 — POWER + CONTROL
# ============================================================

# High-power conversion cabinets
for side in [-1,1]:

    y=side*3.0

    cube(
        f"POWER_CONVERSION_UNIT_{side}",
        (13.0,y,0),
        (1.65,.48,.68),
        MAT["dark"],
        C["POWER"],
        .12
    )

    # Internal power modules
    for j in range(7):

        cube(
            f"POWER_MODULE_{side}_{j+1}",
            (11.7+j*.45,y+side*.52,0),
            (.12,.11,.45),
            MAT["frame"],
            C["POWER"],
            .025
        )

# Current buses
tube(
    "ANODE_BUS",
    [
        (12.5,1.45,1.2),
        (12.5,2.3,1.7),
        (10.5,2.8,2.4)
    ],
    .085,
    MAT["anode"],
    C["POWER"]
)

tube(
    "CATHODE_BUS",
    [
        (12.5,-1.45,-1.2),
        (12.5,-2.3,-1.7),
        (10.5,-2.8,-2.4)
    ],
    .085,
    MAT["cathode"],
    C["POWER"]
)

# ============================================================
# 7 — CRYOGENIC MAGNET COOLING LOOP
# ============================================================

# Supply and return
tube(
    "CRYO_SUPPLY",
    [
        (8.5,2.6,2.5),
        (11,2.8,2.7),
        (14,2.8,2.7),
        (16.8,2.6,2.5)
    ],
    .10,
    MAT["coolant"],
    C["CRYO"]
)

tube(
    "CRYO_RETURN",
    [
        (8.5,-2.6,-2.5),
        (11,-2.8,-2.7),
        (14,-2.8,-2.7),
        (16.8,-2.6,-2.5)
    ],
    .10,
    MAT["coolant"],
    C["CRYO"]
)

# Cryogenic jackets
for i in range(9):

    x=9.0+i*.8

    torus(
        f"CRYO_JACKET_{i+1}",
        2.22,
        .045,
        (x,0,0),
        MAT["coolant"],
        C["CRYO"]
    )

# Cryogenic pump / conditioning module
cube(
    "CRYO_CONDITIONING_UNIT",
    (7.8,2.7,2.0),
    (.75,.40,.55),
    MAT["dark"],
    C["CRYO"],
    .12
)

# ============================================================
# 8 — LH2 PROPULSION SYSTEM
# ============================================================

# Main LH2 vessel
cyl(
    "LH2_TANK",
    .82,
    5.0,
    (13.0,-2.05,0),
    MAT["lh2"],
    C["LH2"]
)

sphere(
    "LH2_DOME_A",
    .82,
    (10.5,-2.05,0),
    MAT["lh2"],
    C["LH2"]
)

sphere(
    "LH2_DOME_B",
    .82,
    (15.5,-2.05,0),
    MAT["lh2"],
    C["LH2"]
)

# LH2 pump
cyl(
    "LH2_TURBOPUMP",
    .30,
    1.0,
    (18.2,-2.05,0),
    MAT["copper"],
    C["LH2"]
)

cube(
    "LH2_PUMP_DRIVE",
    (18.8,-2.05,0),
    (.30,.38,.30),
    MAT["dark"],
    C["LH2"],
    .08
)

# Valves
for i,x in enumerate([19.4,20.0]):

    torus(
        f"LH2_VALVE_{i+1}",
        .25,
        .06,
        (x,-2.05,0),
        MAT["frame"],
        C["LH2"]
    )

# Feed line
tube(
    "LH2_FEEDLINE",
    [
        (15.5,-2.05,0),
        (17.0,-2.05,0),
        (18.2,-2.05,0),
        (19.5,-1.3,0),
        (20.3,-.75,0)
    ],
    .10,
    MAT["lh2"],
    C["LH2"]
)

# ============================================================
# 9 — LOX PROPULSION SYSTEM
# ============================================================

cyl(
    "LOX_TANK",
    .72,
    5.0,
    (13.0,2.05,0),
    MAT["lox"],
    C["LOX"]
)

sphere(
    "LOX_DOME_A",
    .72,
    (10.5,2.05,0),
    MAT["lox"],
    C["LOX"]
)

sphere(
    "LOX_DOME_B",
    .72,
    (15.5,2.05,0),
    MAT["lox"],
    C["LOX"]
)

cyl(
    "LOX_TURBOPUMP",
    .30,
    1.0,
    (18.2,2.05,0),
    MAT["copper"],
    C["LOX"]
)

cube(
    "LOX_PUMP_DRIVE",
    (18.8,2.05,0),
    (.30,.38,.30),
    MAT["dark"],
    C["LOX"],
    .08
)

for i,x in enumerate([19.4,20.0]):

    torus(
        f"LOX_VALVE_{i+1}",
        .25,
        .06,
        (x,2.05,0),
        MAT["frame"],
        C["LOX"]
    )

tube(
    "LOX_FEEDLINE",
    [
        (15.5,2.05,0),
        (17.0,2.05,0),
        (18.2,2.05,0),
        (19.5,1.3,0),
        (20.3,.75,0)
    ],
    .10,
    MAT["lox"],
    C["LOX"]
)

# ============================================================
# 10 — INJECTOR / COMBUSTION
# ============================================================

# Injector head
cyl(
    "INJECTOR_HEAD",
    1.28,
    .50,
    (20.7,0,0),
    MAT["copper"],
    C["COMB"]
)

# Separate manifolds
torus(
    "LOX_INJECTOR_MANIFOLD",
    1.10,
    .11,
    (20.45,0,0),
    MAT["lox"],
    C["COMB"]
)

torus(
    "LH2_INJECTOR_MANIFOLD",
    .82,
    .10,
    (20.35,0,0),
    MAT["lh2"],
    C["COMB"]
)

# Injector elements
for i in range(28):

    a=i/28*2*math.pi

    y=1.0*math.cos(a)
    z=1.0*math.sin(a)

    cyl(
        f"INJECTOR_ELEMENT_{i+1:02d}",
        .045,
        .34,
        (20.35,y,z),
        MAT["copper"],
        C["COMB"]
    )

# Chamber wall
cyl(
    "COMBUSTION_CHAMBER_WALL",
    1.62,
    3.8,
    (22.55,0,0),
    MAT["frame"],
    C["COMB"]
)

# Thermal liner
cyl(
    "COMBUSTION_THERMAL_LINER",
    1.34,
    3.55,
    (22.55,0,0),
    MAT["ceramic"],
    C["THERMAL"]
)

# Conceptual hot-gas volume
cyl(
    "HOT_GAS_VOLUME",
    1.12,
    3.30,
    (22.55,0,0),
    MAT["hot"],
    C["FLOW"]
)

# Chamber cooling manifold
for i in range(8):

    x=21.0+i*.42

    torus(
        f"CHAMBER_COOLING_PASSAGE_{i+1}",
        1.52,
        .045,
        (x,0,0),
        MAT["coolant"],
        C["THERMAL"]
    )

# Chamber structural reinforcement
for i in range(6):

    x=21.1+i*.55

    torus(
        f"CHAMBER_REINFORCEMENT_{i+1}",
        1.70,
        .075,
        (x,0,0),
        MAT["frame"],
        C["STRUCT"]
    )

# ============================================================
# 11 — THROAT / AEROSPIKE MODULE
# ============================================================

# Throat transition
for x,r in [
    (24.0,1.15),
    (24.4,.95),
    (24.8,.76),
    (25.2,.62)
]:

    torus(
        f"THROAT_RING_{x}",
        r,
        .085,
        (x,0,0),
        MAT["ceramic"],
        C["NOZZLE"]
    )

# Central spike
cyl(
    "AEROSPIKE_CENTERBODY",
    .32,
    6.2,
    (28.0,0,0),
    MAT["frame"],
    C["NOZZLE"]
)

# Expansion surface representation
for x,r in [
    (25.7,.50),
    (26.4,.72),
    (27.1,.95),
    (27.8,1.18),
    (28.5,1.42),
    (29.2,1.68)
]:

    torus(
        f"AEROSPIKE_EXPANSION_SUPPORT_{x}",
        r,
        .075,
        (x,0,0),
        MAT["copper"],
        C["NOZZLE"]
    )

# Outer manifold
for x,r in [
    (25.8,1.35),
    (26.8,1.75),
    (27.8,2.15),
    (28.8,2.55),
    (29.8,2.90)
]:

    torus(
        f"AEROSPIKE_OUTER_MANIFOLD_{x}",
        r,
        .09,
        (x,0,0),
        MAT["frame"],
        C["NOZZLE"]
    )

# ============================================================
# 12 — THERMAL MANAGEMENT
# ============================================================

# Thermal barrier plates
for x in [20.0,21.0,23.5,24.5]:

    cube(
        f"THERMAL_BARRIER_{x}",
        (x,0,2.0),
        (.12,2.3,.10),
        MAT["ceramic"],
        C["THERMAL"],
        .03
    )

# Thermal sensor blocks
for i,x in enumerate([20.5,21.5,22.5,23.5]):

    cube(
        f"TEMP_SENSOR_{i+1}",
        (x,1.55,1.2),
        (.10,.12,.12),
        MAT["tech"],
        C["THERMAL"],
        .03
    )

# ============================================================
# 13 — AVIONICS / CONTROL
# ============================================================

# Flight computer
cube(
    "FLIGHT_COMPUTER",
    (8.0,3.1,0),
    (.75,.45,.55),
    MAT["dark"],
    C["AVIONICS"],
    .10
)

# Propulsion controller
cube(
    "PROPULSION_CONTROLLER",
    (16.0,3.1,0),
    (.80,.45,.55),
    MAT["dark"],
    C["AVIONICS"],
    .10
)

# Sensor network
for i,(x,y,z) in enumerate([
    (6.5,2.8,1.2),
    (8.5,2.8,1.2),
    (16,2.8,1.2),
    (21,2.8,1.2),
    (24,2.8,1.2)
]):

    cube(
        f"SENSOR_NODE_{i+1}",
        (x,y,z),
        (.12,.12,.12),
        MAT["tech"],
        C["AVIONICS"],
        .03
    )

# Data bus
tube(
    "DATA_BUS",
    [
        (6.5,2.7,1.2),
        (10,2.7,1.2),
        (16,2.7,1.2),
        (21,2.7,1.2),
        (24,2.7,1.2)
    ],
    .035,
    MAT["tech"],
    C["AVIONICS"]
)

# ============================================================
# 14 — FLOW PATHS
# ============================================================

tube(
    "ATMOSPHERIC_FLOW",
    [
        (-.5,0,0),
        (2,0,0),
        (4,0,0),
        (6.7,0,0)
    ],
    .07,
    MAT["tech"],
    C["FLOW"]
)

tube(
    "IONIZED_FLOW",
    [
        (6.5,0,0),
        (8,0,0),
        (12,0,0),
        (16.7,0,0)
    ],
    .075,
    MAT["plasma"],
    C["FLOW"]
)

tube(
    "CHEMICAL_FLOW",
    [
        (20.5,0,0),
        (22.5,0,0),
        (24.5,0,0),
        (30.5,0,0)
    ],
    .085,
    MAT["hot"],
    C["FLOW"]
)

# ============================================================
# 15 — FIELD VISUALIZATION
# ============================================================

for i in range(20):

    a=i/20*2*math.pi

    y1=1.55*math.cos(a)
    z1=1.55*math.sin(a)

    y2=2.25*math.cos(a)
    z2=2.25*math.sin(a)

    tube(
        f"B_FIELD_VECTOR_{i+1:02d}",
        [
            (12.7,y1,z1),
            (12.7,y2,z2)
        ],
        .018,
        MAT["tech"],
        C["FLOW"]
    )

# ============================================================
# 16 — SYSTEM LABELS
# ============================================================

label("L_INTAKE","AIR INTAKE",(3,0,3.35),.30)
label("L_ION","IONIZATION + SEEDING",(6.8,0,3.35),.27)
label("L_MHD","MHD MAGNET MODULE",(12.5,0,3.55),.34)
label("L_COIL","SUPERCONDUCTING COIL PACK",(12.5,0,3.00),.22)
label("L_ANODE","ANODE +",(12.5,0,1.58),.20)
label("L_CATHODE","CATHODE -",(12.5,0,-1.58),.20)
label("L_POWER","POWER / HV CONVERSION",(13,3.8,.2),.23)
label("L_CRYO","CRYOGENIC LOOP",(12,3.7,-2.5),.23)
label("L_LH2","LH2 SYSTEM",(13,-3.25,0),.25)
label("L_LOX","LOX SYSTEM",(13,3.25,0),.25)
label("L_INJECTOR","INJECTOR HEAD",(20.7,0,3.25),.24)
label("L_COMB","COMBUSTION MODULE",(22.5,0,3.55),.30)
label("L_THERMAL","THERMAL MANAGEMENT",(22.5,3.0,-2.0),.22)
label("L_SPIKE","AEROSPIKE MODULE",(28,0,3.6),.30)
label("L_AVIONICS","AVIONICS / CONTROL",(8,3.8,1.0),.22)

# ============================================================
# 17 — CAMERA
# ============================================================

bpy.ops.object.camera_add(
    location=(39,-42,23)
)

camera=bpy.context.object
camera.name="SYSTEMS_CUTAWAY_CAMERA"

direction=Vector((16,0,0))-camera.location
camera.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()

bpy.context.scene.camera=camera

# ============================================================
# 18 — LIGHTING
# ============================================================

def area(name,loc,energy,size,target=(16,0,0)):

    bpy.ops.object.light_add(type="AREA",location=loc)

    o=bpy.context.object
    o.name=name
    o.data.energy=energy
    o.data.size=size

    d=Vector(target)-o.location
    o.rotation_euler=d.to_track_quat("-Z","Y").to_euler()

    return o


area("KEY_LIGHT",(12,-18,21),2400,16)
area("FILL_LIGHT",(21,16,13),1300,14)

bpy.ops.object.light_add(
    type="POINT",
    location=(12.5,0,0)
)
bpy.context.object.data.energy=700
bpy.context.object.data.color=(.02,.16,1)

bpy.ops.object.light_add(
    type="POINT",
    location=(22.5,0,0)
)
bpy.context.object.data.energy=900
bpy.context.object.data.color=(1,.04,.01)

# ============================================================
# 19 — WORLD / RENDER
# ============================================================

world=bpy.context.scene.world
world.use_nodes=True

world.node_tree.nodes["Background"].inputs["Color"].default_value=(
    .002,.004,.009,1
)

world.node_tree.nodes["Background"].inputs["Strength"].default_value=.12

scene=bpy.context.scene
scene.render.engine="BLENDER_EEVEE_NEXT"

scene.render.resolution_x=1900
scene.render.resolution_y=1050
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"

# ============================================================
# 20 — SAVE
# ============================================================

path=bpy.path.abspath("//Terminal_Velocity_FULL_INTERIOR_MKIII.blend")

bpy.ops.wm.save_as_mainfile(path)

print("\n==============================================")
print(" TERMINAL VELOCITY — FULL INTERIOR MK-III")
print(" SYSTEMS ARCHITECTURE GENERATED")
print(" NO EXTERNAL AIRFRAME")
print(" Saved:",path)
print("==============================================\n")
