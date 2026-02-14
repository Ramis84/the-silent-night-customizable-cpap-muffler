# %% Imports
from build123d import *
from enum import IntEnum
from math import pi, tan, radians
from bd_warehouse.thread import IsoThread
#from ocp_vscode import *

# %% Config

# Global

'''Length of the outer tube+endcaps, excluding connectors'''
class MufflerLength(IntEnum):
    SMALL = 70
    MEDIUM = 85
    LARGE = 100

'''The small inner diameter of the o-ring between body and end-cap. Corresponds to the inner diameter of body'''
class MufflerORingInnerDiameter(IntEnum):
    SMALL = 44
    MEDIUM = 47
    LARGE = 50

MUFFLER_O_RING_THICKNESS = 3.5
'''The thickness of the o-ring in the muffler'''

TOLERANCE = 0.2
'''Extra spacing added for parts that are assembled together, increase if too tight'''

# Connector

CONNECTOR_MALE_OUTER_DIAMETER = 22.5
'''Diameter of tube connector'''

CONNECTOR_LENGTH = 20
'''The length of connector'''

CONNECTOR_MALE_WALL_THICKNESS = 2
'''Thickness of the male connector wall'''

CONNECTOR_FEMALE_WALL_THICKNESS = 4
'''Thickness of the female connector wall'''

CONNECTOR_FEMALE_O_RING_INNER_DIAMETER = 21
'''Inner diameter of the o-ring in the female connector'''

CONNECTOR_CORNER_RADIUS = 1
'''The rounding radius of the connector edge'''

# Body

BODY_WALL_THICKNESS = 4
'''The thickness of the outside tube'''

# End cap

END_CAP_CORNER_RADIUS = 2
'''The rounding radius of the end cap/outer tube'''

END_CAP_BOTTOM_THICKNESS = 4
'''The thickness of the end cap wall'''

END_CAP_GRIP_THICKNESS = 10
'''The thickness of the end cap grip'''

END_CAP_INNER_TUBE_SLOT_DEPTH = 2
'''The depth of the slot inside the endcap, where the inner tube is resting'''

END_CAP_INSERT_LENGTH = 10
'''The length of the end cap insert'''

END_CAP_INSERT_THICKNESS = 2
'''The thickness of the end cap insert'''

END_CAP_GRIP_CUTOUT_COUNT = 30
'''The number of cutouts making a grip in the end cap'''

GRIP_CUTOUT_DIAMETER_RATIO = 1/19
'''The ratio between the muffler outer diameter and grip cutout diameter.'''

# Threading

THREADING_PITCH = 2.0
'''The pitch of the threading'''

THREADING_EXTRA_SPACING_IF_ENABLED = 0.4
'''The extra spacing between internal and external threading, if enabled (only added on end-cap)'''

# Inner tube/mesh

INNER_TUBE_CORKSCREW_THICKNESS = 1
'''The thickness of the inner tube corkscrew'''

INNER_TUBE_SCREW_TWIST_TURNS = 1
'''The number of turns (360 degrees) of the inside screw.'''

INNER_TUBE_MESH_THICKNESS = 1.5
'''The thickness of the inner tube wall/mesh'''

INNER_TUBE_MESH_COUNT = 15
'''The number of mesh lines'''

INNER_TUBE_MESH_TWIST_ANGLE = 35
'''The angle (degrees) in the mesh pattern.'''

# Calculations
connector_male_inner_diameter = CONNECTOR_MALE_OUTER_DIAMETER - 2*CONNECTOR_MALE_WALL_THICKNESS
inner_tube_diameter = connector_male_inner_diameter+2*INNER_TUBE_MESH_THICKNESS
threading_height = 5*0.8660*THREADING_PITCH/8 # Height of thread ISO standard, https://en.wikipedia.org/wiki/ISO_metric_screw_thread

# %% Threadings

def threading_body(muffler_o_ring_inner_diameter: MufflerORingInnerDiameter):
    return IsoThread(major_diameter=muffler_o_ring_inner_diameter+0.01, pitch=THREADING_PITCH, length=END_CAP_INSERT_LENGTH+1, end_finishes=("fade","fade"), external=False, interference=0.0)
        
