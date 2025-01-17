# Addressing Radiotherapy Scheduling with a Bin Packing Problem Formulation: A Comparative Study of Exact Solvers and Genetic Algorithms

## Requirements
0. We assume Anaconda is installed. One can install it according to its [installation page](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).
1. Clone this repo:
```
git clone https://github.com/DIOL-UniTN/complex-bin-packing-GA.git
cd complex-bin-packing-GA
```
2. Create a virtual environment using `environment.yml` file. 
```
conda env create -f environment.yml
conda activate complex-bin-packing-GA
```

## Run

### ILP with SCIP solver

```
python complex_bin_packing.py -f instances/2020_PatientArrivals_instance_1 -s solutions/SCIP/ILP_instance_1 -b SCIP
```

### ILP with SAT solver

```
python complex_bin_packing.py -f instances/2020_PatientArrivals_instance_1 -s solutions/SCIP/ILP_instance_1 -b SAT
```

### CP with CP-SAT solver

```
python complex_bin_packing_cp.py -f instances/2020_PatientArrivals_instance_1 -s solutions/SCIP/ILP_instance_1
```

### GGA Version 1

```
python ga_patient_scheduling.py -f instances/2020_PatientArrivals_instance_1 -s solutions/GA_1/100_200_28/100_200_instance_1 -p 100 -g 200 --seed 28
```

### GGA Version 2

```
python ga_patient_scheduling_v2.py -f instances/2020_PatientArrivals_instance_1 -s solutions/GA_2/100_200_28/100_200_instance_1 -p 100 -g 200 --seed 28
```
