# %% Imports
from build123d import *
from math import pi, tan, radians
from bd_warehouse.thread import IsoThread
from ocp_vscode import *

# %% Config

# Global

muffler_length_small = 70
'''Length of the small outer tube+endcaps, excluding connectors'''

muffler_length_medium = 85
'''Length of the medium outer tube+endcaps, excluding connectors'''

muffler_length_large = 100
'''Length of the large outer tube+endcaps, excluding connectors'''

muffler_o_ring_inner_diameter_small = 44
'''The small inner diameter of the o-ring between body and end-cap. Corresponds to the inner diameter of body'''

muffler_o_ring_inner_diameter_medium = 47
'''The medium inner diameter of the o-ring between body and end-cap. Corresponds to the inner diameter of body'''

muffler_o_ring_inner_diameter_large = 50
'''The large inner diameter of the o-ring between body and end-cap. Corresponds to the inner diameter of body'''

muffler_o_ring_thickness = 3.5
'''The thickness of the o-ring in the muffler'''

tolerance = 0.2
'''Extra spacing added for parts that are assembled together, increase if too tight'''

# Connector

connector_male_outer_diameter = 22.5
'''Diameter of tube connector'''

connector_length = 20
'''The length of connector'''

connector_male_wall_thickness = 2
'''Thickness of the male connector wall'''

connector_female_wall_thickness = 4
'''Thickness of the female connector wall'''

connector_female_o_ring_inner_diameter = 21
'''Inner diameter of the o-ring in the female connector'''

connector_corner_radius = 1
'''The rounding radius of the connector edge'''

# Body

body_wall_thickness = 4
'''The thickness of the outside tube'''

# End cap

end_cap_corner_radius = 2
'''The rounding radius of the end cap/outer tube'''

end_cap_thickness = 4
'''The thickness of the end cap wall'''

end_cap_grip_thickness = 10
'''The thickness of the end cap grip'''

end_cap_recess_for_inner_tube = 2
'''The recess depth inside the endcap, where the inner tube is resting'''

end_cap_insert_length = 10
'''The length of the end cap insert'''

end_cap_insert_thickness = 2
'''The thickness of the end cap insert'''

end_cap_grip_cutout_count = 30
'''The number of cutouts making a grip in the end cap'''

grip_cutout_diameter_ratio = 1/19
'''The ratio between the muffler outer diameter and grip cutout diameter.'''

# Threading

threading_pitch = 2.0
'''The pitch of the threading'''

# Inner tube/mesh

inner_tube_screw_thickness = 1
'''The thickness of the inner tube corkscrew'''

inner_tube_extra_length = 0
'''Extra length added to inner tube. Useful if a big rubber gasket between outer tube and end caps leaves big gap.'''

inner_tube_screw_twist_turns = 1
'''The number of turns (360 degrees) of the inside screw.'''

inner_tube_mesh_thickness = 1.5
'''The thickness of the inner tube wall/mesh'''

inner_tube_mesh_count = 15
'''The number of mesh lines'''

inner_tube_mesh_twist_angle = 35
'''The angle (degrees) in the mesh pattern.'''

# Calculations
connector_male_inner_diameter = connector_male_outer_diameter - 2*connector_male_wall_thickness
inner_tube_diameter = connector_male_inner_diameter+2*inner_tube_mesh_thickness
threading_height = 5*0.8660*threading_pitch/8 # Height of thread ISO standard, https://en.wikipedia.org/wiki/ISO_metric_screw_thread

# %% Male connector

male_connector_wall_profile = Rectangle(connector_male_wall_thickness, connector_length, align=Align.MIN)
male_connector_wall_profile = fillet(male_connector_wall_profile.vertices()[2], connector_corner_radius)
male_connector = revolve(
    Plane.XZ 
    * Pos(connector_male_inner_diameter/2,0,0) 
    * male_connector_wall_profile)

male_connector_inside = Circle(connector_male_outer_diameter/2-connector_male_wall_thickness)
female_connector_inside = Circle(connector_male_outer_diameter/2 + tolerance)

# %% Female connector

def female_connector_o_ring_slot(connector_female_o_ring_thickness):
    # Make slot big enough for, O-ring to expand
    profile = Polygon((connector_female_o_ring_thickness*2, 0), (0,-connector_female_o_ring_thickness/1.4), (0,connector_female_o_ring_thickness/1.4))
    profile = fillet(profile.vertices()[0], connector_female_o_ring_thickness/2)
    return profile