def threading_end_cap(muffler_o_ring_inner_diameter: MufflerORingInnerDiameter,
                      threading_extra_spacing_enabled: bool):
    threading_extra_spacing = (THREADING_EXTRA_SPACING_IF_ENABLED
                               if threading_extra_spacing_enabled
                               else 0.0)
    return IsoThread(major_diameter=muffler_o_ring_inner_diameter-2*(TOLERANCE+threading_extra_spacing), pitch=THREADING_PITCH, length=END_CAP_INSERT_LENGTH, end_finishes=("fade","fade"), interference=0.0)

# %% Male connector

male_connector_wall_profile = (
    Pos(connector_male_inner_diameter/2,0) 
    * Rectangle(CONNECTOR_MALE_WALL_THICKNESS, CONNECTOR_LENGTH, align=Align.MIN)
)
male_connector_wall_profile = fillet(male_connector_wall_profile.vertices()[2], CONNECTOR_CORNER_RADIUS)

# %% Female connector

def female_connector_o_ring_slot_profile(connector_female_o_ring_thickness: float):
    # Make slot big enough for, O-ring to expand
    profile = Polygon((connector_female_o_ring_thickness*2, 0), (0,-connector_female_o_ring_thickness/1.4), (0,connector_female_o_ring_thickness/1.4))
    profile = fillet(profile.vertices()[0], connector_female_o_ring_thickness/2)
    return profile

def female_connector_wall_profile(connector_female_o_ring_thickness: float):
    profile = (
        Pos(CONNECTOR_MALE_OUTER_DIAMETER/2 + TOLERANCE,0,0) 
        * Rectangle(CONNECTOR_FEMALE_WALL_THICKNESS, CONNECTOR_LENGTH, align=Align.MIN)
    )
    if CONNECTOR_CORNER_RADIUS > 0:
        profile = fillet(profile.vertices()[2], CONNECTOR_CORNER_RADIUS)
    # O-ring inside connector
    profile -= (
        Pos(CONNECTOR_FEMALE_O_RING_INNER_DIAMETER/2,CONNECTOR_LENGTH/5) 
        * female_connector_o_ring_slot_profile(connector_female_o_ring_thickness)
    )
    return profile

# %% Grip cutout

def grip_cutout_profile(outer_tube_outer_diameter: float):
    grip_cutout_diameter = outer_tube_outer_diameter*GRIP_CUTOUT_DIAMETER_RATIO
    circles = (
        PolarLocations(radius=(outer_tube_outer_diameter+grip_cutout_diameter)/2, count=END_CAP_GRIP_CUTOUT_COUNT)
        * Circle(grip_cutout_diameter/2, align=(Align.CENTER,Align.MIN))
    )
    return Compound(circles)

# %% Base grip (pre-generate for performance)

def grip_base_profile(muffler_o_ring_inner_diameter: MufflerORingInnerDiameter):
    outer_tube_inner_diameter = muffler_o_ring_inner_diameter
    outer_tube_outer_diameter = outer_tube_inner_diameter+2*BODY_WALL_THICKNESS
    grip_cutout_diameter = outer_tube_outer_diameter*GRIP_CUTOUT_DIAMETER_RATIO
    # Base grip
    profile = Rectangle((outer_tube_outer_diameter+grip_cutout_diameter)/2, END_CAP_GRIP_THICKNESS, align=Align.MIN)
    profile = fillet(profile.vertices()[2], END_CAP_CORNER_RADIUS)
    return profile

# %% Outer tube

def outer_tube_profile(muffler_length: MufflerLength,
                       muffler_o_ring_inner_diameter: MufflerORingInnerDiameter):
    outer_tube_inner_diameter = muffler_o_ring_inner_diameter
    outer_tube_outer_diameter = outer_tube_inner_diameter+2*BODY_WALL_THICKNESS
    # Outer tube
    profile = Rectangle(outer_tube_outer_diameter/2,muffler_length-2*END_CAP_GRIP_THICKNESS, align=Align.MIN)
    # Slot for o-ring
    profile -= (
        Pos((muffler_o_ring_inner_diameter+BODY_WALL_THICKNESS)/2,muffler_length-2*END_CAP_GRIP_THICKNESS)
        * Ellipse(MUFFLER_O_RING_THICKNESS/2, MUFFLER_O_RING_THICKNESS/2.5) # Make slot slightly smaller than o-ring, so it can "squish"
    )
    return profile

