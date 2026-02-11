// Type of part to render
Part = "AllFemale"; // [AllFemale, AllMale, Combined, MufflerBase, InnerTube, EndCapMale, EndCapFemale, Gasket]

// Length of the outer tube+endcaps, excluding connectors
Muffler_Length = 100; // [20:1:200]

// The length of connector
Connector_Length = 20; // [0:1:30]

// Diameter of tube connector
Connector_Male_Outer_Diameter = 22.5; // [0:0.1:30]

// Extra spacing added for parts that are assembled together, increase if too tight
Tolerance = 0.2; // [0:0.05:0.5]

/* [Seal-edge] */

// Enable the extra edge, which may make it easier to make it air-tight
Enable_Seal_Edge = false;

/* [Connector] */

// Thickness of the male connector wall
Connector_Male_Wall_Thickness = 2; // [0.1:0.1:4]

// Thickness of the female connector wall
Connector_Female_Wall_Thickness = 3; // [0.1:0.1:4]

// The rounding radius of the connector edge
Connector_Corner_Radius = 1; // [0:0.1:4]

// The rounding radius of the connector edge
Female_Connector_O_Ring_Thickness = 2; // [0:0.1:4]

/* [Body] */

// The thickness of the outside tube
Muffler_Wall_Thickness = 4; // [0.1:0.1:10]

// The length of the chamber (radius difference) between inner tube and outside wall
Chamber_Thickness = 15; // [0:1:30]

/* [End cap] */

// The rounding radius of the end cap/outer tube
End_Cap_Corner_Radius = 2; // [0:0.1:4]

// The thickness of the end cap wall
End_Cap_Thickness = 4; // [0:0.1:10]

// The thickness of the end cap wall
End_Cap_Grip_Thickness = 10; // [0:1:50]

// The recess depth inside the endcap, where the inner tube is resting
End_Cap_Recess_For_Inner_Tube = 2; // [0:0.1:5]

// The length of the end cap insert
End_Cap_Insert_Length = 10; // [0:1:50]

// The thickness of the end cap insert
End_Cap_Insert_Thickness = 2; // [0:0.1:3]

// The number of cutouts making a grip in the end cap
End_Cap_Grip_Cutout_Count = 30; // [0:1:50]

// The diameter of each cutout in the grip
End_Cap_Grip_Cutout_Diameter = 3; // [0.1:0.1:5]

/* [Threading] */

// The pitch of the threading
Threading_Pitch = 2.0; // [0:0.1:4]

// The number of starts in the threading
Threading_N_Starts = 1; // [1:1:10]

// Makes the end of the threading smaller, so its easier to insert
Threading_Taper = 0.1; // [0:0.01:1]

// Extra spacing between outer shell and end cap thread, to increase tolerance.
Threading_Extra_Spacing = 0.0;

/* [Inner tube/mesh] */

// Enable/Disable inside screw
Inner_Tube_Screw_Enabled = true;

// The thickness of the inner tube screw
Inner_Tube_Screw_Thickness = 1; // [0:0.1:3]

// Extra length added to inner tube. Useful if using rubber gaskets between outer tube and end caps.
Inner_Tube_Extra_Length = 0; // [0:0.1:3]

// The number of turns (360 degrees) of the inside screw.
Inner_Tube_Screw_Twist_Turns = 1; // [0:0.1:3]

// The thickness of the inner tube wall/mesh
Inner_Tube_Mesh_Thickness = 1.5; // [0:0.1:3]

// The number of mesh lines
Inner_Tube_Mesh_Count = 15; // [50]

// The angle (degrees) in the mesh pattern.
Inner_Tube_Mesh_Twist_Angle = 35; // [0:1:70]

/* [Gasket (Optional)] */

// The thickness of the optional gasket
Gasket_Thickness = 0.8;