def female_connector(connector_length, connector_corner_radius, connector_female_o_ring_thickness):
    wall_profile = Rectangle(connector_female_wall_thickness, connector_length, align=Align.MIN)
    if connector_corner_radius > 0:
        wall_profile = fillet(wall_profile.vertices()[2], connector_corner_radius)
    # O-ring inside connector
    wall_profile -= (
        Pos(-(connector_male_outer_diameter-connector_female_o_ring_inner_diameter)/2,connector_length/5) 
        * female_connector_o_ring_slot(connector_female_o_ring_thickness)
    )
    part = revolve(
        Plane.XZ 
        * Pos(connector_male_outer_diameter/2 + tolerance,0,0) 
        * wall_profile)
    return part

# %% Grip cutout

def grip_cutout(outer_tube_outer_diameter):
    grip_cutout_diameter = outer_tube_outer_diameter*grip_cutout_diameter_ratio
    part = (
        PolarLocations(radius=(outer_tube_outer_diameter+grip_cutout_diameter)/2, count=end_cap_grip_cutout_count)
        * Cylinder(grip_cutout_diameter/2, end_cap_grip_thickness, align=(Align.CENTER,Align.MIN))
    )
    return part

# %% Body grip 2D profile, to be revolved

def body_grip_profile(muffler_length, muffler_o_ring_inner_diameter):
    outer_tube_inner_diameter = muffler_o_ring_inner_diameter
    outer_tube_outer_diameter = outer_tube_inner_diameter+2*body_wall_thickness
    grip_cutout_diameter = outer_tube_outer_diameter*grip_cutout_diameter_ratio
    # Base grip
    profile = Rectangle((outer_tube_outer_diameter+grip_cutout_diameter)/2, end_cap_grip_thickness, align=Align.MIN)
    profile = fillet(profile.vertices()[2], end_cap_corner_radius)
    # Body wall
    profile += Rectangle(outer_tube_outer_diameter/2,muffler_length-end_cap_grip_thickness, align=Align.MIN)
    # Inside of the body
    profile -= (
        Pos(0,end_cap_thickness)
        * Rectangle(outer_tube_inner_diameter/2,muffler_length_large, align=Align.MIN)
    )
    # Slot for inner mesh tube
    profile -= (
        Pos(0,end_cap_thickness-end_cap_recess_for_inner_tube)
        * Rectangle(inner_tube_diameter/2+tolerance,end_cap_grip_thickness-end_cap_thickness, align=Align.MIN)
    )
    # Slot for o-ring
    profile -= (
        Pos((muffler_o_ring_inner_diameter+body_wall_thickness)/2,muffler_length-end_cap_grip_thickness)
        * Ellipse(muffler_o_ring_thickness/2, muffler_o_ring_thickness/2.5) # Make slot slightly smaller than o-ring, so it can "squish"
    )
    return profile

# %% Body grip only, no connector

def body_grip_male(muffler_length, muffler_o_ring_inner_diameter):
    outer_tube_inner_diameter = muffler_o_ring_inner_diameter
    outer_tube_outer_diameter = outer_tube_inner_diameter+2*body_wall_thickness
    # Profile of whole body, except threads & connector
    profile = body_grip_profile(muffler_length, muffler_o_ring_inner_diameter)
    part = revolve(Plane.XZ * profile)
    # Grip
    body_grip_cutout = grip_cutout(outer_tube_outer_diameter)
    part -= body_grip_cutout
    # Internal threads
    part += (
        Pos(0,0,muffler_length-end_cap_grip_thickness-end_cap_insert_length-1) 
        * IsoThread(major_diameter=outer_tube_inner_diameter+0.01, pitch=threading_pitch, length=end_cap_insert_length+1, end_finishes=("fade","fade"), external=False)
    )
    part -= extrude(male_connector_inside, end_cap_thickness)
    return part

# %% Male end cap, with connector

def body_male(muffler_length, muffler_o_ring_inner_diameter):
    body = (
        Pos(0,0,connector_length) 
        * body_grip_male(muffler_length, muffler_o_ring_inner_diameter)
    )
    return body + male_connector

# %% End cap grip 2D profile, to be revolved