# %% Body with grip only, no connector

def body_grip_male_profile(muffler_length: MufflerLength,
                           muffler_o_ring_inner_diameter: MufflerORingInnerDiameter):
    # Grip
    profile = grip_base_profile(muffler_o_ring_inner_diameter)
    # Outer tube
    profile += Pos(0,END_CAP_GRIP_THICKNESS) * outer_tube_profile(muffler_length, muffler_o_ring_inner_diameter)
    # Inside of the body
    profile -= Pos(0,END_CAP_BOTTOM_THICKNESS) * Rectangle(muffler_o_ring_inner_diameter/2, muffler_length, align=Align.MIN)
    # Slot for inner mesh tube
    profile -= (
        Pos(0,END_CAP_BOTTOM_THICKNESS-END_CAP_INNER_TUBE_SLOT_DEPTH) 
        * Rectangle(inner_tube_diameter/2+TOLERANCE, END_CAP_GRIP_THICKNESS, align=Align.MIN)
    )
    # Hole in bottom
    profile -= Rectangle(CONNECTOR_MALE_OUTER_DIAMETER/2-CONNECTOR_MALE_WALL_THICKNESS, END_CAP_BOTTOM_THICKNESS, align=Align.MIN)
    return profile

# %% Male end cap, with connector

def body_male(muffler_length: MufflerLength, 
              muffler_o_ring_inner_diameter: MufflerORingInnerDiameter):
    outer_tube_outer_diameter = muffler_o_ring_inner_diameter+2*BODY_WALL_THICKNESS
    # Connector + body grip
    profile = male_connector_wall_profile
    profile += (
        Pos(0,CONNECTOR_LENGTH) 
        * body_grip_male_profile(muffler_length, muffler_o_ring_inner_diameter)
    )
    part = revolve(Plane.XZ * profile)
    # Grip cutout
    body_grip_cutout = grip_cutout_profile(outer_tube_outer_diameter)
    part -= extrude(body_grip_cutout, CONNECTOR_LENGTH+END_CAP_GRIP_THICKNESS)
    # Internal threads
    threading = (
        Pos(0,0,CONNECTOR_LENGTH+muffler_length-END_CAP_GRIP_THICKNESS-END_CAP_INSERT_LENGTH-1) 
        * threading_body(muffler_o_ring_inner_diameter)
    )
    return Compound([part, threading])

# %% End cap insert

def end_cap_insert_profile(muffler_o_ring_inner_diameter: MufflerORingInnerDiameter,
                           threading_extra_spacing_enabled: bool):
    threading_extra_spacing = THREADING_EXTRA_SPACING_IF_ENABLED if threading_extra_spacing_enabled else 0.0
    # Threading insert
    profile = Rectangle(muffler_o_ring_inner_diameter/2-TOLERANCE-threading_height-threading_extra_spacing,END_CAP_INSERT_LENGTH, align=Align.MIN)
    return profile

# %% End cap grip used by both male & female versions, no connector

def end_cap_grip_base_profile(muffler_o_ring_inner_diameter: MufflerORingInnerDiameter, 
                      threading_extra_spacing_enabled: bool):
    threading_extra_spacing = THREADING_EXTRA_SPACING_IF_ENABLED if threading_extra_spacing_enabled else 0.0
    # Grip
    profile = grip_base_profile(muffler_o_ring_inner_diameter)
    # Threading insert
    profile += (
        Pos(0,END_CAP_GRIP_THICKNESS) 
        * end_cap_insert_profile(muffler_o_ring_inner_diameter, threading_extra_spacing_enabled)
    )
    # Slot for o-ring
    profile -= (
        Pos((muffler_o_ring_inner_diameter+BODY_WALL_THICKNESS)/2,END_CAP_GRIP_THICKNESS)
        * Ellipse(MUFFLER_O_RING_THICKNESS/2, MUFFLER_O_RING_THICKNESS/2.5) # Make slot slightly smaller than o-ring, so it can "squish"
    )
    # Inside of the end-cap
    profile -= (
        Pos(0,END_CAP_BOTTOM_THICKNESS) 
        * Rectangle(muffler_o_ring_inner_diameter/2-END_CAP_INSERT_THICKNESS-threading_height-threading_extra_spacing, END_CAP_GRIP_THICKNESS+END_CAP_INSERT_LENGTH, align=Align.MIN)
    )
    # Slot for inner mesh tube
    profile -= (
        Pos(0,END_CAP_BOTTOM_THICKNESS-END_CAP_INNER_TUBE_SLOT_DEPTH) 
        * Rectangle(inner_tube_diameter/2+TOLERANCE, END_CAP_GRIP_THICKNESS, align=Align.MIN)
    )
    return profile

