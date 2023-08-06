''' A python script to generate input files for the Ewald code '''

# Import modules 
from .input import FileReader, FileWriter
import re
import os
import scipy as sp
import numpy as np
from textwrap import dedent

# Define the class

class Ewald():
    def __init__(self, atom, Exp_a, Exp_b, Exp_c):
        self.atom = atom
        self.Exp_a = Exp_a
        self.Exp_b = Exp_b
        self.Exp_c = Exp_c

    def translate_unit_cell(self):
        # Read the POSCAR containing the unit cell
        unit_cell = FileReader('POSCAR')
        name, a, b, c, elements, num_elements, coordinates = unit_cell.read_poscar()
        num_elements = [int(i) for i in num_elements]

        # Split the atom into symbol and index
        atom = re.split('(\d+)', self.atom)

        # Calculate the number of atoms in previous 
        for index, symbol in enumerate(elements):
            if symbol == atom[0]:
                atom_index = index

        previous_atoms = sum(num_elements[:atom_index])

        # Locate the coordiantes of the atom
        atom_location = coordinates[previous_atoms + int(atom[1]) - 1]

        # Caluculate the destination 
        destination = np.float_([
                [0.5, 0, 0],
                [0, 0.5, 0],
                [0, 0, 0.5]
                ])

        if int(self.Exp_a) %2 == 0:
            destination[0] = [0, 0, 0]
        if int(self.Exp_b) %2 == 0:
            destination[1] = [0, 0, 0]
        if int(self.Exp_c) %2 == 0:
            destination[2] = [0, 0, 0]

        destination = destination.sum(axis=0)

        # Caluclate the translation vector 
        translation = atom_location - destination 
        
        # Translate the unit_cell
        coordinates = coordinates - translation
        coordinates %= 1

        os.system('cp POSCAR POSCAR_unit_cell')

        poscar = FileWriter(name, a, b, c, elements, num_elements, coordinates)
        poscar.write_poscar()

    def calculate_potential(self, n, alpha, charges, r_cut, iter, steps, bound_inc, bound, qm):
        print(f'''
------------------------------------------------------------------------
                       UNIT CELL INFORMATION
------------------------------------------------------------------------
''')

        # Read the translated unit cell
        poscar = FileReader('POSCAR')
        name, a1, a2, a3, elements, num_elements, coordinates = poscar.read_poscar()
        
        # read the charge file 
        with open(charges, 'r') as f:
            charges = []
            symbols = []
            for lines in f:
                stripped_lines = lines.strip()
                split_lines = stripped_lines.split()
                charges.append(split_lines[0])
                symbols.append(split_lines[1])


        # Insert the charges into the coordinates
        coordinates, charges = np.float_(coordinates), np.float_(charges)
        coordinates = np.insert(coordinates, 3, charges, axis=1)

        # Print unit cell and charges 
        print('''Unit cell:
     X               Y               Z            q''')
        for i in range(len(coordinates)):
                       print(f'''{coordinates[i,0]:.10f}   {coordinates[i,1]:.10f}   {coordinates[i,2]:.10f}   {coordinates[i,3]:.10f}   {symbols[i]}''')

        # Compute expansions of the unit cell 
        n = [int(i) for i in n]
        n1 = list(range(-n[0], n[0] + 1))
        n2 = list(range(-n[1], n[1] + 1))
        n3 = list(range(-n[2], n[2] + 1))

        evconv = 14.399645

        # Compute the cell volume 
        V = a1@np.cross(a2,a3)

        a_v = np.float_([a1, a2, a3])

        b_v = np.float_([
            np.cross(a2, a3)/V,
            np.cross(a3, a1)/V,
            np.cross(a1, a2)/V
            ])

        b1, b2, b3 = b_v

        # Compute the real space lattice lengths 
        a1_len = np.linalg.norm(a1)
        a2_len = np.linalg.norm(a2)
        a3_len = np.linalg.norm(a3)

        print(f'''
Lattice vectors:
a1 = {a1[0]:.10f} {a1[1]:.10f} {a1[2]:.10f}
a2 = {a2[0]:.10f} {a2[1]:.10f} {a2[2]:.10f}
a3 = {a3[0]:.10f} {a3[1]:.10f} {a3[2]:.10f}

Reciprocal lattice vectors:
b1 = {b1[0]:.10f} {b1[1]:.10f} {b1[2]:.10f}
b2 = {b2[0]:.10f} {b2[1]:.10f} {b2[2]:.10f}
b3 = {b3[0]:.10f} {b3[1]:.10f} {b3[2]:.10f}

Unit cell volume = {V:.10f} Å^3

Unit cell charge = {coordinates[:,3].sum():.10f}
''')

        print(f'''
------------------------------------------------------------------------
                             EWALD SUMMATION
                           EXPANSION {n[0]*2+1} x {n[1]*2+1} x {n[2]*2+1}
                       Total number of atoms = {len(coordinates)*(n[0]*2+1) * (n[1]*2+1) * (n[2]*2+1)}
                               Alpha = {alpha}
------------------------------------------------------------------------
''')

        # Compute the reciprocal unit cell expansions, m 
        m1 = [i for i in n1 if i != 0]
        m2 = [i for i in n2 if i != 0]
        m3 = [i for i in n3 if i != 0]

        # Compute the ewald sum for each atom 

        Ewald_sum_ri = []
        Direct_sum_ri = []
        Ewald_direct = []
        for i in range(len(coordinates)):
            ri = (coordinates[i, :3]*a_v).sum(axis=1) 
            real_space_potential = 0
            reciprocal_space_potential = 0
            direct_sum = 0
            ewald_c = 0
            for j in range(len(coordinates)):
                for n_1 in n1:
                    for n_2 in n2:
                        for n_3 in n3:
                            rj = (coordinates[j,:3] + n_1)*a1 + (coordinates[j,:3] + n_2)*a2 + (coordinates[j,:3] + n_3)*a3 
                            if np.allclose(ri, rj,rtol=1e-06):
                                continue
                            else:
                                rij = np.linalg.norm(ri - rj)
                                direct_sum += evconv*coordinates[j,3]/ np.linalg.norm(ri - rj)
                                real_space_potential += evconv * coordinates[j, 3] * sp.special.erfc( alpha * rij)/rij

                sum_m_potential = 0
                for m_1 in m1:
                    for m_2 in m2:
                        for m_3 in m3:
                            rj0 = (coordinates[j,:3]*a_v).sum(axis=1) 
                            if np.allclose(ri, rj0, rtol=1e-06):
                                continue
                            else:
                                rij0 = ri - rj 
                                fm = np.float_([m_1, m_2, m_3])@b_v
                                sum_m_potential += np.exp(-((np.pi**2 * fm@fm)/alpha**2))/fm@fm * np.cos((2*np.pi*fm)@rij0)
                reciprocal_space_potential = coordinates[j,3] * sum_m_potential
            ewald_c = -evconv * 2. * alpha * coordinates[i,3]/ np.sqrt(np.pi)
            reciprocal_space_potential *= evconv/(np.pi*V)
            ewald_sum = real_space_potential + reciprocal_space_potential + ewald_c
            Ewald_direct.append(ewald_sum - direct_sum)
            Ewald_sum_ri.append(ewald_sum)
            Direct_sum_ri.append(direct_sum)
            print(dedent(f'''{symbols[i]}:
Real space potential = {real_space_potential:.10f}
Reciprocal space potential = {reciprocal_space_potential:.10f}
Correction = {ewald_c:.10f}
Ewald sum = {Ewald_sum_ri[i]:.10f}
Direct sum = {Direct_sum_ri[i]:.10f}
'''))
        Ewald_direct = np.float_(Ewald_direct)

        # Compute the delta_rms
        delta_rms = np.sum([i**2 for i in Ewald_direct])/len(Ewald_direct)

        print(f'''
(Ewald - Direct) potential avereage = {np.sum(Ewald_direct)/len(Ewald_direct):.10f}
delta  RMS = {delta_rms:.10f}''')
        coordinates = np.insert(coordinates, 4, Ewald_sum_ri, axis=1)

        # Build the supercell 
        a_list = list(range(self.Exp_a))
        b_list = list(range(self.Exp_b))
        c_list = list(range(self.Exp_c))
        supercell = [[coordinates[i,0]+(1*exp_a), coordinates[i,1]+(1*exp_b), coordinates[i,2]+(1*exp_c), coordinates[i,3], coordinates[i,4], symbols[i]] for i in range(len(coordinates)) for exp_a in a_list for exp_b in b_list for exp_c in c_list]
        supercell = np.array(supercell)
        supercell = np.unique(supercell, axis=0)
        supercell = supercell[supercell[:,5].argsort()]

        # Supercell lattice vectors 
        a1 = a1*self.Exp_a 
        a2 = a2*self.Exp_b 
        a3 = a3*self.Exp_c

        # Normalize the coordinates to origin 
        for i in range(len(supercell)):
            supercell[i,0] = float(supercell[i,0])/float(self.Exp_a)-0.5
            supercell[i,1] = float(supercell[i,1])/float(self.Exp_b)-0.5 
            supercell[i,2] = float(supercell[i,2])/float(self.Exp_c)-0.5

        cartesian_coordinates = [[np.float_(i[0])*np.float_(a1) + np.float_(i[1])*np.float_(a2) + np.float_(i[2])*np.float_(a3), i[3], i[4], i[5]] for i in supercell]
        cartesian_coordinates = [[i[0][0], i[0][1], i[0][2], i[1], i[2], i[3]] for i in cartesian_coordinates]
        cartesian_coordinates = np.array(cartesian_coordinates)


        S_V = a1@np.cross(a2,a3)

        print(f'''
------------------------------------------------------------------
              {self.Exp_a} x {self.Exp_b} x {self.Exp_c} SUPERCELL CONSTRUCTED
------------------------------------------------------------------
Lattice Vectors:
a1 = {a1[0]:.10f} {a1[1]:.10f} {a1[2]:.10f}
a2 = {a2[0]:.10f} {a2[1]:.10f} {a2[2]:.10f}
a3 = {a3[0]:.10f} {a3[1]:.10f} {a3[2]:.10f}

Supercell volume =  {S_V:.10f} Å^3

Supercell charge = {np.sum(np.float_(supercell[:,3])):.10f}

Number of atoms in supercell = {len(supercell)}''')

        # read qm region 
        with open(qm, 'r') as f:
            qm_coordinates = np.array([lines.split() for lines in f.readlines()[2:]])
            qm_coordinates = np.float_(qm_coordinates[:,1:])

        sphere_coordinates = [list(i) for i in cartesian_coordinates if np.linalg.norm(i[:3]) < r_cut] 
        parameter_coordinates = [list(i) for i in cartesian_coordinates if np.linalg.norm(i[:3]) > r_cut]
        sphere_coordinates = np.array(sphere_coordinates)
        parameter_coordinates = np.array(parameter_coordinates)


        # remove qm region from sphere coordinates 
        for i in range(len(qm_coordinates)):
            for j in range(len(sphere_coordinates)-1): 
                if np.allclose(float(qm_coordinates[i,0]), float(sphere_coordinates[j,0])) and np.allclose(float(qm_coordinates[i,1]), float(sphere_coordinates[j,1])) and np.allclose(float(qm_coordinates[i,2]), float(sphere_coordinates[j,2])):
                    sphere_coordinates = np.delete(sphere_coordinates, j, axis=0)


        print(f'''Number of atoms in QM region = {len(qm_coordinates)}
Number of atoms in sphere = {len(sphere_coordinates)}
Number of atoms in parameter region = {len(parameter_coordinates)}''')

        print(f'''
------------------------------------------------------------------
            || A x = b || MATRIX, VECTOR CONSTRUCTION
------------------------------------------------------------------
''')

        sphere_charge = np.sum(np.float_(sphere_coordinates[:,3]))
        print(f'''Sum of sphere charges = {sphere_charge}''')

        bi = sphere_coordinates[:,4]

        print(f'''Constructing A matrix and b vector for parameter fitting''')
        print(f'''||A x = b||''')
        A = 1/sp.spatial.distance.cdist(np.float_(sphere_coordinates[:,:3]), np.float_(parameter_coordinates[:,:3]), metric='euclidean') 
        Pij = sp.spatial.distance.squareform(1/sp.spatial.distance.pdist(np.float_(sphere_coordinates[:,:3]), metric='euclidean'))
        P = Pij@(evconv*np.float_(sphere_coordinates[:,3]))

        bi = np.float_(bi) - np.float_(P)
        A = np.float_(A)
        print(f'''Complete\n''')

        print('Computing QR decomposition')
        c = np.ones((1, len(parameter_coordinates)))

        d = -(np.sum(np.float_(sphere_coordinates[:,3])))

        # Create d target vector such that the sum of the parmater charges is negative the sum of the sphere charges 

        Q,R = np.linalg.qr(c.T, mode='complete')

        AQ = A@Q

        b2 = bi - AQ[:,0]*((1/R[0].T)*d)

        print('Complete\n')

        lb, ub = -bound, bound


        print(f'''
------------------------------------------------------------------
                         PARAMETER FITTING
                   (scipy.optimize.lsq_linear)
                   MAXIMUM ITERATIONS = {iter}
                      MAXIMUM STEPS = {steps}
------------------------------------------------------------------
''')
        #x2 = np.linalg.lstsq(AQ[:,1:], bi, rcond=None)[0]
        success = False 
        number = 1
        while success == False:
            print(f'''
Step {number}
Lower bound = {lb}
Upper bound = {ub}
''') 
            x2 = sp.optimize.lsq_linear(AQ[:,1:], b2, bounds=(lb,ub), verbose=2, max_iter=iter)
            print(x2)
            if x2.success == True:
                if x2.optimality > 1e-5:
                    print(f'''
------------------------------------------------------------------
##################################################################
------------------------------------------------------------------
                          !!!WARNING!!!
                    OPTIMALITY CRITERION NOT MET 
                      USING ITERATIVE METHODS

                        SOLVING ANALYTICALLY
                        (numpy.linalg.lstsq)
------------------------------------------------------------------
##################################################################
------------------------------------------------------------------
''')
                    x2 = np.linalg.lstsq(AQ[:,1:], b2, rcond=None)[0]
                    success = True
                else:
                    success = True
                    x2 = x2.x
            else:
                ub -= bound_inc
                number += 1
            if number > int(steps):
                x2 = np.linalg.lstsq(AQ[:,1:], b2, rcond=None)[0]
                success = True
                print(f'''
------------------------------------------------------------------
##################################################################
------------------------------------------------------------------
                        !!!WARNGING!!!
        A LEAST SQUARES OPTIMAL SOLUTION WAS NOT ACHIEVED
                    WITHIN BOUNDS {lb} - {ub}

                    SOLVING ANALYTICALLY
                    (numpy.linalg.lstsq)
------------------------------------------------------------------
##################################################################
------------------------------------------------------------------
    ''')
        x1 = (1/R[0].T)*d
        x = np.concatenate((x1, x2))

        x = Q@x

        print('\nSum of parameter charges = ', np.sum(x))
        print('sum of sphere charges + sum of paramter charges = ', np.sum(np.float_(sphere_coordinates[:,3])) + np.sum(x))

        rijp = 1/sp.spatial.distance.cdist(np.float_(sphere_coordinates[:,:3]), np.float_(parameter_coordinates[:,:3]), metric='euclidean') 
        parameter_potential = rijp@x
        rijs = sp.spatial.distance.squareform(1/sp.spatial.distance.pdist(np.float_(sphere_coordinates[:,:3]), metric='euclidean'))
        sphere_potential = evconv*np.float_(sphere_coordinates[:,3])@rijs
        temp2 = np.float_(np.float_(sphere_coordinates[:,4])) - (sphere_potential + parameter_potential)
        delta_rms = np.sqrt(np.sum(np.square(temp2))/len(temp2))
        print('Delta RMS = ', delta_rms)

        # output 
        with open(f'''{''.join(name)}_sphere.xyz''', 'w') as f:
            f.write(f'''{len(sphere_coordinates)}
\n''')
            for i in range(len(sphere_coordinates)):
                f.write(f'''{sphere_coordinates[i,5]} {sphere_coordinates[i,0]} {sphere_coordinates[i,1]} {sphere_coordinates[i,2]}
''')
        
        with open(f'''{''.join(name)}_parameter.xyz''', 'w') as f:
            f.write(f'''{len(parameter_coordinates)}
\n''')
            for i in range(len(parameter_coordinates)):
                f.write(f'''{parameter_coordinates[i,5]} {parameter_coordinates[i,0]} {parameter_coordinates[i,1]} {parameter_coordinates[i,2]}
''')

        with open('ewald.out', 'w') as f:
            for i in range(len(sphere_coordinates)):
                f.write(f'''{float(sphere_coordinates[i,0])}   {float(sphere_coordinates[i,1])}   {float(sphere_coordinates[i,2])}   {float(sphere_coordinates[i,3])}
''')
            for i in range(len(parameter_coordinates)):
                f.write(f'''{float(parameter_coordinates[i,0])}   {float(parameter_coordinates[i,1])}   {float(parameter_coordinates[i,2])}   {x[i]}
''')

def ewald_potential(atom, expansion, n, charges, r_cut, iter, steps, bound_inc, bound, qm):
    ewald = Ewald(atom, expansion[0], expansion[1], expansion[2])
    ewald.translate_unit_cell()
    ewald.calculate_potential(n, 0.2, charges, r_cut, iter, steps, bound_inc, bound, qm)