def end_cap_grip_profile(muffler_o_ring_inner_diameter, threading_extra_spacing):
    outer_tube_inner_diameter = muffler_o_ring_inner_diameter
    outer_tube_outer_diameter = outer_tube_inner_diameter+2*body_wall_thickness
    grip_cutout_diameter = outer_tube_outer_diameter*grip_cutout_diameter_ratio
    # Base grip
    profile = Rectangle((outer_tube_outer_diameter+grip_cutout_diameter)/2, end_cap_grip_thickness, align=Align.MIN)
    profile = fillet(profile.vertices()[2], end_cap_corner_radius)
    # Threading insert
    profile += Rectangle(outer_tube_inner_diameter/2-tolerance-threading_height-threading_extra_spacing,end_cap_grip_thickness+end_cap_insert_length, align=Align.MIN)
    # Inside of the threading insert
    profile -= (
        Pos(0,end_cap_thickness)
        * Rectangle(outer_tube_inner_diameter/2-end_cap_insert_thickness-threading_height-threading_extra_spacing,end_cap_grip_thickness+end_cap_insert_length, align=Align.MIN)
    )
    # Slot for inner mesh tube
    profile -= (
        Pos(0,end_cap_thickness-end_cap_recess_for_inner_tube)
        * Rectangle(inner_tube_diameter/2+tolerance,end_cap_grip_thickness-end_cap_thickness, align=Align.MIN)
    )
    # Slot for o-ring
    profile -= (
        Pos((muffler_o_ring_inner_diameter+body_wall_thickness)/2,end_cap_grip_thickness)
        * Ellipse(muffler_o_ring_thickness/2, muffler_o_ring_thickness/2.5) # Make slot slightly smaller than o-ring, so it can "squish"
    )
    return profile

# %% End cap grip used by both male & female versions, no connector

def end_cap_grip_base(muffler_o_ring_inner_diameter, threading_extra_spacing):
    outer_tube_inner_diameter = muffler_o_ring_inner_diameter
    outer_tube_outer_diameter = outer_tube_inner_diameter+2*body_wall_thickness
    # Profile of whole end-cap, except threads & connector
    profile = end_cap_grip_profile(muffler_o_ring_inner_diameter, threading_extra_spacing)
    part = revolve(Plane.XZ * profile)
    # Grip
    end_cap_grip_cutout = grip_cutout(outer_tube_outer_diameter)
    part -= end_cap_grip_cutout
    # External threads
    part += (
        Pos(0,0,end_cap_grip_thickness) 
        * IsoThread(major_diameter=outer_tube_inner_diameter-2*tolerance-threading_extra_spacing, pitch=threading_pitch, length=end_cap_insert_length, end_finishes=("fade","fade"), interference=0.0)
    )
    return part

show(end_cap_grip_base(muffler_o_ring_inner_diameter_large, 0))

# %% Male end cap grip

def end_cap_grip_male(muffler_o_ring_inner_diameter, threading_extra_spacing):
    part = (
        end_cap_grip_base(muffler_o_ring_inner_diameter, threading_extra_spacing) 
        - extrude(male_connector_inside, end_cap_thickness)
    )
    return part

# %% Female end cap grip

def end_cap_grip_female(muffler_o_ring_inner_diameter, threading_extra_spacing):
    part = (
        end_cap_grip_base(muffler_o_ring_inner_diameter, threading_extra_spacing)
        # Taper the edge inwards between end cap and connector, since the inner mesh tube needs a ledge to sit on
        - extrude(female_connector_inside, end_cap_thickness, taper=45)
    )
    # Cut off top of taper, in case the top of taper becomes narrower then a male connector diameter
    part -= extrude(male_connector_inside, end_cap_thickness)
    return part

# %% Male end cap, with connector

def end_cap_male(muffler_o_ring_inner_diameter, threading_extra_spacing = 0.0):
    part = male_connector + (
        Pos(0,0,connector_length) 
        * end_cap_grip_male(muffler_o_ring_inner_diameter, threading_extra_spacing)
    )
    return part

# %% Female end cap, with connector

def end_cap_female(muffler_o_ring_inner_diameter, connector_female_o_ring_thickness, threading_extra_spacing = 0.0):
    part = female_connector(connector_length, connector_corner_radius, connector_female_o_ring_thickness) + (
        Pos(0,0,connector_length) 
        * end_cap_grip_female(muffler_o_ring_inner_diameter, threading_extra_spacing)
    )
    return part

# %% Inner mesh tube