# %% Male end cap grip

def end_cap_grip_male_profile(muffler_o_ring_inner_diameter: MufflerORingInnerDiameter,
                              threading_extra_spacing_enabled: bool):
    profile = end_cap_grip_base_profile(muffler_o_ring_inner_diameter, threading_extra_spacing_enabled)
    # Hole in bottom
    profile -= Rectangle(CONNECTOR_MALE_OUTER_DIAMETER/2-CONNECTOR_MALE_WALL_THICKNESS, END_CAP_BOTTOM_THICKNESS, align=Align.MIN)
    return profile

# %% Female end cap grip

def end_cap_grip_female_profile(muffler_o_ring_inner_diameter: MufflerORingInnerDiameter,
                                threading_extra_spacing_enabled: bool):
    female_connection_inside_radius = CONNECTOR_MALE_OUTER_DIAMETER/2 + TOLERANCE
    profile = end_cap_grip_base_profile(muffler_o_ring_inner_diameter, threading_extra_spacing_enabled)
    # Taper the edge inwards between end cap and connector, since the inner mesh tube needs a ledge to sit on
    profile -= (
        Polygon((0, 0),
                (female_connection_inside_radius, 0),
                (0, female_connection_inside_radius))
    )
    # Cut off top of taper, in case the top of taper becomes narrower then a male connector diameter
    profile -= Rectangle(CONNECTOR_MALE_OUTER_DIAMETER/2-CONNECTOR_MALE_WALL_THICKNESS, END_CAP_BOTTOM_THICKNESS, align=Align.MIN)
    return profile

# %% Male end cap, with connector

def end_cap_male(muffler_o_ring_inner_diameter: MufflerORingInnerDiameter, 
                 threading_extra_spacing_enabled: bool = False):
    outer_tube_outer_diameter = muffler_o_ring_inner_diameter+2*BODY_WALL_THICKNESS
    # Connector + end-cap grip
    profile = male_connector_wall_profile
    profile += (
        Pos(0,CONNECTOR_LENGTH) 
        * end_cap_grip_male_profile(muffler_o_ring_inner_diameter, threading_extra_spacing_enabled)
    )
    part = revolve(Plane.XZ * profile)
    # Grip cutout
    body_grip_cutout = grip_cutout_profile(outer_tube_outer_diameter)
    part -= extrude(body_grip_cutout, CONNECTOR_LENGTH+END_CAP_GRIP_THICKNESS)
    # External threads
    threading = (
        Pos(0,0,CONNECTOR_LENGTH+END_CAP_GRIP_THICKNESS) 
        * threading_end_cap(muffler_o_ring_inner_diameter, threading_extra_spacing_enabled)
    )
    return Compound([part, threading])

# %% Female end cap, with connector

def end_cap_female(muffler_o_ring_inner_diameter: MufflerORingInnerDiameter, 
                   connector_female_o_ring_thickness: float, 
                   threading_extra_spacing_enabled: bool = False):
    outer_tube_outer_diameter = muffler_o_ring_inner_diameter+2*BODY_WALL_THICKNESS
    # Connector + end-cap grip
    profile = female_connector_wall_profile(connector_female_o_ring_thickness) + (
        Pos(0,CONNECTOR_LENGTH) 
        * end_cap_grip_female_profile(muffler_o_ring_inner_diameter, threading_extra_spacing_enabled)
    )
    part = revolve(Plane.XZ * profile)
    # Grip cutout
    body_grip_cutout = grip_cutout_profile(outer_tube_outer_diameter)
    part -= extrude(body_grip_cutout, CONNECTOR_LENGTH+END_CAP_GRIP_THICKNESS)
    # External threads
    threading = (
        Pos(0,0,CONNECTOR_LENGTH+END_CAP_GRIP_THICKNESS) 
        * threading_end_cap(muffler_o_ring_inner_diameter, threading_extra_spacing_enabled)
    )
    return Compound([part, threading])

