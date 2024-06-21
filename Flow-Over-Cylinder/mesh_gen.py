import numpy as np
import re
from collections import OrderedDict
"""
Mesh generation script for cylinder 
"""

__author__ = "Trey Gower, David Valenzano, Ty Zimmerman"


def params():
    """ 
    enter paramters for cylinder
    """
    Lw = 0
    H =0
    Lf =0
    #we will always have 64 vertices
    n = 64
    r = .5

    while H < (3*(r*2)): 
        H = float(input('Enter H: '))
        if H < 3*(r*2):
            print('Height boundary must be 3 diameters away')

    while Lw < (3*(r*2)): 
        Lw = float(input('Enter Lw: ')) 
        if Lw < 3*(r*2):
            print('Wake boundary must be 3 diameters away')

    while Lf < (3*(r*2)): 
        Lf= float(input('Enter Lf: ')) 
        if Lf < 3*(r*2):
            print('Fore boundary must be 3 diameters away')

    return n, Lf, Lw, r, H

def arc_adjust(R):
    """
    Adjust arc midpoints based on radius
    """
    r = .5
    #Assemble inner radius r
    arc_points = np.zeros((8, 2))
    theta = 22.5
    for i in range(8):
        arc_x = r * np.cos(np.deg2rad(theta))
        arc_y = r * np.sin(np.deg2rad(theta))

        arc_points[i, :] = [arc_x, arc_y]
        theta += 45

    #Assemble outer radius R
    arc_pointsR = np.zeros((8, 2))
    theta = 22.5
    for i in range(8):
        arc_xR = R * np.cos(np.deg2rad(theta))
        arc_yR = R * np.sin(np.deg2rad(theta))

        arc_pointsR[i, :] = [arc_xR, arc_yR]
        theta += 45
    
    zvec = np.zeros((16,1))
    zvec[:]= -.005
    arc_points = np.vstack((arc_points,arc_pointsR))
    arc_points = np.column_stack((arc_points,zvec))
    arc_points = np.vstack((arc_points,arc_points))
    arc_points[16:,2] = .005

    circle_label = np.arange(8)
    circle_label = np.vstack((circle_label,np.arange(8,16)))
    circle_label = np.vstack((circle_label,np.arange(32,40)))
    circle_label = np.vstack((circle_label,np.arange(40,48)))

    #Formating
    formatted_arcs = ''
    for row in range(len(arc_points[:, 0])):
        if row % 8 != 7:
            formatted_arc = f"arc {circle_label[row // 8][row % 8]} {circle_label[row // 8][row % 8 + 1]} ({arc_points[row][0]: .5e}  {arc_points[row][1]: .5e} {arc_points[row][2]: .5e})\n"
            formatted_arcs += formatted_arc
        else:
            formatted_arc = f"arc {circle_label[row // 8][7]} {circle_label[row // 8][0]} ({arc_points[row][0]: .5e}  {arc_points[row][1]: .5e} {arc_points[row][2]: .5e})\n"
            formatted_arcs += formatted_arc
               
    return formatted_arcs