// Calculations
Connector_Male_Inner_Diameter = Connector_Male_Outer_Diameter - 2*Connector_Male_Wall_Thickness;
Connector_Female_Outer_Diameter = Connector_Male_Outer_Diameter + 2*Connector_Female_Wall_Thickness;
Inner_Tube_Diameter = Connector_Male_Inner_Diameter+2*Inner_Tube_Mesh_Thickness;
Inner_Tube_Length = Muffler_Length-2*End_Cap_Thickness+2*End_Cap_Recess_For_Inner_Tube+Inner_Tube_Extra_Length;
Outer_Tube_Length = Muffler_Length-2*End_Cap_Grip_Thickness;
Outer_Tube_Inner_Diameter = Inner_Tube_Diameter+2*Chamber_Thickness;
Outer_Tube_Outer_Diameter = Outer_Tube_Inner_Diameter+2*Muffler_Wall_Thickness;

module inner_tube_inner_screw() {
    linear_extrude(Inner_Tube_Length, twist=Inner_Tube_Screw_Twist_Turns*360, slices=50) {
        translate([-Connector_Male_Inner_Diameter/2, -0.5, 0])
            square([Connector_Male_Inner_Diameter,Inner_Tube_Screw_Thickness]);
    }
}

module inner_tube_end_ring() {
    rotate_extrude(angle = 360, $fn = 50) {
        translate([Connector_Male_Inner_Diameter/2,0,0]) {
            square(Inner_Tube_Mesh_Thickness);
        }
    }
}

module inner_tube_mesh() {
    for (angle = [0 : 360/Inner_Tube_Mesh_Count : 359]) {
        linear_extrude(Inner_Tube_Length, twist=tan(Inner_Tube_Mesh_Twist_Angle)*360*Inner_Tube_Length/(Connector_Male_Outer_Diameter*PI)) {
            rotate(angle) {
                translate([Connector_Male_Inner_Diameter/2,-Inner_Tube_Mesh_Thickness/2,0]) {
                    square(Inner_Tube_Mesh_Thickness);
                }
            }
        }
        if (Inner_Tube_Mesh_Twist_Angle > 0) {
            linear_extrude(Inner_Tube_Length, twist=-tan(Inner_Tube_Mesh_Twist_Angle)*360*Inner_Tube_Length/(Connector_Male_Outer_Diameter*PI)) {
                rotate(angle) {
                    translate([Connector_Male_Inner_Diameter/2,-Inner_Tube_Mesh_Thickness/2,0]) {
                        square(Inner_Tube_Mesh_Thickness);
                    }
                }
            }
        }
    }
}

module inner_tube() {
    if (Inner_Tube_Screw_Enabled) {
        inner_tube_inner_screw();
    }
    if (Inner_Tube_Mesh_Count > 0) {
        inner_tube_mesh();
        inner_tube_end_ring();
        translate([0,0,Inner_Tube_Length-Inner_Tube_Mesh_Thickness]) {
            inner_tube_end_ring();
        }
    }
}

module threading(diameter, length, internal=false, taper=0) {
    metric_thread (diameter=diameter, pitch=Threading_Pitch, length=length, n_starts=Threading_N_Starts,internal=internal,taper=taper);
}

module seal_edge(removeLength = 0) {
    rotate_extrude(angle = 360, $fn = 100) {
        translate([Outer_Tube_Outer_Diameter/2-1.5,0])
            difference() {
                polygon([[1,0],[-1,0],[0,1]]);
                translate([0,1])
                    square(removeLength*2, center=true);
            }
    }
}