# %% Inner mesh tube

def inner_mesh_tube(muffler_length: MufflerLength, 
                    include_corkscrew: bool):
    inner_tube_length = muffler_length-2*END_CAP_BOTTOM_THICKNESS+2*END_CAP_INNER_TUBE_SLOT_DEPTH
    ring_profile = Rectangle(INNER_TUBE_MESH_THICKNESS, INNER_TUBE_MESH_THICKNESS, align=Align.MIN)
    # End rings
    bottom_ring = revolve(Plane.XZ * Pos(connector_male_inner_diameter/2,0) * ring_profile)
    top_ring = Pos(0,0,inner_tube_length-INNER_TUBE_MESH_THICKNESS) * bottom_ring
    # Mesh
    ring_circumference = pi*CONNECTOR_MALE_OUTER_DIAMETER
    pitch = tan(radians(90-INNER_TUBE_MESH_TWIST_ANGLE))*ring_circumference
    clockwise_helix = Helix(pitch, inner_tube_length, connector_male_inner_diameter/2)
    anticlockwise_helix = Helix(pitch, inner_tube_length, connector_male_inner_diameter/2, lefthand=True)
    mesh_profile = Rectangle(INNER_TUBE_MESH_THICKNESS, INNER_TUBE_MESH_THICKNESS, align=(Align.MIN, Align.CENTER))
    clockwise = sweep(Pos(connector_male_inner_diameter/2,0,0) * mesh_profile, clockwise_helix, is_frenet=True)
    anticlockwise = sweep(Pos(connector_male_inner_diameter/2,0,0) * mesh_profile, anticlockwise_helix, is_frenet=True)
    # Make a flat Compound of all the objects
    solids = [bottom_ring, top_ring]
    # Optional corkscrew
    if include_corkscrew:
        clockwise_helix = Helix(INNER_TUBE_SCREW_TWIST_TURNS*inner_tube_length, inner_tube_length, connector_male_inner_diameter/2)
        corkscrew_profile = Rectangle(connector_male_inner_diameter, INNER_TUBE_CORKSCREW_THICKNESS, align=Align.MAX)
        corkscrew = sweep(Pos(connector_male_inner_diameter/2,0,0) * corkscrew_profile, clockwise_helix, is_frenet=True)
        solids.append(corkscrew)
    # Merge mesh strands into same Compound
    for i in range(INNER_TUBE_MESH_COUNT):
        strand = Rot(Z=i * 360 / INNER_TUBE_MESH_COUNT) * clockwise
        solids.append(strand)
        antistrand = Rot(Z=i * 360 / INNER_TUBE_MESH_COUNT) * anticlockwise
        solids.append(antistrand)
    return Compound(solids)

# %% Generate parts

body_male_small = body_male(MufflerLength.SMALL, MufflerORingInnerDiameter.SMALL)
body_male_medium = body_male(MufflerLength.MEDIUM, MufflerORingInnerDiameter.MEDIUM)
body_male_large = body_male(MufflerLength.LARGE, MufflerORingInnerDiameter.LARGE)

end_cap_male_small = end_cap_male(MufflerORingInnerDiameter.SMALL)
end_cap_male_small_extra_spacing = end_cap_male(MufflerORingInnerDiameter.SMALL, True)
end_cap_male_medium = end_cap_male(MufflerORingInnerDiameter.MEDIUM)
end_cap_male_medium_extra_spacing = end_cap_male(MufflerORingInnerDiameter.MEDIUM, True)
end_cap_male_large = end_cap_male(MufflerORingInnerDiameter.LARGE)
end_cap_male_large_extra_spacing = end_cap_male(MufflerORingInnerDiameter.LARGE, True)

