# %% Imports
from build123d import *
from enum import IntEnum
from math import pi, tan, radians
from bd_warehouse.thread import IsoThread
#from ocp_vscode import *

# %% Config

# Global

class MufflerLength(IntEnum):
    SMALL = 70
    MEDIUM = 85
    LARGE = 100
'''Length of the outer tube+endcaps, excluding connectors'''

class MufflerORingInnerDiameter(IntEnum):
    SMALL = 44
    MEDIUM = 47
    LARGE = 50
'''The small inner diameter of the o-ring between body and end-cap. Corresponds to the inner diameter of body'''

MUFFLER_O_RING_THICKNESS = 3.5
'''The thickness of the o-ring in the muffler'''

MUFFLER_O_RING_SHIFT = 0.4
'''The muffler wall and grip will be shifted this amount, relative to the large O-ring'''

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

GRIP_CUTOUT_RATIO = 1/19
'''The ratio between the muffler outer diameter/radius and grip cutout diameter/radius.'''

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
connector_male_outer_radius = CONNECTOR_MALE_OUTER_DIAMETER/2
connector_male_inner_radius = connector_male_outer_radius - CONNECTOR_MALE_WALL_THICKNESS
inner_mesh_tube_outer_radius = connector_male_inner_radius+INNER_TUBE_MESH_THICKNESS
threading_height = 5*0.8660*THREADING_PITCH/8 # Height of thread ISO standard, https://en.wikipedia.org/wiki/ISO_metric_screw_thread

# %% Threadings

def threading_body(major_diameter: float):
    return IsoThread(major_diameter=major_diameter, pitch=THREADING_PITCH, length=END_CAP_INSERT_LENGTH, end_finishes=("fade","fade"), external=False, interference=0.0)
        
def threading_end_cap(major_diameter: float,
                      threading_extra_spacing_enabled: bool):
    threading_extra_spacing = (THREADING_EXTRA_SPACING_IF_ENABLED
                               if threading_extra_spacing_enabled
                               else 0.0)
    return IsoThread(major_diameter=major_diameter-2*(TOLERANCE+threading_extra_spacing), pitch=THREADING_PITCH, length=END_CAP_INSERT_LENGTH, end_finishes=("fade","fade"), interference=0.0)

# %% Male connector

male_connector_wall_profile = Rectangle(connector_male_outer_radius, CONNECTOR_LENGTH, align=Align.MIN)
male_connector_wall_profile = fillet(male_connector_wall_profile.vertices()[2], CONNECTOR_CORNER_RADIUS)

# %% Female connector

def female_connector_o_ring_slot_profile(connector_female_o_ring_thickness: float):
    # Make slot big enough for, O-ring to expand
    profile = (
        Polygon((connector_female_o_ring_thickness*2, 0),
                (0,-connector_female_o_ring_thickness/1.4),
                (0,connector_female_o_ring_thickness/1.4))
    )
    profile = fillet(profile.vertices()[0], connector_female_o_ring_thickness/2)
    return profile

