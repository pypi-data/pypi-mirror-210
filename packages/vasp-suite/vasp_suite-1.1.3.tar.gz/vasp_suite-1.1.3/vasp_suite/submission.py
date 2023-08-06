#Imports
import socket

class SubmissionWriter():
    def __init__(self, title, cores, vasp_type):
        self.title = title
        self.cores = cores
        self.vasp_type = vasp_type
        hostname = socket.gethostname() 
        if 'csf3' in hostname:
            self.hostname = 'csf3' 
        elif 'csf4' in hostname:
            self.hostname = 'csf4' 
        else:
            raise Warning('Hostname not recognised. No submission script generated.')

    def submission_csf3(self):
        with open('submit.sh', 'w') as f:
            if self.cores < 32:
                f.write(f'''#!/bin/bash --login
#$ -cwd
#$ -pe smp.pe {self.cores}
''')
            else:
                f.write(f'''#!/bin/bash --login 
#$ -cwd 
#$ -pe mpi-24-ib.pe {self.cores}
''')
                f.write(f'''#$ -N {self.title}

module load apps/intel-19.0/vasp/5.4.4
module load apps/binapps/anaconda3/2022.10 

echo "Started running at `date`"

# Run Vasp
mpirun -np {self.cores} {self.vasp_type}

#run VASP via python script
#python3 Opt.py 
#python3 Conv.py

echo "Finished running at `date`"
''')
 
    def submission_csf4(self):
        with open('submit.sh', 'w') as f:
            if self.cores < 40:
                f.write(f'''#!/bin/bash --login
#SBATCH -p multicore
''')
            else:
                f.write(f'''#!/bin/bash --login
#SBATCH -p multinode
''')
            f.write(f'''#SBATCH -n {self.cores}
#SBATCH --job-name={self.title}

module load vasp/5.4.4-iomkl-2020.02 
module load anaconda3/2020.07

echo "Started running at `date`" 

# Run Vasp 
mpirun -np {self.cores} {self.vasp_type}

#run VASP via python script
#python3 Opt.py 
#python3 Conv.py 

echo "Finished running at `date`"
''')