def inner_mesh_tube(muffler_length, includeCorkscrew):
    inner_tube_length = muffler_length-2*end_cap_thickness+2*end_cap_recess_for_inner_tube+inner_tube_extra_length
    ring_profile = Rectangle(inner_tube_mesh_thickness, inner_tube_mesh_thickness, align=Align.MIN)
    # End rings
    bottom_ring = revolve(Plane.XZ * Pos(connector_male_inner_diameter/2,0) * ring_profile)
    top_ring = Pos(0,0,inner_tube_length-inner_tube_mesh_thickness) * bottom_ring
    # Mesh
    ring_circumference = pi*connector_male_outer_diameter
    pitch = tan(radians(90-inner_tube_mesh_twist_angle))*ring_circumference
    clockwise_helix = Helix(pitch, inner_tube_length, connector_male_inner_diameter/2)
    anticlockwise_helix = Helix(pitch, inner_tube_length, connector_male_inner_diameter/2, lefthand=True)
    mesh_profile = Rectangle(inner_tube_mesh_thickness, inner_tube_mesh_thickness, align=(Align.MIN, Align.CENTER))
    clockwise = sweep(Pos(connector_male_inner_diameter/2,0,0) * mesh_profile, clockwise_helix, is_frenet=True)
    anticlockwise = sweep(Pos(connector_male_inner_diameter/2,0,0) * mesh_profile, anticlockwise_helix, is_frenet=True)
    # Make a flat Compound of all the objects
    solids = [bottom_ring, top_ring]
    # Optional corkscrew
    if includeCorkscrew:
        clockwise_helix = Helix(inner_tube_screw_twist_turns*inner_tube_length, inner_tube_length, connector_male_inner_diameter/2)
        corkscrew_profile = Rectangle(connector_male_inner_diameter, inner_tube_screw_thickness, align=Align.MAX)
        corkscrew = sweep(Pos(connector_male_inner_diameter/2,0,0) * corkscrew_profile, clockwise_helix, is_frenet=True)
        solids.append(corkscrew)
    # Merge mesh strands into same Compound
    for i in range(inner_tube_mesh_count):
        strand = Rot(Z=i * 360 / inner_tube_mesh_count) * clockwise
        solids.append(strand)
        antistrand = Rot(Z=i * 360 / inner_tube_mesh_count) * anticlockwise
        solids.append(antistrand)
    return Compound(solids)

# %% Generate parts

body_male_large = body_male(muffler_length_large, muffler_o_ring_inner_diameter_large)
body_male_large = body_male(muffler_length_large, muffler_o_ring_inner_diameter_large)
body_male_large = body_male(muffler_length_large, muffler_o_ring_inner_diameter_large)
end_cap_male_large = end_cap_male(muffler_o_ring_inner_diameter_large)
end_cap_male_large_extra_spacing = end_cap_male(muffler_o_ring_inner_diameter_large, 0.2)
end_cap_female_large_2_0 = end_cap_female(muffler_o_ring_inner_diameter_large, 2.0)
end_cap_female_large_2_5 = end_cap_female(muffler_o_ring_inner_diameter_large, 2.5)
end_cap_female_large_2_0_extra_spacing = end_cap_female(muffler_o_ring_inner_diameter_large, 2.0, 0.2)
end_cap_female_large_2_5_extra_spacing = end_cap_female(muffler_o_ring_inner_diameter_large, 2.5, 0.2)
inner_mesh_tube_large = inner_mesh_tube(muffler_length_large, False)
inner_mesh_tube_large_corkscrew = inner_mesh_tube(muffler_length_large, True)

# Debug
#test_body_grip_male_small = body_grip_male(muffler_length_small, muffler_o_ring_inner_diameter_small)
#test_end_cap_base_small_extra_spacing = end_cap_grip_male(muffler_o_ring_inner_diameter_small, 0.2)
#test_body_grip_male_large = body_grip_male(muffler_length_large, muffler_o_ring_inner_diameter_large)
#test_end_cap_base_large = end_cap_grip_male(muffler_o_ring_inner_diameter_large)
#test_body_grip_male_medium = body_grip_male(muffler_length_medium, muffler_o_ring_inner_diameter_medium)
#test_end_cap_base_medium_extra_spacing = end_cap_grip_male(muffler_o_ring_inner_diameter_medium, 0.2)
#female_connector_test = female_connector(8, 0, 2.5)

show(body_male_large)

# %% Exports STL

export_stl(body_male_large, "body_male_large.stl")

# %% Exports STEP

export_step(body_male_large, "body_male_large.step")

# %%