def generate_vertices(n,r,H,Lf,Lw):
   #R is outer radius
    R = input("Outer Radius: ")
    R = float(R)
    if R == "n":
        R = 2*r
    # Generate vertices around the circumference of inner cylinder
    #We want 8 vertices around each block so n//8
    z= .05
    angles = np.linspace(0, 2*np.pi, n//8, endpoint=False)
    x = r * np.cos(angles)
    y = r * np.sin(angles)
    zvec = np.zeros_like(x)  # Assuming the inner cylinder is at z = 0
    zvec[:] = -.05
    inner_vertices = np.column_stack((x, y, zvec))
    outer_vertices = inner_vertices.copy()
    outer_vertices[:, 1] = R*np.sin(angles[:])  # Offset y coordinates by y component
    outer_vertices[:, 0] = R*np.cos(angles[:])  # Offset x coordinates by x component

    vertices = np.concatenate((inner_vertices, outer_vertices), axis=0)
    vertices = np.concatenate((vertices, np.zeros((n//4,3))), axis=0)

    #Manually entering the first quadrant
    #point 16
    vertices[16,0] = Lw 
    vertices[16, 1] = vertices[0,1]
    vertices[16, 2] = -z 
    #point 17
    vertices[17,0] = Lw
    vertices[17, 1] = vertices[9,1]
    vertices[17, 2] = -z  
    #point 19
    vertices[19,0] = vertices[9,0]
    vertices[19, 1] = H
    vertices[19, 2] = -z 
    #point 18
    vertices[18,0] =  vertices[17, 0]
    vertices[18, 1] = H
    vertices[18, 2] = -z  
    #point 20
    vertices[20,0] = 0
    vertices[20, 1] = H
    vertices[20, 2] = -z  
    
    #point 21
    vertices[21,0] = -vertices[11,1] 
    vertices[21, 1] = H
    vertices[21, 2] = -z 
    #point 22
    vertices[22,0] = -Lf
    vertices[22, 1] = H
    vertices[22, 2] = -z  
    #point 23
    vertices[23,0] = -Lf
    vertices[23, 1] = vertices[11,1] 
    vertices[23, 2] = -z  
    #point 24
    vertices[24,0] =  -Lf
    vertices[24, 1] = 0
    vertices[24, 2] = -z  
    j=1
    for i in range(25, 32, 1):
        vertices[i,0] = vertices[i-(2*j),0]
        vertices[i,1] = -vertices[i-(2*j),1]
        vertices[i,2] = -z
        j +=1;
    vertices = np.concatenate((vertices, vertices), axis=0)
    vertices[32:, 2] = -vertices[32:,2]
    return vertices, R

def grading(lines):
    """
    Serves to adjust the grading of the mesh
    """
    #preserve the template
    org_data = lines
    block = ""
    new_values = ""
    yorn = None
    while block != 'done' and block != 'd':
        block = ""
        while not block.isdigit() or int(block) >= 20:
            block = input("Input the block to change grading of: ")
            if block == 'done' or block == 'd':
                break

            if not block.isdigit() or int(block) >= 20:
                print("Invalid block number. Please enter an integer less than 20.")
                continue
        if block == 'done' or block == 'd':
            break


        #Finds Pattern for a given block
        for i in range(len(org_data)):
            if f'   // block {block}\n' == org_data[i]:
                print('Current Block org_data:\n' + lines[i+1])
                print(f'Enter desired grading along x or y for block {block}')
                x = input('x grade: ')
                y = input('y grade: ')
                yorn = input('would you like to change simple grading too (y/n)? ')
                
                #Adjusting simple grading
                if yorn == 'y':
                    simplegrade_pattern = r'\(\s*(\d+\.\d+e[+-]\d+)\s+(\d+\.\d+e[+-]\d+)\s+(\d+\.\d+)\s*\)'
                    # Search for the pattern in the line
                    match_simple = re.search(simplegrade_pattern, org_data[i+1])
                    simple_x = input('simple x grade (or type (s) to keep it the same): ')
                    simple_y = input('simple y grade (or type (s) to keep it the same): ')
                    dim_simple = match_simple.groups()

                    if simple_x == 's':
                        simple_x = dim_simple[0]
                    if simple_y == 's':
                        simple_y = dim_simple[1]
                    simple_newvals = f'({float(simple_x): .5e} {float(simple_y): .5e} {1.0})'
                    pat_simple = f' ( {dim_simple[0]}  {dim_simple[1]} 1.0)'
                
                new_values = f'{x} {y} {1}'
                grade_pattern = r'\(\s*(\d+)\s+(\d+)\s+(\d+)\s*\)'
                # Search for the pattern in the line
                match = re.search(grade_pattern, org_data[i+1])

                dim = match.groups()
                pat = f'({dim[0]} {dim[1]} 1)'
                break
        # Go through the file again and replace all matching patterns
        print('Grading Selected and Bordering Blocks:')
        for j in range(len(org_data)):
            if re.search(pat, org_data[j]):
                # Attempt to identify the block number for reporting
                if j > 0 and 'block' in org_data[j-1]:
                    print(org_data[j-1].strip()[3:])
                if yorn == 'y':
                    lines[j] = re.sub(simplegrade_pattern, simple_newvals, org_data[j])
                lines[j] = re.sub(pat, new_values, org_data[j])
    
    
    return lines

def mesh_file(vertices, R):
    """ 
    saves the mesh in an openfoam readable format based on the example given
    """
    formatted_string = "   ("
    i = 0
    for row in vertices:
        formatted_string += " ".join([f"{val: .16e}" for val in row]) + f") // {i}\n   ("
        i += 1;
    formatted_string = formatted_string[:-2]  # Remove the extra "( " at the end

    #Modifing a specific template and saving as a new output
    
    contents_to_modify = {'vert_template': '   ( 7.0710678118654735e-01 -7.0710678118654768e-01 -5.0000000000000003e-02) // 15',
                          'edge_template': 'arc 0 1 ( 4.61940e-01  1.91342e-01 -5.00000e-02)'}
    
    index = 0;
    
    with open("./blockMeshDict1.template", "r") as file:
        lines = file.readlines()
    
    #inserts formatted string of vertices
    for i, line in enumerate(lines):
        if contents_to_modify['vert_template'] in line:
            lines[i] = formatted_string
            break

    #Adjust grading
    yorn = None
    while yorn != 'y' or yorn != 'n':
        yorn = input('Would you like to change Resolution? (y/n): ')
        if yorn == 'y':
            lines = grading(lines)
            break
        if yorn == 'n':
            break
        else: 
            print('enter y or n')
    #Outer radius arc adjustment
    '''
    formatted_arc = arc_adjust(R)
    for i, line in enumerate(lines):
        if contents_to_modify['edge_template'] in line:
            lines[i] = formatted_arc
            break
    '''
    
    meshlet = input("Enter a Letter to name the mesh with: ")
# Write the modified lines back to the file
    with open(f"./blockMeshDict_{meshlet}", "w") as file:
        file.writelines(lines)
    print("\n**************\n")
    print(f"Mesh blockMeshDict_{meshlet} has been generated\n")
    print("**************\n")

def main():
    """ Main entry vertices  """
n, Lf, Lw, r, H = params()
vertices, R = generate_vertices(n,r,H,Lf,Lw)
mesh_file(vertices,R)

if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()