module grip(includeThreading = false) {
    difference() {
        union() {
            difference() {
                translate([0,0,End_Cap_Corner_Radius])
                {
                    minkowski() {
                        cylinder(d=Outer_Tube_Outer_Diameter-2*End_Cap_Corner_Radius+End_Cap_Grip_Cutout_Diameter, h = End_Cap_Grip_Thickness, $fn = 100);
                        sphere(r=End_Cap_Corner_Radius, $fn = 20);
                    }
                }
                translate([0,0,End_Cap_Grip_Thickness])
                    cylinder(d=2*Outer_Tube_Outer_Diameter, h = 10*End_Cap_Grip_Thickness);
            }
            if (includeThreading) {
                translate([0,0,End_Cap_Grip_Thickness])
                    //cylinder(End_Cap_Insert_Length, d=Outer_Tube_Inner_Diameter+2, $fn = 50);
                    threading(diameter = Outer_Tube_Inner_Diameter+2-2*Threading_Extra_Spacing-2*Tolerance, length=End_Cap_Insert_Length, taper=Threading_Taper);
            }
        }
        union() {
            translate([0,0,End_Cap_Thickness-End_Cap_Recess_For_Inner_Tube-Tolerance])
                cylinder(d=Inner_Tube_Diameter+2*Tolerance, h = End_Cap_Insert_Length+1, $fn = 50);
            translate([0,0,End_Cap_Thickness])
                cylinder(d=Outer_Tube_Inner_Diameter-2*End_Cap_Insert_Thickness, h = End_Cap_Grip_Thickness+End_Cap_Insert_Length+1, $fn = 50);
            for (angle = [0 : 360/End_Cap_Grip_Cutout_Count : 359]) {
                translate([cos(angle)*(Outer_Tube_Outer_Diameter+End_Cap_Grip_Cutout_Diameter)/2,sin(angle)*(Outer_Tube_Outer_Diameter+End_Cap_Grip_Cutout_Diameter)/2,-0.5])
                    cylinder(h = 2*End_Cap_Grip_Thickness, d = End_Cap_Grip_Cutout_Diameter, $fn = 50);
            }
            
            if (Enable_Seal_Edge)
                translate([0,0,End_Cap_Grip_Thickness+0.4]) // Reduce space in seal, so it becomes tight
                    rotate([180,0,0])
                        seal_edge();
        }
    }
}

module muffler_base() {
    difference() {
        union() {
            end_cap_male(false);
            translate([0,0,End_Cap_Grip_Thickness])
                cylinder(h = Outer_Tube_Length, d = Outer_Tube_Outer_Diameter, $fn = 100);
                
            if (Enable_Seal_Edge)
                translate([0,0,End_Cap_Grip_Thickness+Outer_Tube_Length])
                    seal_edge(removeLength=0.3);
        }
        translate([0,0,End_Cap_Thickness])
            cylinder(h = Outer_Tube_Length+End_Cap_Grip_Thickness+1, d = Outer_Tube_Inner_Diameter, $fn = 50);
        translate([0,0,End_Cap_Grip_Thickness+Outer_Tube_Length])
            rotate([180,0,0])
                threading(diameter = Outer_Tube_Inner_Diameter+2+2*Tolerance, length=End_Cap_Insert_Length+1, internal=true);
    }
}
    
module end_cap_male(includeThreading) {
    difference() {
        union() {
            translate([0,0,-Connector_Length+Connector_Corner_Radius])
                minkowski() {
                    cylinder(d = Connector_Male_Outer_Diameter-2*Connector_Corner_Radius, h = Connector_Length+0.1, $fn = 50);
                    sphere(r=Connector_Corner_Radius, $fn = 20);
                }
            grip(includeThreading);
        }
        translate([0,0,-Connector_Length-0.5])
                cylinder(d=Connector_Male_Inner_Diameter, h = Connector_Length+End_Cap_Grip_Thickness+1);
    }
}
    
module end_cap_female(includeThreading) {
    difference() {
        union() {
            translate([0,0,-Connector_Length+Connector_Corner_Radius])
                minkowski() {
                    cylinder(d = Connector_Female_Outer_Diameter-2*Connector_Corner_Radius, h = Connector_Length+0.1, $fn = 50);
                    sphere(r=Connector_Corner_Radius, $fn = 20);
                }
            grip(includeThreading);
        }
        cylinder(d=Connector_Male_Inner_Diameter, h = 20, $fn = 50);
        cylinder(d1=Connector_Male_Outer_Diameter, d2=Connector_Male_Inner_Diameter, h = 1.5, $fn = 50);
        translate([0,0,-Connector_Length-1])
            cylinder(d=Connector_Male_Outer_Diameter, h = Connector_Length+1, $fn = 50);
        translate([0,0,-Connector_Length/2]) {
            rotate_extrude($fn = 50) {
                translate([Connector_Male_Outer_Diameter/2,0])
                    scale([1.5,1])
                    circle(d = Female_Connector_O_Ring_Thickness, $fn = 20);
            }
        }
    }
}