end_cap_female_small_2_0 = end_cap_female(MufflerORingInnerDiameter.SMALL, 2.0)
end_cap_female_small_2_5 = end_cap_female(MufflerORingInnerDiameter.SMALL, 2.5)
end_cap_female_small_2_0_extra_spacing = end_cap_female(MufflerORingInnerDiameter.SMALL, 2.0, True)
end_cap_female_small_2_5_extra_spacing = end_cap_female(MufflerORingInnerDiameter.SMALL, 2.5, True)
end_cap_female_medium_2_0 = end_cap_female(MufflerORingInnerDiameter.MEDIUM, 2.0)
end_cap_female_medium_2_5 = end_cap_female(MufflerORingInnerDiameter.MEDIUM, 2.5)
end_cap_female_medium_2_0_extra_spacing = end_cap_female(MufflerORingInnerDiameter.MEDIUM, 2.0, True)
end_cap_female_medium_2_5_extra_spacing = end_cap_female(MufflerORingInnerDiameter.MEDIUM, 2.5, True)
end_cap_female_large_2_0 = end_cap_female(MufflerORingInnerDiameter.LARGE, 2.0)
end_cap_female_large_2_5 = end_cap_female(MufflerORingInnerDiameter.LARGE, 2.5)
end_cap_female_large_2_0_extra_spacing = end_cap_female(MufflerORingInnerDiameter.LARGE, 2.0, True)
end_cap_female_large_2_5_extra_spacing = end_cap_female(MufflerORingInnerDiameter.LARGE, 2.5, True)

inner_mesh_tube_small = inner_mesh_tube(MufflerLength.SMALL, False)
inner_mesh_tube_small_corkscrew = inner_mesh_tube(MufflerLength.SMALL, True)
inner_mesh_tube_medium = inner_mesh_tube(MufflerLength.MEDIUM, False)
inner_mesh_tube_medium_corkscrew = inner_mesh_tube(MufflerLength.MEDIUM, True)
inner_mesh_tube_large = inner_mesh_tube(MufflerLength.LARGE, False)
inner_mesh_tube_large_corkscrew = inner_mesh_tube(MufflerLength.LARGE, True)

# %% Preview 
# (uncomment one object at a time to preview, import 'ocp_vscode' needs to be uncommented at the top of the file as well)

#show(body_male_small)
#show(body_male_medium)
#show(body_male_large)

#show(end_cap_male_small)
#show(end_cap_male_small_extra_spacing)
#show(end_cap_male_medium)
#show(end_cap_male_medium_extra_spacing)
#show(end_cap_male_large)
#show(end_cap_male_large_extra_spacing)

#show(end_cap_female_small_2_0)
#show(end_cap_female_small_2_5)
#show(end_cap_female_small_2_0_extra_spacing)
#show(end_cap_female_small_2_5_extra_spacing)
#show(end_cap_female_medium_2_0)
#show(end_cap_female_medium_2_5)
#show(end_cap_female_medium_2_0_extra_spacing)
#show(end_cap_female_medium_2_5_extra_spacing)
#show(end_cap_female_large_2_0)
#show(end_cap_female_large_2_5)
#show(end_cap_female_large_2_0_extra_spacing)
#show(end_cap_female_large_2_5_extra_spacing)

#show(inner_mesh_tube_small)
#show(inner_mesh_tube_small_corkscrew)
#show(inner_mesh_tube_medium)
#show(inner_mesh_tube_medium_corkscrew)
#show(inner_mesh_tube_large)
#show(inner_mesh_tube_large_corkscrew)

# %% Exports STL

export_stl(body_male_small, "body_male_small.stl")
export_stl(body_male_medium, "body_male_medium.stl")
export_stl(body_male_large, "body_male_large.stl")

export_stl(end_cap_male_small, "end_cap_male_small.stl")
export_stl(end_cap_male_small_extra_spacing, "end_cap_male_small_extra_spacing.stl")
export_stl(end_cap_male_medium, "end_cap_male_medium.stl")
export_stl(end_cap_male_medium_extra_spacing, "end_cap_male_medium_extra_spacing.stl")
export_stl(end_cap_male_large, "end_cap_male_large.stl")
export_stl(end_cap_male_large_extra_spacing, "end_cap_male_large_extra_spacing.stl")

