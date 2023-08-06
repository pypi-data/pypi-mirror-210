# Import argparse
import argparse
from textwrap import dedent
import numpy as np

# Import Modules
from . import core

# Create the wrapper funstions 

def generate_input_func(args):
    '''
    Wrapper function for the generate_input function

    parameters
    ----------
    filename : str
    config_file : file

    Returns
    -------
    INCAR : file
    '''
    core.generate_input(
        filename=args.filename,
        calculation=args.config_file,
            )

def calculate_kpoints_func(args):
    '''
    Wrapper function for the calculate_kpoints function

    parameters
    ----------
    filename : str

    Returns
    -------
    KPOINT mesh : int 
    '''
    core.calculate_kpoints(
            filename=args.filename,
            )

def generate_kpoints_func(args):
    '''
    Wrapper function for the generate_kpoints function 

    parameters
    ----------
    mesh : int 

    Returns
    -------
    KPOINTS : file
    '''
    core.generate_kpoints(
            mesh=args.mesh,
            )

def generate_supercell_func(args):
    '''
    Wrapper function for the generate_supercell function

    parameters
    ----------
    expansion : list

    Returns
    -------
    POSCAR : file 
    .xyz : file
    '''
    core.generate_supercell(
            expansion=np.array(args.expansion, dtype=int),
            )

def generate_job_func(args):
    '''
    Wrapper function for the generate_job function 

    parameters
    ----------
    title : str 
    cores : int 
    vasp_type : str 

    Returns
    -------
    job.sh : file
    '''
    core.generate_job(
            title=args.title,
            cores=args.cores,
            vasp_type=args.vasp_type,
            )

def start_up_func():
    '''
    Wrapper function for the start_up function

    parameters
    ----------
    None

    Returns
    -------
    configuration files : file
    '''
    core.start_up()

def dope_structure_func(args):
    '''
    Wrapper function for the dope_structure function

    parameters
    ----------
    filename : str 
    dopant : str 
    replace : str 
    instances : int 
    
    Returns
    -------
    POSCARs : file 
    '''
    core.dope_structure(
        filename=args.filename,
        dopant=args.dopant,
        replace=args.replace,
        instances=args.instances,
        )

def generate_defect_func(args): 
    '''
    Wrapper function for the generate_defect function

    parameters
    ----------
    filename : str 
    site : str 
    instances : int 

    Returns
    -------
    POSCAR : file 
    '''
    core.generate_defect(
            filename=args.filename,
            site=args.site,
            instances=args.instances,
            )

def asymmetric_unit_func(args):
    '''
    Wrapper function for the asymmetric_unit function

    parameters
    ----------
    filename : str 
    atom : str 
    bond_max : float 

    Returns
    -------
    POSCAR : file 
    '''
    core.asymmetric_unit(
            filename=args.filename,
            atom=args.atom,
            bond_max=args.bond_max,
            )