module gasket() {
    difference() {
        cylinder(h = Gasket_Thickness, d = Outer_Tube_Outer_Diameter, $fn = 100);
        translate([0,0,-0.5])
            cylinder(h = Gasket_Thickness+1, d = Outer_Tube_Inner_Diameter+Threading_Pitch, $fn = 50);
    }
}

// ----------------------------------------------------------------------------
function segments (diameter) = min (150, max (ceil (diameter*6), 25));

// ----------------------------------------------------------------------------
// diameter -    outside diameter of threads in mm. Default: 8.
// pitch    -    thread axial "travel" per turn in mm.  Default: 1.
// length   -    overall axial length of thread in mm.  Default: 1.
// internal -    true = clearances for internal thread (e.g., a nut).
//               false = clearances for external thread (e.g., a bolt).
//               (Internal threads should be "cut out" from a solid using
//               difference ()).  Default: false.
// n_starts -    Number of thread starts (e.g., DNA, a "double helix," has
//               n_starts=2).  See wikipedia Screw_thread.  Default: 1.
// thread_size - (non-standard) axial width of a single thread "V" - independent
//               of pitch.  Default: same as pitch.
// groove      - (non-standard) true = subtract inverted "V" from cylinder
//                (rather thanadd protruding "V" to cylinder).  Default: false.
// square      - true = square threads (per
//               https://en.wikipedia.org/wiki/Square_thread_form).  Default:
//               false.
// rectangle   - (non-standard) "Rectangular" thread - ratio depth/(axial) width
//               Default: 0 (standard "v" thread).
// angle       - (non-standard) angle (deg) of thread side from perpendicular to
//               axis (default = standard = 30 degrees).
// taper       - diameter change per length (National Pipe Thread/ANSI B1.20.1
//               is 1" diameter per 16" length). Taper decreases from 'diameter'
//               as z increases.  Default: 0 (no taper).
// leadin      - 0 (default): no chamfer; 1: chamfer (45 degree) at max-z end;
//               2: chamfer at both ends, 3: chamfer at z=0 end.
// leadfac     - scale of leadin chamfer length (default: 1.0 = 1/2 thread).
// test        - true = do not render threads (just draw "blank" cylinder).
//               Default: false (draw threads).
module metric_thread (diameter=8, pitch=1, length=1, internal=false, n_starts=1,
                      thread_size=-1, groove=false, square=false, rectangle=0,
                      angle=30, taper=0, leadin=0, leadfac=1.0, test=false)
{
   // thread_size: size of thread "V" different than travel per turn (pitch).
   // Default: same as pitch.
   local_thread_size = thread_size == -1 ? pitch : thread_size;
   local_rectangle = rectangle ? rectangle : 1;

   n_segments = segments (diameter);
   h = (test && ! internal) ? 0 : (square || rectangle) ? local_thread_size*local_rectangle/2 : local_thread_size / (2 * tan(angle));

   h_fac1 = (square || rectangle) ? 0.90 : 0.625;

   // External thread includes additional relief.
   h_fac2 = (square || rectangle) ? 0.95 : 5.3/8;

   tapered_diameter = diameter - length*taper;

   difference () {
      union () {
         if (! groove) {
            if (! test) {
               metric_thread_turns (diameter, pitch, length, internal, n_starts,
                                    local_thread_size, groove, square, rectangle, angle,
                                    taper);
            }
         }

         difference () {

            // Solid center, including Dmin truncation.
            if (groove) {
               cylinder (r1=diameter/2, r2=tapered_diameter/2,
                         h=length, $fn=n_segments);
            } else if (internal) {
               cylinder (r1=diameter/2 - h*h_fac1, r2=tapered_diameter/2 - h*h_fac1,
                         h=length, $fn=n_segments);
            } else {

               // External thread.
               cylinder (r1=diameter/2 - h*h_fac2, r2=tapered_diameter/2 - h*h_fac2,
                         h=length, $fn=n_segments);
            }

            if (groove) {
               if (! test) {
                  metric_thread_turns (diameter, pitch, length, internal, n_starts,
                                       local_thread_size, groove, square, rectangle,
                                       angle, taper);
               }
            }
         }

         // Internal thread lead-in: take away from external solid.
         if (internal) {

            // "Negative chamfer" z=0 end if leadin is 2 or 3.
            if (leadin == 2 || leadin == 3) {

               // Fixes by jeffery.spirko@tamucc.edu.
               cylinder (r1=diameter/2 - h + h*h_fac1*leadfac,
                         r2=diameter/2 - h,
                         h=h*h_fac1*leadfac, $fn=n_segments);
               /*
               cylinder (r1=diameter/2,
                         r2=diameter/2 - h*h_fac1*leadfac,
                         h=h*h_fac1*leadfac, $fn=n_segments);
               */
            }

            // "Negative chamfer" z-max end if leadin is 1 or 2.
            if (leadin == 1 || leadin == 2) {
               translate ([0, 0, length + 0.05 - h*h_fac1*leadfac]) {

                  cylinder (r1=tapered_diameter/2 - h,
                            h=h*h_fac1*leadfac,
                            r2=tapered_diameter/2 - h + h*h_fac1*leadfac,
                            $fn=n_segments);
                  /*
                  cylinder (r1=tapered_diameter/2 - h*h_fac1*leadfac,
                            h=h*h_fac1*leadfac,
                            r2=tapered_diameter/2,
                            $fn=n_segments);
                  */
               }
            }
         }
      }

      if (! internal) {

         // Chamfer z=0 end if leadin is 2 or 3.
         if (leadin == 2 || leadin == 3) {
            difference () {
               //cylinder (r=diameter/2 + 1, h=h*h_fac1*leadfac, $fn=n_segments);
               // Speed-up by Odino.
               linear_extrude (h*h_fac1*leadfac) {
                  circle(r=diameter/2 + 1, $fn=n_segments);
               }

               cylinder (r2=diameter/2, r1=diameter/2 - h*h_fac1*leadfac, h=h*h_fac1*leadfac,
                         $fn=n_segments);
            }
         }

         // Chamfer z-max end if leadin is 1 or 2.
         if (leadin == 1 || leadin == 2) {
            translate ([0, 0, length + 0.05 - h*h_fac1*leadfac]) {
               difference () {
                  //cylinder (r=diameter/2 + 1, h=h*h_fac1*leadfac, $fn=n_segments);
                  // Speed-up by Odino.
                  linear_extrude (h*h_fac1*leadfac) {
                     circle(r=diameter/2 + 1, $fn=n_segments);
                  }

                  cylinder (r1=tapered_diameter/2, r2=tapered_diameter/2 - h*h_fac1*leadfac, h=h*h_fac1*leadfac,
                            $fn=n_segments);
               }
            }
         }
      }
   }
}

