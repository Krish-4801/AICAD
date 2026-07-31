import math
from build123d import *

def gen_step():
    flange_width = 80.0
    flange_thickness = 8.0
    flange_hole_dist = 60.0
    flange_hole_diam = 6.0
    
    barrel_outer_diam = 50.0
    barrel_inner_diam = 38.0
    barrel_height = 90.0
    
    fin_outer_diam = 75.0
    fin_thickness = 2.0
    num_fins = 12
    
    cap_thickness = 10.0
    
    boss_angle = 35.0
    boss_outer_diam = 18.0
    boss_inner_diam = 10.0
    boss_length = 15.0
    
    with BuildPart() as part:
        with BuildSketch(Plane.XY):
            RectangleRounded(flange_width, flange_width, 8.0)
            with Locations((flange_hole_dist/2, flange_hole_dist/2),
                           (flange_hole_dist/2, -flange_hole_dist/2),
                           (-flange_hole_dist/2, flange_hole_dist/2),
                           (-flange_hole_dist/2, -flange_hole_dist/2)):
                Circle(flange_hole_diam/2, mode=Mode.SUBTRACT)
        extrude(amount=flange_thickness)
        
        with BuildSketch(Plane(origin=(0, 0, flange_thickness))):
            Circle(barrel_outer_diam/2)
        extrude(amount=barrel_height)
        
        with BuildSketch(Plane(origin=(0, 0, flange_thickness + barrel_height))):
            Circle(barrel_outer_diam/2)
        extrude(amount=cap_thickness)
        
        z_start = flange_thickness + 5.0
        z_end = flange_thickness + barrel_height - 5.0
        fin_spacing = (z_end - z_start) / (num_fins - 1) if num_fins > 1 else 0
        
        for i in range(num_fins):
            z_pos = z_start + i * fin_spacing
            with BuildSketch(Plane(origin=(0, 0, z_pos))):
                Circle(fin_outer_diam/2)
            extrude(amount=fin_thickness)
            
        with BuildSketch(Plane.XY):
            Circle(barrel_inner_diam/2)
        extrude(amount=flange_thickness + barrel_height + cap_thickness - 6.0, mode=Mode.SUBTRACT)
        
        top_z = flange_thickness + barrel_height + cap_thickness
        boss_plane = Plane(Location((0, 0, top_z), (0, boss_angle, 0)))
        
        with BuildSketch(boss_plane):
            Circle(boss_outer_diam/2)
        extrude(amount=boss_length)
        with BuildSketch(boss_plane):
            Circle(boss_outer_diam/2)
        extrude(amount=-15)
        
        with BuildSketch(boss_plane):
            Circle(boss_inner_diam/2)
        extrude(amount=boss_length + 5, mode=Mode.SUBTRACT)
        with BuildSketch(boss_plane):
            Circle(boss_inner_diam/2)
        extrude(amount=-30, mode=Mode.SUBTRACT)
        
    part.part.label = "engine_cylinder"
    return part.part

if __name__ == "__main__":
    part = gen_step()