def read_args(arg_list=None):
    '''Reads the command line arguments'''
    parser = argparse.ArgumentParser(
            prog='vasp_suite',
            description=dedent(
                '''
                ---------------------------------------------------
                                                  
                      A suite of tools for VASP calculations      

                ---------------------------------------------------
                
                Available programmes:
                    vasp_suite generate_input ...
                    vasp_suite generate_job ...
                    vasp_suite calculate_kpoints ...
                    vasp_suite generate_kpoints ...
                    vasp_suite generate_supercell ...
                    vasp_suite start_up ...
                    vasp_suite dope_structure ...
                    vasp_suite generate_defect ...
                    vasp_suite asymmetric_unit ...
                '''
                ),
            epilog=dedent(
                '''
                To display options for a specific programme, use vasp_suite <programme> -h
                '''
                ),
            formatter_class=argparse.RawDescriptionHelpFormatter
            )

    # Subparsers 
    subparsers = parser.add_subparsers(dest='prog')

    gen_inp = subparsers.add_parser(
            'generate_input',
            help='Generate input files for VASP calculations',
            description=dedent(
                '''
                Generation of INCAR and POTCAR files for VASP calculations.
                '''
                ),
            formatter_class=argparse.RawDescriptionHelpFormatter
            )

    gen_inp.set_defaults(func=generate_input_func)

    gen_inp.add_argument(
            'config_file',
            help=dedent(
                '''
                The configuration file for the input generation.
                
                Example:
                Inside ~/.vasp_suite_templates '.ini' configuration files are 
                stored. To perform a relaxation caluclation using the relaxation.ini 
                template, use the following command:

                vasp_suite generate_input relaxation
                '''
                )
            )

    gen_inp.add_argument(
            '--filename, -f',
            help=dedent(
                '''
                The name of the structure file, default is POSCAR
                '''
                ),
            default='POSCAR'
            )

    gen_job = subparsers.add_parser(
        'generate_job',
        help='Generate job submission files for VASP calculations',
        formatter_class=argparse.RawDescriptionHelpFormatter
        )

    gen_job.set_defaults(func=generate_job_func)

    gen_job.add_argument(
        'title',
        help='The title of the job'
        )

    gen_job.add_argument(
        'cores',
        help='The number of cores to use',
        type=int,
        )

    gen_job.add_argument(
        '--vasp_type',
        help=dedent(
            '''
            The VASP programme you widh to use:
                - vasp_std
                - vasp_gam
            '''
            ),
        default='vasp_gam'
        )

    calc_kpoints = subparsers.add_parser(
        'calculate_kpoints',
        help='Calculate the possible kpoint meshes for a given structure',
        formatter_class=argparse.RawDescriptionHelpFormatter
        )

    calc_kpoints.set_defaults(func=calculate_kpoints_func)

    gen_kpoints = subparsers.add_parser(
        'generate_kpoints',
        help='Generate the kpoints file for a given structure',
        formatter_class=argparse.RawDescriptionHelpFormatter
        )

    gen_kpoints.set_defaults(func=generate_kpoints_func)

    gen_kpoints.add_argument(
        'mesh',
        nargs=3,
        help=dedent(
            '''
            The mesh to use for the kpoints file.
            command line arguments are written in the form:
            a b c
            '''
            )
        )

    gen_supercell = subparsers.add_parser(
        'generate_supercell',
        help='Generate a supercell from a given structure',
        formatter_class=argparse.RawDescriptionHelpFormatter
        )

    gen_supercell.set_defaults(func=generate_supercell_func)

    gen_supercell.add_argument(
        'Expansion',
        nargs=3,
        help=dedent(
            '''
            The expansion factor for the a lattice vector.
            '''
            ),
        )

    start_up = subparsers.add_parser(
        'start_up',
        help='Generate the configuration files for the suite',
        formatter_class=argparse.RawDescriptionHelpFormatter
        )

    start_up.set_defaults(func=start_up_func)

    dope_struct = subparsers.add_parser(
        'dope_structure',
        help='Dope a structure with a given element',
        formatter_class=argparse.RawDescriptionHelpFormatter
        )

    dope_struct.set_defaults(func=dope_structure_func)

    dope_struct.add_argument(
        '--filename, -f',
        help='The name of the structure file',
        default='POSCAR',
        )

    dope_struct.add_argument(
            'dopant',
            help='The element to dope the structure with',
            )

    dope_struct.add_argument(
            'replace',
            help='The element to replace',
            ) 

    dope_struct.add_argument(
            '--instances',
            help='The number of instances of the dopant to add',
            type=int,
            default=1,
            )

    gen_defect = subparsers.add_parser(
        'generate_defect',
        help='Generate a defect structure',
        formatter_class=argparse.RawDescriptionHelpFormatter
        )

    gen_defect.set_defaults(func=generate_defect_func)

    gen_defect.add_argument(
            '--filename, -f',
            help='The name of the structure file',
            default='POSCAR',
            )

    gen_defect.add_argument(
            'site',
            help='The name of the atom to remove',
            )

    gen_defect.add_argument(
            '--instances',
            help='The number of instances of defect',
            type=int,
            default=1,
            )

    asym = subparsers.add_parser(
        'asymmetric_unit',
        help='Generate the asymmetric unit of a structure',
        formatter_class=argparse.RawDescriptionHelpFormatter
        )

    asym.set_defaults(func=asymmetric_unit_func)

    asym.add_argument(
            '--filename, -f',
            help='The name of the structure file',
            default='POSCAR',
            )

    asym.add_argument(
            'atom',
            help='The name of the spin centre in the molecular crystal',
            )

    asym.add_argument(
            '--bond_max, -b',
            help='The maximum bond length/ Å',
            type=float,
            default=2.6,
            )


    # Parse the ArgumentParser
    parser.set_defaults(func=lambda args: parser.print_help())
    args = parser.parse_known_args(arg_list)

    # Select programme 
    if args in ['generate_input, generate_job, calculate_kpoints, generate_kpoints, generate_supercell, start_up, dope_structure, generate_defect']:
        args.func(args)
    else:
        args = parser.parse_args(arg_list)
        args.func(args)

def main():
    read_args()
