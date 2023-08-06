'''
A module for the Structure class. Structure will perform operations structure data files.
'''
 # Imports 
import re
import os
import numpy as np 
import scipy as sp 
from functools import wraps 
from time import perf_counter

def timer(func):
    '''
    A decorator function to time functions.
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        print(f'Running {func.__name__}...')
        func(*args, *kwargs)
        end = perf_counter()
        print(f"Time elapsed: {end - start}") 
    return wrapper

class Structure(): 
    '''
    A class of functions for manipulating structure data files. 
    '''
    def __init__(self, filename: str):
        '''
        Initializes the Structure class.
        '''
        self.filename = filename

    def Vasp_reader(self):
       '''
       Reads and formats a .vasp, POSCAR or CONTCAR file. 
       '''
       # Obtain the data 
       with open(self.filename) as f:
           data = f.readlines()
       data = [x.strip().split() for x in data]

       self.name: str  = data[0][0]
       self.scale: float = data[1][0]
       self.av: np.ndarray = np.array(data[2:5], dtype=float)
       self.atoms: list = data[5] 
       self.natoms: list = [int(x) for x in data[6]]
       self._N: int = sum(self.natoms)
       self._type: str = data[7][0].lower()
       self.coords: np.ndarray = np.array(data[8:8+self._N], dtype=float)

       # Calculate reciprocal lattice vectors 
       a1, a2, a3 = self.av 
       b1 = 2 * np.pi * np.cross(a2, a3) / (a1@np.cross(a2, a3))
       b2 = 2 * np.pi * np.cross(a3, a1) / (a2@np.cross(a3, a1))
       b3 = 2 * np.pi * np.cross(a1, a2) / (a3@np.cross(a1, a2))
       self.bv: np.ndarray = np.array([b1, b2, b3])

       # Generate atom list 
       atom_list = [f'{symbol} '*num for symbol, num in zip(self.atoms, self.natoms)]
       atom_list = ' '.join(atom_list).split()
       self._atom_list = atom_list

    @property
    def get_name(self):
        '''
        Getter for name
        '''
        print(f'Name: {self.name}')
        return self.name

    @get_name.setter 
    def rename(self, new_name: str):
        '''
        Setter for name
        '''
        print(f'Name changed from "{self.name}" to "{new_name}"')
        self.name = new_name

    @get_name.deleter 
    def delete_name(self): 
        '''
        Deleter for name 
        '''
        print(f'Name "{self.name}" deleted') 
        del self.name

    def Cart_coords(self) -> np.ndarray:
        '''
        Converts fractional coordinates to cartesian coordinates. 
        '''
        self._type = 'cartesian'
        self.cart_coords =  self.coords @ self.av

    def Supercell(self, n: list) -> None: 
        '''
        Creates a supercell of size n1 x n2 x n3. 
        '''
        coords = self.coords
        n1, n2, n3 = n 
        supercell = np.array([[x[0]+a, x[1]+b, x[2]+c] for x in coords for a in range(n1) for b in range(n2) for c in range(n3)]) 
        supercell /= n
        self.av = self.av * n
        self.coords = supercell 
        atom_list = self._s._atom_list
        atom_list = np.array([(f'{x} ' * 8).split() for x in atom_list])
        atom_list = atom_list.flatten().reshape(-1,1)
        self._atom_list = atom_list
        self.natoms = [x*n1*n2*n3 for x in self.natoms]

    def Const_shift(self, vector: np.ndarray) -> np.ndarray:
        '''
        Shifts the structure by a constant vector. 
        '''
        coords = self.coords 
        coords += vector 
        if self._type == 'direct':
            coords %= 1 
        else: 
            pass
        return coords

    def Calculate_mesh(self) -> np.ndarray: 
        '''
        Calculates K-point mesh.
        '''
        kpoint_mesh = []
        kspacing_min, kspacing_max = 0.05, 0.5
        av = self.av 
        bv = self.bv 
        bv_norm = np.array([np.linalg.norm(x) for x in bv], dtype=float)

        temp = [(i,norm) for i, norm in enumerate(bv_norm)]
        temp.sort(key=lambda x: x[1], reverse=True)

        i1, i2, i3 = [i for i,_ in temp]

        # Calculate the number of subdivisions N1, N2, N3 in the reciprocal lattice vectors 
        N_max = max(1, int(np.ceil(bv_norm[i1] / kspacing_min)))
        N_min = max(1, int(np.ceil(bv_norm[i1] / kspacing_max)))

        for n1 in range(N_min, N_max):
            min_spacing = bv_norm[i1] / n1
            if np.fabs(bv_norm[i2] - bv_norm[i1]) < 1e-5:
                n2 = n1 
            else:
                n2 = int(np.ceil(bv_norm[i2] / min_spacing))
                n2 = max(n2, 1) 

            if np.fabs(bv_norm[i3] - bv_norm[i2]) < 1e-5:
                n3 = n2 
            else:
                n3 = int(np.ceil(bv_norm[i3] / min_spacing))
                n3 = max(n3, 1)

            if bv_norm[i2] / n2 < kspacing_max and bv_norm[i3] / n3 < kspacing_max:
                mesh = np.array([None, None, None])
            
            mesh[i1], mesh[i2], mesh[i3] = n1, n2, n3 
            kpoint_mesh.append(mesh)

        # calculate kpoint density 
        volume = np.linalg.det(bv)
        density = np.array([[np.prod(mesh) / volume] for mesh in kpoint_mesh], dtype=float)

        return np.array(kpoint_mesh, dtype=int), density

    def _ENCUT(self) -> np.ndarray:
        '''
        Calculates possible ENCUT values to test for convergence.
        '''
        # check if POTCAR file exits 
        if not os.path.isfile('POTCAR'):
            raise Warning('POTCAR file not found. Please generate POTCAR file first.') 

        with open('POTCAR', 'r') as f: 
            lines = f.readlines() 
        enmax = [float(re.findall(r'ENMAX = ([0-9]+.[0-9]+)', x)[0]) for x in lines if 'ENMAX' in x] 
        encut = max(enmax) * 1.3 
        encut = round(encut / 50) * 50 
        encut_list = [x for x in range(encut - 300, encut + 300, 50)]
        self.encut = encut_list
        return np.array(encut_list)

    def write_poscar(self):
        '''
        Writes POSCAR file. 
        '''
        with open('POSCAR', 'w') as f:
            f.write(f'{self.name}\n')
            f.write(f'{self.scale}\n')
            f.write(f'{" ".join([str(x) for x in self.av[0]])}\n')
            f.write(f'{" ".join([str(x) for x in self.av[1]])}\n')
            f.write(f'{" ".join([str(x) for x in self.av[2]])}\n')
            f.write(f'{" ".join(self.atoms)}\n')
            f.write(f'{" ".join([str(x) for x in self.natoms])}\n')
            f.write(f'{self._type}\n')
            for x in self.coords:
                f.write(f'{" ".join([str(y) for y in x])}\n')


class DOPE():
    """
    A class doping materials. 

    Returns:
        POSCAR: POSCAR files containing the doped structures.
    """
    def __init__(
            self, 
            filename: str, 
            dopant: str, 
            replace: str,
            instances: int):
        '''
        Initializes the DOPE class
        '''
        self.filename = filename
        self.dopant = dopant 
        self.replace = replace
        self.instances = instances 
        self._s = Structure(filename) 
        self._s.Vasp_reader()

    def Symbol_coords(self) -> np.ndarray: 
        '''
        Returns the symbol and coordinates of the atoms in the structure.
        '''
        return np.hstack((np.array(self._s._atom_list).reshape(-1,1), self._s.coords))

    def _replace_atom(self, coords) -> np.ndarray:
        '''
        Replaces the atom in the structure with the dopant in all possible locations. 
        '''
        dopant = self.dopant 
        replace = self.replace 



        # validate replace atom 
        if replace not in self._s.atoms: 
            raise ValueError(f'Atom {replace} not found in structure.')

        structures = []
        temp_coords = coords.copy()
        prev_index = None
        for i in range(len(coords)):
            if coords[i][0] == replace and i != prev_index:
                temp_coords[i][0] = dopant 
                prev_index = i 
                structures.append(temp_coords) 
                temp_coords = coords.copy()

        return np.array(structures)

    @timer
    def Generate_structure(self) -> np.ndarray: 
        '''
        Generate the doped structures with the correct number of instances.
        '''
        structures = self._replace_atom(self.Symbol_coords()) 
        # transform structures into one array of structures
        instances = self.instances 

        if instances == 1:
            pass
        else:
            for j in range(instances-1): 
                for i in range(len(structures)):
                    _temp = self._replace_atom(structures[i]) 
                    structures = np.vstack((structures, _temp))
                    structures = np.unique(structures, axis=0)

        # remove duplicarte structures 
        structures = np.array([x for x in structures if np.count_nonzero(x[:,0] == self.dopant) == instances]) 
        structures = np.unique(structures, axis=0)
        for i in range(len(structures)):
            structures[i] = structures[i][structures[i][:,0].argsort()]

        self._structures = structures
        print(f'Number of structures found = {len(structures)}')

    def Create_defect(self):
        '''
        Creates defects in the stucture
        '''
        for structure in self._structures:
            for i in range(len(structure)):
                if structure[i][0] == self.dopant:
                    del structure[i]
                else:
                    continue

    def write_poscars(self) -> None:
        '''
        Writes the doped structures to POSCAR files.
        '''
        name: str = self._s.name 
        scale: int  = self._s.scale 
        av: np.ndarray = self._s.av 
        type: str = self._s._type
        structures = self._structures

        for i in range(len(structures)):
            atom_list = structures[i][:,0] 
            atoms, counts = np.unique(atom_list, return_counts=True) 
            counts = np.array([str(x) for x in counts]) 
            coords = structures[i][:,1:]

            with open(f'POSCAR_{i+1}.vasp', 'w') as f:
                f.write(f'{name}\n')
                f.write(f'{scale}\n') 
                f.write(f'{av[0][0]} {av[0][1]} {av[0][2]}\n') 
                f.write(f'{av[1][0]} {av[1][1]} {av[1][2]}\n') 
                f.write(f'{av[2][0]} {av[2][1]} {av[2][2]}\n') 
                f.write(f'{" ".join(atoms)}\n')
                f.write(f'{" ".join(counts)}\n') 
                f.write(f'{type}\n') 
                for coord in coords: 
                    f.write(f'{coord[0]} {coord[1]} {coord[2]}\n')

class Rotate():
    '''
    A class for rotating structures.
    '''
    def __init__(self, filename: str, axis: str, angle: float):
        '''
        Initializes the Rotate class.
        '''
        self.filename = filename 
        self.axis = axis 
        self.angle = angle 
        self._s = Structure(filename) 
        self._s.Vasp_reader()
        self.Rx = np.array([
            [1, 0, 0],
            [0, np.cos(angle), -np.sin(angle)],
            [0, np.sin(angle), np.cos(angle)]
            ])
        self.Ry = np.array([
            [np.cos(angle), 0, np.sin(angle)],
            [0, 1, 0],
            [-np.sin(angle), 0, np.cos(angle)]
            ])
        self.Rz = np.array([
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle), np.cos(angle), 0],
            [0, 0, 1]
            ])

    def translate(self) -> None:
        # find the centre 
        coords = self._s.coords 
        centre = np.mean(coords, axis=0) 
        # translate the structure to the origin 
        self._s.coords = coords - centre 
        self._rotate_coord() 
        self._s.coords = self._s.coords + centre 


    def _rotate_coord(self) -> None:
        '''
        Rotates the structure.
        '''
        # Rotate coordinates
        coords = self._s.coords
        if self.axis == 'x':
            self._s.coords = coords @ self.Rx
            #self.av = self._s.av @ self.Rx
        elif self.axis == 'y':
            self._s.coords = coords @ self.Ry
            #self.av = self._s.av @ self.Ry
        elif self.axis == 'z':
            self._s.coords = coords @ self.Rz
            #self.av = self._s.av @ self.Rz
        else:
            raise ValueError(f'Axis {self.axis} not found.')

    def write_poscar(self) -> None: 
        '''
        Writes the rotated structure to a POSCAR file.
        '''
        name: str = self._s.name 
        scale: int  = self._s.scale 
        av: np.ndarray = self._s.av 
        type: str = self._s._type
        coords = self._s.coords
        counts = [str(x) for x in self._s.natoms]

        with open(f'POSCAR_rotated.vasp', 'w') as f:
            f.write(f'{name}\n')
            f.write(f'{scale}\n') 
            f.write(f'{av[0][0]} {av[0][1]} {av[0][2]}\n') 
            f.write(f'{av[1][0]} {av[1][1]} {av[1][2]}\n') 
            f.write(f'{av[2][0]} {av[2][1]} {av[2][2]}\n') 
            f.write(f'{" ".join(self._s.atoms)}\n')
            f.write(f'{" ".join(counts)}\n')
            f.write(f'{type}\n') 
            for coord in coords: 
                f.write(f'{coord[0]} {coord[1]} {coord[2]}\n')


class Asymmetric_unit():
    '''
    A class for creating asymmetric units from a molecular crystal POSCAR file.
    '''
    def __init__(self,
                 filename: str,
                 atom: str,
                 bond_max: float,
                 ):
        '''
        Initializes the Asymmetric_unit class.
        '''
        self.filename = filename 
        self.atom = atom
        self.bond_max = bond_max
        self._s = Structure(filename) 
        self._s.Vasp_reader() 

    def _locate_atom(self) -> None: 
        '''
        Locates the atom in the structure
        '''
        atom = re.split(r'(\d+)', self.atom)
        symbol, index = atom[0], int(atom[1])
        coords = self._s.coords 
        atoms = self._s.atoms 
        natoms = self._s.natoms 

        # find the atom in the structure 
        for ind, sym in enumerate(atoms):
            if sym == symbol:
                atom_index = sum(natoms[0:ind]) + index - 1
        self.vector = np.array([.0, .0, .0]) - coords[atom_index]

    def _translate(self) -> None: 
        '''
        Performs a translation and expansion to ensure a whole molecule is included.
        '''
        self._s.Const_shift(self.vector) 
        self._s.Supercell([2,2,2])
        self._s._type = 'Cartesian'
        self.vector = np.array([-.5, -.5, -.5])
        self._s.Const_shift(self.vector)
        self._s.Cart_coords()

    def _origin_index(self) -> int:
        '''
        Finds the index of the origi atom.
        '''
        coords = self._s.coords
        for ind, val in enumerate(coords):
            if np.allclose(val, [0,0,0]):
                return ind

    def _nearest_neighbours(self, coords: np.ndarray, point: np.ndarray, bond_max: float) -> np.ndarray:
        neighbours = sp.spatial.KDTree(coords[:,1:], leafsize=10, compact_nodes=True, balanced_tree=True) 
        dist, ind = neighbours.query(point, k=10)
        ind = [ind[i] for i in range(len(ind)) if dist[i] < bond_max]
        coords = np.array([coords[i] for i in ind])
        return coords

    def _write_xyz(self) -> None:
        '''
        Writes the asymmetric unit to an XYZ file.
        '''
        with open(f'{self._s.name}_asymmetric_unit.xyz', 'w') as f:
            f.write(f'{len(self.asymm_unit)}\n')
            f.write(f'{self._s.name}\n') 
            for atom in self.asymm_unit: 
                f.write(f'{atom[0]} {atom[1]} {atom[2]} {atom[3]}\n')


    @timer
    def find_unit(self) -> None:
        '''
        Finds the asymmetric unit.
        '''
        self._locate_atom()
        self._translate()
        origin = self._origin_index()
        coords = np.hstack((self._atom_list, np.array(self._s.cart_coords, dtype=float)))

        asymm_unit = np.array([coords[origin]])
        searching = True 
        while searching:
            total_coords = []
            for i in asymm_unit:
                if not i[0] == 'H':
                    temp = self._nearest_neighbours(coords, i[1:], self.bond_max)
                    for i in range(len(temp)): 
                        total_coords.append(temp[i])
            total_coords = np.array(total_coords)
            total_coords = np.unique(total_coords, axis=0)
            if len(total_coords) == len(asymm_unit):
                searching = False
            else: 
                asymm_unit = total_coords
        self.asymm_unit = asymm_unit
        self._write_xyz()


if __name__ == '__main__': 
    dope = DOPE('POSCAR', 'Gd', 'Ca', 2) 
    dope.Generate_structure()
    dope.write_poscars()