// ----------------------------------------------------------------------------
module metric_thread_turns (diameter, pitch, length, internal, n_starts,
                            thread_size, groove, square, rectangle, angle,
                            taper)
{
   // Number of turns needed.
   n_turns = floor (length/pitch);

   intersection () {

      // Start one below z = 0.  Gives an extra turn at each end.
      for (i=[-1*n_starts : n_turns+1]) {
         translate ([0, 0, i*pitch]) {
            metric_thread_turn (diameter, pitch, internal, n_starts,
                                thread_size, groove, square, rectangle, angle,
                                taper, i*pitch);
         }
      }

      // Cut to length.
      //translate ([0, 0, length/2]) {
      //   cube ([diameter*3, diameter*3, length], center=true);
      //}
      // Speed-up by Odino.
      linear_extrude (length) {
         square (diameter*3, center=true);
      }
   }
}

// ----------------------------------------------------------------------------
module metric_thread_turn (diameter, pitch, internal, n_starts, thread_size,
                           groove, square, rectangle, angle, taper, z)
{
   n_segments = segments (diameter);
   fraction_circle = 1.0/n_segments;
   for (i=[0 : n_segments-1]) {

      // Keep polyhedron "facets" aligned -- circumferentially -- with base
      // cylinder facets.  (Patch contributed by rambetter@protonmail.com.)
      rotate ([0, 0, (i + 0.5)*360*fraction_circle + 90]) {
         translate ([0, 0, i*n_starts*pitch*fraction_circle]) {
            //current_diameter = diameter - taper*(z + i*n_starts*pitch*fraction_circle);
            thread_polyhedron ((diameter - taper*(z + i*n_starts*pitch*fraction_circle))/2,
                               pitch, internal, n_starts, thread_size, groove,
                               square, rectangle, angle);
         }
      }
   }
}