export_stl(end_cap_female_small_2_0, "end_cap_female_small_2_0.stl")
export_stl(end_cap_female_small_2_5, "end_cap_female_small_2_5.stl")
export_stl(end_cap_female_small_2_0_extra_spacing, "end_cap_female_small_2_0_extra_spacing.stl")
export_stl(end_cap_female_small_2_5_extra_spacing, "end_cap_female_small_2_5_extra_spacing.stl")
export_stl(end_cap_female_medium_2_0, "end_cap_female_medium_2_0.stl")
export_stl(end_cap_female_medium_2_5, "end_cap_female_medium_2_5.stl")
export_stl(end_cap_female_medium_2_0_extra_spacing, "end_cap_female_medium_2_0_extra_spacing.stl")
export_stl(end_cap_female_medium_2_5_extra_spacing, "end_cap_female_medium_2_5_extra_spacing.stl")
export_stl(end_cap_female_large_2_0, "end_cap_female_large_2_0.stl")
export_stl(end_cap_female_large_2_5, "end_cap_female_large_2_5.stl")
export_stl(end_cap_female_large_2_0_extra_spacing, "end_cap_female_large_2_0_extra_spacing.stl")
export_stl(end_cap_female_large_2_5_extra_spacing, "end_cap_female_large_2_5_extra_spacing.stl")

export_stl(inner_mesh_tube_small, "inner_mesh_tube_small.stl")
export_stl(inner_mesh_tube_small_corkscrew, "inner_mesh_tube_small_corkscrew.stl")
export_stl(inner_mesh_tube_medium, "inner_mesh_tube_medium.stl")
export_stl(inner_mesh_tube_medium_corkscrew, "inner_mesh_tube_medium_corkscrew.stl")
export_stl(inner_mesh_tube_large, "inner_mesh_tube_large.stl")
export_stl(inner_mesh_tube_large_corkscrew, "inner_mesh_tube_large_corkscrew.stl")

# %% Exports STEP

export_step(body_male_small, "body_male_small.step")
export_step(body_male_medium, "body_male_medium.step")
export_step(body_male_large, "body_male_large.step")

export_step(end_cap_male_small, "end_cap_male_small.step")
export_step(end_cap_male_small_extra_spacing, "end_cap_male_small_extra_spacing.step")
export_step(end_cap_male_medium, "end_cap_male_medium.step")
export_step(end_cap_male_medium_extra_spacing, "end_cap_male_medium_extra_spacing.step")
export_step(end_cap_male_large, "end_cap_male_large.step")
export_step(end_cap_male_large_extra_spacing, "end_cap_male_large_extra_spacing.step")

export_step(end_cap_female_small_2_0, "end_cap_female_small_2_0.step")
export_step(end_cap_female_small_2_5, "end_cap_female_small_2_5.step")
export_step(end_cap_female_small_2_0_extra_spacing, "end_cap_female_small_2_0_extra_spacing.step")
export_step(end_cap_female_small_2_5_extra_spacing, "end_cap_female_small_2_5_extra_spacing.step")
export_step(end_cap_female_medium_2_0, "end_cap_female_medium_2_0.step")
export_step(end_cap_female_medium_2_5, "end_cap_female_medium_2_5.step")
export_step(end_cap_female_medium_2_0_extra_spacing, "end_cap_female_medium_2_0_extra_spacing.step")
export_step(end_cap_female_medium_2_5_extra_spacing, "end_cap_female_medium_2_5_extra_spacing.step")
export_step(end_cap_female_large_2_0, "end_cap_female_large_2_0.step")
export_step(end_cap_female_large_2_5, "end_cap_female_large_2_5.step")
export_step(end_cap_female_large_2_0_extra_spacing, "end_cap_female_large_2_0_extra_spacing.step")
export_step(end_cap_female_large_2_5_extra_spacing, "end_cap_female_large_2_5_extra_spacing.step")

export_step(inner_mesh_tube_small, "inner_mesh_tube_small.step")
export_step(inner_mesh_tube_small_corkscrew, "inner_mesh_tube_small_corkscrew.step")
export_step(inner_mesh_tube_medium, "inner_mesh_tube_medium.step")
export_step(inner_mesh_tube_medium_corkscrew, "inner_mesh_tube_medium_corkscrew.step")
export_step(inner_mesh_tube_large, "inner_mesh_tube_large.step")
export_step(inner_mesh_tube_large_corkscrew, "inner_mesh_tube_large_corkscrew.step")

# %%