def female_connector_wall_profile(connector_female_o_ring_thickness: float):
    profile = (
        Pos(connector_male_outer_radius + TOLERANCE,0,0) 
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

def grip_cutout_profile(outer_tube_outer_radius: float):
    grip_cutout_radius = outer_tube_outer_radius*GRIP_CUTOUT_RATIO
    circles = (
        PolarLocations(radius=outer_tube_outer_radius+grip_cutout_radius, count=END_CAP_GRIP_CUTOUT_COUNT)
        * Circle(grip_cutout_radius, align=(Align.CENTER,Align.MIN))
    )
    return Compound(circles)

# %% Base grip

def grip_base_profile(outer_tube_outer_radius: float):
    grip_cutout_radius = outer_tube_outer_radius*GRIP_CUTOUT_RATIO
    # Base grip
    profile = Rectangle(outer_tube_outer_radius+grip_cutout_radius, END_CAP_GRIP_THICKNESS, align=Align.MIN)
    profile = fillet(profile.vertices()[2], END_CAP_CORNER_RADIUS)
    return profile

# %% Body with grip only, no connector

def body_male_profile(muffler_length: MufflerLength,
                      muffler_o_ring_inner_diameter: MufflerORingInnerDiameter):
    outer_tube_inner_radius = muffler_o_ring_inner_diameter/2+MUFFLER_O_RING_SHIFT
    outer_tube_outer_radius = outer_tube_inner_radius+BODY_WALL_THICKNESS
    # Connector
    profile = male_connector_wall_profile
    # Grip
    profile += (
        Pos(0,CONNECTOR_LENGTH) 
        * grip_base_profile(outer_tube_outer_radius)
    )
    # Outer tube
    profile += (
        Pos(0,CONNECTOR_LENGTH+END_CAP_GRIP_THICKNESS) 
        * Rectangle(outer_tube_outer_radius,muffler_length-2*END_CAP_GRIP_THICKNESS, align=Align.MIN)
    )
    # Slot for o-ring
    profile -= (
        Pos((muffler_o_ring_inner_diameter+BODY_WALL_THICKNESS)/2,CONNECTOR_LENGTH+muffler_length-END_CAP_GRIP_THICKNESS)
        * Ellipse(MUFFLER_O_RING_THICKNESS/2, MUFFLER_O_RING_THICKNESS/2.5) # Make slot slightly smaller than o-ring, so it can "squish"
    )
    # Inside of the body
    profile -= Pos(0,CONNECTOR_LENGTH+END_CAP_BOTTOM_THICKNESS) * Rectangle(muffler_o_ring_inner_diameter/2, muffler_length, align=Align.MIN)
    # Slot for inner mesh tube
    profile -= (
        Pos(0,CONNECTOR_LENGTH+END_CAP_BOTTOM_THICKNESS-END_CAP_INNER_TUBE_SLOT_DEPTH) 
        * Rectangle(inner_mesh_tube_outer_radius+TOLERANCE, END_CAP_GRIP_THICKNESS, align=Align.MIN)
    )
    # Hole through connector
    profile -= Rectangle(connector_male_inner_radius, CONNECTOR_LENGTH+END_CAP_BOTTOM_THICKNESS, align=Align.MIN)
    return profile

# %% Male end cap, with connector

def body_male(muffler_length: MufflerLength, 
              muffler_o_ring_inner_diameter: MufflerORingInnerDiameter):
    outer_tube_inner_radius = muffler_o_ring_inner_diameter/2+MUFFLER_O_RING_SHIFT
    outer_tube_outer_radius = outer_tube_inner_radius+BODY_WALL_THICKNESS
    # Revolve 2D profile
    profile = body_male_profile(muffler_length, muffler_o_ring_inner_diameter)
    part = revolve(Plane.XZ * profile)
    # Grip cutout
    body_grip_cutout = grip_cutout_profile(outer_tube_outer_radius)
    part -= extrude(body_grip_cutout, CONNECTOR_LENGTH+END_CAP_GRIP_THICKNESS)
    # Internal threads
    threading = (
        Pos(0,0,CONNECTOR_LENGTH+muffler_length-END_CAP_GRIP_THICKNESS-END_CAP_INSERT_LENGTH-1) 
        * threading_body(outer_tube_inner_radius*2)
    )
    return Compound([part, threading])

# %% End cap grip used by both male & female versions, no connector

def end_cap_grip_base_profile(muffler_o_ring_inner_diameter: MufflerORingInnerDiameter,
                              threading_extra_spacing_enabled: bool):
    outer_tube_inner_radius = muffler_o_ring_inner_diameter/2+MUFFLER_O_RING_SHIFT
    outer_tube_outer_radius = outer_tube_inner_radius+BODY_WALL_THICKNESS
    threading_extra_spacing = THREADING_EXTRA_SPACING_IF_ENABLED if threading_extra_spacing_enabled else 0.0
    # Grip
    profile = grip_base_profile(outer_tube_outer_radius)
    # Threading insert
    profile += (
        Pos(0,END_CAP_GRIP_THICKNESS) 
        * Rectangle(outer_tube_inner_radius-TOLERANCE-threading_height-threading_extra_spacing,END_CAP_INSERT_LENGTH, align=Align.MIN)
    )
    # Slot for o-ring
    profile -= (
        Pos((muffler_o_ring_inner_diameter+BODY_WALL_THICKNESS)/2,END_CAP_GRIP_THICKNESS)
        * Ellipse(MUFFLER_O_RING_THICKNESS/2, MUFFLER_O_RING_THICKNESS/2.5) # Make slot slightly smaller than o-ring, so it can "squish"
    )
    # Inside of the end-cap
    profile -= (
        Pos(0,END_CAP_BOTTOM_THICKNESS) 
        * Rectangle(outer_tube_inner_radius-END_CAP_INSERT_THICKNESS-threading_height-threading_extra_spacing, END_CAP_GRIP_THICKNESS+END_CAP_INSERT_LENGTH, align=Align.MIN)
    )
    # Slot for inner mesh tube
    profile -= (
        Pos(0,END_CAP_BOTTOM_THICKNESS-END_CAP_INNER_TUBE_SLOT_DEPTH) 
        * Rectangle(inner_mesh_tube_outer_radius+TOLERANCE, END_CAP_GRIP_THICKNESS, align=Align.MIN)
    )
    return profile

# %% Male end cap profile

def end_cap_male_profile(muffler_o_ring_inner_diameter: MufflerORingInnerDiameter,
                         threading_extra_spacing_enabled: bool):
    # Connector
    profile = male_connector_wall_profile
    # End-cap grip
    profile += (
        Pos(0,CONNECTOR_LENGTH) 
        * end_cap_grip_base_profile(muffler_o_ring_inner_diameter, threading_extra_spacing_enabled)
    )
    # Hole through connector
    profile -= Rectangle(connector_male_inner_radius, CONNECTOR_LENGTH+END_CAP_BOTTOM_THICKNESS, align=Align.MIN)
    return profile

# %% Male end cap

def end_cap_male(muffler_o_ring_inner_diameter: MufflerORingInnerDiameter, 
                 threading_extra_spacing_enabled: bool = False):
    outer_tube_inner_radius = muffler_o_ring_inner_diameter/2+MUFFLER_O_RING_SHIFT
    outer_tube_outer_radius = outer_tube_inner_radius+BODY_WALL_THICKNESS
    # Revolve 2D profile
    profile = end_cap_male_profile(muffler_o_ring_inner_diameter, threading_extra_spacing_enabled)
    part = revolve(Plane.XZ * profile)
    # Grip cutout
    body_grip_cutout = grip_cutout_profile(outer_tube_outer_radius)
    part -= extrude(body_grip_cutout, CONNECTOR_LENGTH+END_CAP_GRIP_THICKNESS)
    # External threads
    threading = (
        Pos(0,0,CONNECTOR_LENGTH+END_CAP_GRIP_THICKNESS) 
        * threading_end_cap(outer_tube_inner_radius*2, threading_extra_spacing_enabled)
    )
    return Compound([part, threading])

# %% Female end cap profile

def end_cap_female_profile(muffler_o_ring_inner_diameter: MufflerORingInnerDiameter,
                           connector_female_o_ring_thickness: float,
                           threading_extra_spacing_enabled: bool):
    female_connection_inside_radius = connector_male_outer_radius + TOLERANCE
    # Connector
    profile = female_connector_wall_profile(connector_female_o_ring_thickness)
    # End-cap grip
    profile += (
        Pos(0,CONNECTOR_LENGTH) 
        * end_cap_grip_base_profile(muffler_o_ring_inner_diameter, threading_extra_spacing_enabled)
    )
    # Taper the edge inwards between end cap and connector, since the inner mesh tube needs a ledge to sit on
    profile -= (
        Pos(0,CONNECTOR_LENGTH) 
        * Polygon((0, 0),
                (female_connection_inside_radius, 0),
                (0, female_connection_inside_radius))
    )
    # Cut off top of taper, in case the top of taper becomes narrower then a male connector diameter
    profile -= Rectangle(connector_male_inner_radius, CONNECTOR_LENGTH+END_CAP_BOTTOM_THICKNESS, align=Align.MIN)
    return profile

# %% Female end cap

def end_cap_female(muffler_o_ring_inner_diameter: MufflerORingInnerDiameter, 
                   connector_female_o_ring_thickness: float, 
                   threading_extra_spacing_enabled: bool = False):
    outer_tube_inner_radius = muffler_o_ring_inner_diameter/2+MUFFLER_O_RING_SHIFT
    outer_tube_outer_radius = outer_tube_inner_radius+BODY_WALL_THICKNESS
    # Revolve 2D profile
    profile = end_cap_female_profile(muffler_o_ring_inner_diameter, connector_female_o_ring_thickness, threading_extra_spacing_enabled)
    part = revolve(Plane.XZ * profile)
    # Grip cutout
    body_grip_cutout = grip_cutout_profile(outer_tube_outer_radius)
    part -= extrude(body_grip_cutout, CONNECTOR_LENGTH+END_CAP_GRIP_THICKNESS)
    # External threads
    threading = (
        Pos(0,0,CONNECTOR_LENGTH+END_CAP_GRIP_THICKNESS) 
        * threading_end_cap(outer_tube_inner_radius*2, threading_extra_spacing_enabled)
    )
    return Compound([part, threading])

# %% Inner mesh tube

def inner_mesh_tube(muffler_length: MufflerLength, 
                    include_corkscrew: bool):
    inner_tube_length = muffler_length-2*END_CAP_BOTTOM_THICKNESS+2*END_CAP_INNER_TUBE_SLOT_DEPTH
    ring_profile = Rectangle(INNER_TUBE_MESH_THICKNESS, INNER_TUBE_MESH_THICKNESS, align=Align.MIN)
    # End rings
    bottom_ring = revolve(Plane.XZ * Pos(connector_male_inner_radius,0) * ring_profile)
    top_ring = Pos(0,0,inner_tube_length-INNER_TUBE_MESH_THICKNESS) * bottom_ring
    # Mesh
    ring_circumference = pi*CONNECTOR_MALE_OUTER_DIAMETER
    pitch = tan(radians(90-INNER_TUBE_MESH_TWIST_ANGLE))*ring_circumference
    clockwise_helix = Helix(pitch, inner_tube_length, connector_male_inner_radius)
    anticlockwise_helix = Helix(pitch, inner_tube_length, connector_male_inner_radius, lefthand=True)
    mesh_profile = Rectangle(INNER_TUBE_MESH_THICKNESS, INNER_TUBE_MESH_THICKNESS, align=(Align.MIN, Align.CENTER))
    clockwise = sweep(Pos(connector_male_inner_radius,0,0) * mesh_profile, clockwise_helix, is_frenet=True)
    anticlockwise = sweep(Pos(connector_male_inner_radius,0,0) * mesh_profile, anticlockwise_helix, is_frenet=True)
    # Make a flat Compound of all the objects
    solids = [bottom_ring, top_ring]
    # Optional corkscrew
    if include_corkscrew:
        clockwise_helix = Helix(INNER_TUBE_SCREW_TWIST_TURNS*inner_tube_length, inner_tube_length, connector_male_inner_radius)
        corkscrew_profile = Rectangle(connector_male_inner_radius, INNER_TUBE_CORKSCREW_THICKNESS, align=Align.MAX)
        corkscrew = sweep(Pos(connector_male_inner_radius,0,0) * corkscrew_profile, clockwise_helix, is_frenet=True)
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

export_stl(body_male_small, "v2-body-male-small.stl")
export_stl(body_male_medium, "v2-body-male-medium.stl")
export_stl(body_male_large, "v2-body-male-large.stl")

export_stl(end_cap_male_small, "v2-end-cap-male-small.stl")
export_stl(end_cap_male_small_extra_spacing, "v2-end-cap-male-small-extra-spacing.stl")
export_stl(end_cap_male_medium, "v2-end-cap-male-medium.stl")
export_stl(end_cap_male_medium_extra_spacing, "v2-end-cap-male-medium-extra-spacing.stl")
export_stl(end_cap_male_large, "v2-end-cap-male-large.stl")
export_stl(end_cap_male_large_extra_spacing, "v2-end-cap-male-large-extra-spacing.stl")

export_stl(end_cap_female_small_2_0, "v2-end-cap-female-small-2-0.stl")
export_stl(end_cap_female_small_2_5, "v2-end-cap-female-small-2-5.stl")
export_stl(end_cap_female_small_2_0_extra_spacing, "v2-end-cap-female-small-2-0-extra-spacing.stl")
export_stl(end_cap_female_small_2_5_extra_spacing, "v2-end-cap-female-small-2-5-extra-spacing.stl")
export_stl(end_cap_female_medium_2_0, "v2-end-cap-female-medium-2-0.stl")
export_stl(end_cap_female_medium_2_5, "v2-end-cap-female-medium-2-5.stl")
export_stl(end_cap_female_medium_2_0_extra_spacing, "v2-end-cap-female-medium-2-0-extra-spacing.stl")
export_stl(end_cap_female_medium_2_5_extra_spacing, "v2-end-cap-female-medium-2-5-extra-spacing.stl")
export_stl(end_cap_female_large_2_0, "v2-end-cap-female-large-2-0.stl")
export_stl(end_cap_female_large_2_5, "v2-end-cap-female-large-2-5.stl")
export_stl(end_cap_female_large_2_0_extra_spacing, "v2-end-cap-female-large-2-0-extra-spacing.stl")
export_stl(end_cap_female_large_2_5_extra_spacing, "v2-end-cap-female-large-2-5-extra-spacing.stl")

export_stl(inner_mesh_tube_small, "v2-inner-mesh-tube-small.stl")
export_stl(inner_mesh_tube_small_corkscrew, "v2-inner-mesh-tube-small-corkscrew.stl")
export_stl(inner_mesh_tube_medium, "v2-inner-mesh-tube-medium.stl")
export_stl(inner_mesh_tube_medium_corkscrew, "v2-inner-mesh-tube-medium-corkscrew.stl")
export_stl(inner_mesh_tube_large, "v2-inner-mesh-tube-large.stl")
export_stl(inner_mesh_tube_large_corkscrew, "v2-inner-mesh-tube-large-corkscrew.stl")

# %% Exports STEP

export_step(body_male_small, "v2-body-male-small.step")
export_step(body_male_medium, "v2-body-male-medium.step")
export_step(body_male_large, "v2-body-male-large.step")

export_step(end_cap_male_small, "v2-end-cap-male-small.step")
export_step(end_cap_male_small_extra_spacing, "v2-end-cap-male-small-extra-spacing.step")
export_step(end_cap_male_medium, "v2-end-cap-male-medium.step")
export_step(end_cap_male_medium_extra_spacing, "v2-end-cap-male-medium-extra-spacing.step")
export_step(end_cap_male_large, "v2-end-cap-male-large.step")
export_step(end_cap_male_large_extra_spacing, "v2-end-cap-male-large-extra-spacing.step")

export_step(end_cap_female_small_2_0, "v2-end-cap-female-small-2-0.step")
export_step(end_cap_female_small_2_5, "v2-end-cap-female-small-2-5.step")
export_step(end_cap_female_small_2_0_extra_spacing, "v2-end-cap-female-small-2-0-extra-spacing.step")
export_step(end_cap_female_small_2_5_extra_spacing, "v2-end-cap-female-small-2-5-extra-spacing.step")
export_step(end_cap_female_medium_2_0, "v2-end-cap-female-medium-2-0.step")
export_step(end_cap_female_medium_2_5, "v2-end-cap-female-medium-2-5.step")
export_step(end_cap_female_medium_2_0_extra_spacing, "v2-end-cap-female-medium-2-0-extra-spacing.step")
export_step(end_cap_female_medium_2_5_extra_spacing, "v2-end-cap-female-medium-2-5-extra-spacing.step")
export_step(end_cap_female_large_2_0, "v2-end-cap-female-large-2-0.step")
export_step(end_cap_female_large_2_5, "v2-end-cap-female-large-2-5.step")
export_step(end_cap_female_large_2_0_extra_spacing, "v2-end-cap-female-large-2-0-extra-spacing.step")
export_step(end_cap_female_large_2_5_extra_spacing, "v2-end-cap-female-large-2-5-extra-spacing.step")

export_step(inner_mesh_tube_small, "v2-inner-mesh-tube-small.step")
export_step(inner_mesh_tube_small_corkscrew, "v2-inner-mesh-tube-small-corkscrew.step")
export_step(inner_mesh_tube_medium, "v2-inner-mesh-tube-medium.step")
export_step(inner_mesh_tube_medium_corkscrew, "v2-inner-mesh-tube-medium-corkscrew.step")
export_step(inner_mesh_tube_large, "v2-inner-mesh-tube-large.step")
export_step(inner_mesh_tube_large_corkscrew, "v2-inner-mesh-tube-large-corkscrew.step")

# %%