// ----------------------------------------------------------------------------
module thread_polyhedron (radius, pitch, internal, n_starts, thread_size,
                          groove, square, rectangle, angle)
{
   n_segments = segments (radius*2);
   fraction_circle = 1.0/n_segments;

   local_rectangle = rectangle ? rectangle : 1;

   h = (square || rectangle) ? thread_size*local_rectangle/2 : thread_size / (2 * tan(angle));
   outer_r = radius + (internal ? h/20 : 0); // Adds internal relief.
   //echo (str ("outer_r: ", outer_r));

   // A little extra on square thread -- make sure overlaps cylinder.
   h_fac1 = (square || rectangle) ? 1.1 : 0.875;
   inner_r = radius - h*h_fac1; // Does NOT do Dmin_truncation - do later with
                                // cylinder.

   translate_y = groove ? outer_r + inner_r : 0;
   reflect_x   = groove ? 1 : 0;

   // Make these just slightly bigger (keep in proportion) so polyhedra will
   // overlap.
   x_incr_outer = (! groove ? outer_r : inner_r) * fraction_circle * 2 * PI * 1.02;
   x_incr_inner = (! groove ? inner_r : outer_r) * fraction_circle * 2 * PI * 1.02;
   z_incr = n_starts * pitch * fraction_circle * 1.005;

   /*
    (angles x0 and x3 inner are actually 60 deg)

                          /\  (x2_inner, z2_inner) [2]
                         /  \
   (x3_inner, z3_inner) /    \
                  [3]   \     \
                        |\     \ (x2_outer, z2_outer) [6]
                        | \    /
                        |  \  /|
             z          |[7]\/ / (x1_outer, z1_outer) [5]
             |          |   | /
             |   x      |   |/
             |  /       |   / (x0_outer, z0_outer) [4]
             | /        |  /     (behind: (x1_inner, z1_inner) [1]
             |/         | /
    y________|          |/
   (r)                  / (x0_inner, z0_inner) [0]

   */

   x1_outer = outer_r * fraction_circle * 2 * PI;

   z0_outer = (outer_r - inner_r) * tan(angle);
   //echo (str ("z0_outer: ", z0_outer));

   //polygon ([[inner_r, 0], [outer_r, z0_outer],
   //        [outer_r, 0.5*pitch], [inner_r, 0.5*pitch]]);
   z1_outer = z0_outer + z_incr;

   // Give internal square threads some clearance in the z direction, too.
   bottom = internal ? 0.235 : 0.25;
   top    = internal ? 0.765 : 0.75;

   translate ([0, translate_y, 0]) {
      mirror ([reflect_x, 0, 0]) {

         if (square || rectangle) {

            // Rule for face ordering: look at polyhedron from outside: points must
            // be in clockwise order.
            polyhedron (
               points = [
                         [-x_incr_inner/2, -inner_r, bottom*thread_size],         // [0]
                         [x_incr_inner/2, -inner_r, bottom*thread_size + z_incr], // [1]
                         [x_incr_inner/2, -inner_r, top*thread_size + z_incr],    // [2]
                         [-x_incr_inner/2, -inner_r, top*thread_size],            // [3]

                         [-x_incr_outer/2, -outer_r, bottom*thread_size],         // [4]
                         [x_incr_outer/2, -outer_r, bottom*thread_size + z_incr], // [5]
                         [x_incr_outer/2, -outer_r, top*thread_size + z_incr],    // [6]
                         [-x_incr_outer/2, -outer_r, top*thread_size]             // [7]
                        ],

               faces = [
                         [0, 3, 7, 4],  // This-side trapezoid

                         [1, 5, 6, 2],  // Back-side trapezoid

                         [0, 1, 2, 3],  // Inner rectangle

                         [4, 7, 6, 5],  // Outer rectangle

                         // These are not planar, so do with separate triangles.
                         [7, 2, 6],     // Upper rectangle, bottom
                         [7, 3, 2],     // Upper rectangle, top

                         [0, 5, 1],     // Lower rectangle, bottom
                         [0, 4, 5]      // Lower rectangle, top
                        ]
            );
         } else {

            // Rule for face ordering: look at polyhedron from outside: points must
            // be in clockwise order.
            polyhedron (
               points = [
                         [-x_incr_inner/2, -inner_r, 0],                        // [0]
                         [x_incr_inner/2, -inner_r, z_incr],                    // [1]
                         [x_incr_inner/2, -inner_r, thread_size + z_incr],      // [2]
                         [-x_incr_inner/2, -inner_r, thread_size],              // [3]

                         [-x_incr_outer/2, -outer_r, z0_outer],                 // [4]
                         [x_incr_outer/2, -outer_r, z0_outer + z_incr],         // [5]
                         [x_incr_outer/2, -outer_r, thread_size - z0_outer + z_incr], // [6]
                         [-x_incr_outer/2, -outer_r, thread_size - z0_outer]    // [7]
                        ],

               faces = [
                         [0, 3, 7, 4],  // This-side trapezoid

                         [1, 5, 6, 2],  // Back-side trapezoid

                         [0, 1, 2, 3],  // Inner rectangle

                         [4, 7, 6, 5],  // Outer rectangle

                         // These are not planar, so do with separate triangles.
                         [7, 2, 6],     // Upper rectangle, bottom
                         [7, 3, 2],     // Upper rectangle, top

                         [0, 5, 1],     // Lower rectangle, bottom
                         [0, 4, 5]      // Lower rectangle, top
                        ]
            );
         }
      }
   }
}

if (Part == "AllFemale" || Part == "AllMale") {
    translate([-(Outer_Tube_Outer_Diameter+End_Cap_Grip_Cutout_Diameter)/2-1,0,Connector_Length])
        muffler_base();
    translate([0,sqrt(((Outer_Tube_Outer_Diameter+End_Cap_Grip_Cutout_Diameter+Inner_Tube_Diameter)/2+2)^2-((Outer_Tube_Outer_Diameter+End_Cap_Grip_Cutout_Diameter)/2+1)^2), 0])
        inner_tube();
    translate([(Outer_Tube_Outer_Diameter+End_Cap_Grip_Cutout_Diameter)/2+1,0,Connector_Length])
        if (Part == "AllMale")
            end_cap_male(true);
        else
            end_cap_female(true);
} else if (Part == "Combined") {
    muffler_base();
    translate([0,0,End_Cap_Thickness-End_Cap_Recess_For_Inner_Tube])
        inner_tube();
    translate([0,0,Muffler_Length])
        rotate([180,0,0])
            end_cap_male(true);
} else if (Part == "MufflerBase") {
    muffler_base();
} else if (Part == "InnerTube") {
    inner_tube();
} else if (Part == "EndCapFemale") {
    end_cap_female(true);
} else if (Part == "EndCapMale") {
    end_cap_male(true);
} else if (Part == "Gasket") {
    gasket();
}