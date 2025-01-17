from typing import List, Dict
import datetime
import random
import copy
import pandas as pd
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
import scienceplots
import argparse
#import pickle
import dill
import time
from data_manipulation import create_data_model_2
from pathlib import Path

parser = argparse.ArgumentParser(description='Plot fitnesses of same encoding but different seeds.')

parser.add_argument('-f', dest='arrivals_file', action='store',
                    help='File of patient arrivals (must be in folder "data")', default='instances/2020_PatientArrivals_instance_1')
parser.add_argument('-s', dest='save_file', action='store',
                    help='File where to save the plot', default='GA_instance_1')
parser.add_argument('-p', dest='pop_size', action='store',
                    help='Population size', default='100', type=int)
parser.add_argument('-g', dest='generations_num', action='store',
                    help='Number of generations', default='200', type=int)
parser.add_argument('--seed', dest='seed', action='store',
                    help='Seed', default=23, type=int)

args = parser.parse_args()

class Fraction:
    def __init__(self, patient_id, id, size = 5):
        self.patient_id = patient_id
        self.id = id
        self.size = size

    def __eq__(self, other):
        if not isinstance(other, Fraction):
            return False
        return self.patient_id == other.patient_id and self.id == other.id and self.size == other.size

    def __hash__(self):
        return hash(f"{self.patient_id}_{self.id}")
    
    def __repr__(self):
        return f"{self.patient_id}_fraction_{self.id}_{self.size}"

class Patient:
    def __init__(self, id, fractions: List[int], machines: List[str]):
        self.id = id
        self.fractions = []
        for i in range(len(fractions)):
            self.fractions.append(Fraction(self.id, i, fractions[i]))
        self.machines = machines

    def get_fractions(self):
        return self.fractions
    
    def get_machines(self):
        return self.machines
    
    def __eq__(self, other):
        if not isinstance(other, Patient):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
    
    def __repr__(self):
        return f"patient_{self.id}"
    
class Machine:
    def __init__(self, id, capacity = 100):
        self.id = id
        self.patients = set()
        self.start_patients = set()
        self.capacity = capacity
        self.occupation = 0

    def get_patients(self):
        return self.patients
    
    def get_start_patients(self):
        return self.start_patients
    
    def add_patient(self, patient: Patient, fraction: Fraction):
        self.patients.add(patient)
        self.occupation += fraction.size
    
    def add_start_patient(self, patient: Patient):
        self.start_patients.add(patient)

    def remove_patient(self, patient: Patient, fraction: Fraction):
        self.patients.remove(patient)
        self.occupation -= fraction.size

    def remove_start_patient(self, patient: Patient):
        self.start_patients.remove(patient)

    def getRemaininSpace(self):
        return self.capacity - self.occupation

class Day:
    def __init__(self, id, date: datetime, machines : Dict[str, Machine]):
        self.id = id
        self.date = date
        self.machines = machines

    def find_patient_machine(self, patient: Patient):
        machine = [key for key, value in self.machines.items() if patient in value.get_patients()]
        if len(machine) != 1:
            raise NotImplementedError
        
        return machine[0]

class GA():
    def __init__(self, patients: List[Patient], machines: List[Dict[str, int]], days, population_size, generations, mutation_rate, crossover_rate, tournament_size = 2, offspring_num = None):
        self.patients = patients
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.tournament_size = tournament_size
        if offspring_num is not None:
            self.offspring_num = offspring_num
        else:
            self.offspring_num = int(population_size/2)
        self.population = self.create_population(patients, machines, days)

    def add_start_patient(self, patient: Patient, individual: List[Day], index):
        machine_chosen = random.sample(patient.get_machines(), 1)[0]
        individual[index].machines[machine_chosen].add_start_patient(patient)

        all_fractions = patient.get_fractions()
        for i, fraction in enumerate(all_fractions):
            try:
                individual[i+index].machines[machine_chosen].add_patient(patient, fraction)
            except IndexError:
                print(len(individual), index, i)
                raise IndexError
            machine_chosen = random.sample(patient.get_machines(), 1)[0]

    def remove_start_patient(self, patient: Patient, individual: List[Day], index_day, index_machine):
        individual[index_day].machines[index_machine].remove_start_patient(patient)

        all_fractions = patient.get_fractions()
        for i, fraction in enumerate(all_fractions):
            index_mach = individual[i+index_day].find_patient_machine(patient)
            individual[i+index_day].machines[index_mach].remove_patient(patient, fraction)

    def create_population(self, patients: List[Patient], machines_list: List[Dict[str, int]], days):
        # also try shuffling n times the items and applying first fit
        fractions_list = [len(patient.get_fractions()) for patient in patients]
        total_fractions = sum(fractions_list)
        max_fractions = max(fractions_list)
        population = []
        # all_days = [pd.to_datetime(i, unit='D', origin=pd.Timestamp('01-01-2020')).date() for i in range(total_fractions*2)]
        # all_days = [d for d in all_days if d not in holidays.BE(years=2020) and d.weekday() < 5][:total_fractions]
        all_days = days[:total_fractions]
        population = []

        for _ in range(self.population_size):
            machines = [{key: Machine(key, value) for key, value in machines.items()} for machines in machines_list]
            individual = [Day(i, day, machines[i]) for i, day in enumerate(all_days)]
            for patient in patients:
                index = random.randint(0, min(
                    int(max_fractions), 
                    len(individual)-len(patient.get_fractions())-1
                ))
                self.add_start_patient(patient, individual, index)
            population.append(individual)

        return population
    
    def find_patient_start_day_and_machine(self, individual, patient: Patient):
        indexes = [(ind_day, ind_mach) for ind_day, day in enumerate(individual) for ind_mach, mach in day.machines.items() if patient in mach.start_patients]
        if len(indexes) != 1:
            raise NotImplementedError
        return indexes[0]

    def crossover(self, parent1: List[Day], parent2: List[Day]):
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)

        if random.random() > self.crossover_rate:
            cross_patients = random.sample(self.patients, random.randint(1, min(3, len(self.patients))))

            for cross_p in cross_patients:
                d_start_1_ind, ind_mach_1 = self.find_patient_start_day_and_machine(child1, cross_p)
                d_start_2_ind, ind_mach_2 = self.find_patient_start_day_and_machine(child2, cross_p)

                self.remove_start_patient(cross_p, child1, d_start_1_ind, ind_mach_1)
                self.add_start_patient(cross_p, child1, d_start_2_ind)

                self.remove_start_patient(cross_p, child2, d_start_2_ind, ind_mach_2)
                self.add_start_patient(cross_p, child2, d_start_1_ind)

            # if sum([1 for day in child1[21:] if len(day.patients) > 0]) > 0 or sum([1 for day in child2[21:] if len(day.patients) > 0]) > 0:
            #     raise NotImplementedError
            
        return child1, child2

    def mutation(self, individual: List[Day]):
        #select randomly a patient and shift the starting treatment 
        patient_to_shift = random.sample(self.patients, 1)[0]
        shift_day = random.sample([-3, -2, -1, 1, 2, 3], 1)[0]
        
        d_start_ind, ind_mach = self.find_patient_start_day_and_machine(individual, patient_to_shift)

        new_ind = d_start_ind + shift_day

        if new_ind < 0:
            new_ind =  len(individual) - len(patient_to_shift.get_fractions())
        if new_ind + len(patient_to_shift.get_fractions()) > len(individual):
            new_ind = 0
        
        self.remove_start_patient(patient_to_shift, individual, d_start_ind, ind_mach)
        self.add_start_patient(patient_to_shift, individual, new_ind)

        # if sum([1 for day in individual[21:] if len(day.patients) > 0]) > 0:
        #     raise NotImplementedError

        return individual
    
    def get_fitness(self, individual: List[Day]):
        f = 0
        days_len = len(individual)
        for i in range(1, days_len+1):
            if(sum([1 for machine in individual[-i].machines.values() if machine.occupation > 0]) != 0):
                f += days_len-i+1
                break
        for day in individual:
            f += 50 * sum([1 for machine in day.machines.values() if machine.getRemaininSpace() < 0])

        return f

    def tournament_selection(self):
        k = self.tournament_size
        n = self.offspring_num

        if k < 1 or k > len(self.population):
            raise NotImplementedError
        parents = []
        for i in range(n):
            parents.append(sorted(random.sample(self.population, k), key= lambda a: self.get_fitness(a), reverse=False)[0])
        
        return parents


    def run(self):
        start_time = time.time()

        sorted_pop = sorted(self.population, key = lambda a: self.get_fitness(a), reverse=False)
        worst = {
            'fitness':[self.get_fitness(sorted_pop[-1])],
            'individual':[sorted_pop[-1]]
        }
        mean = [np.mean([self.get_fitness(individual) for individual in sorted_pop])]
        best = {
            'fitness':[self.get_fitness(sorted_pop[0])],
            'individual':[sorted_pop[0]]
        }

        for _ in tqdm(range(self.generations)):
            # if sum([sum([1 for day in individual[21:] if len(day.patients) > 0]) for individual in self.population]) > 0:
            #     raise NotImplementedError
            # TODO: use crossover rate
            parents = self.tournament_selection()
            offspring = []
            for i in range(0, len(parents), 2):
                child1, child2 = self.crossover(parents[i], parents[i+1])
                offspring.append(child1)
                offspring.append(child2)
            sorted_pop = sorted(self.population, key = lambda a: self.get_fitness(a), reverse=False)
            self.population = sorted_pop[:len(sorted_pop)-self.offspring_num] + offspring
            for i in range(len(self.population)):
                if random.random() >= self.mutation_rate:
                    self.population[i] = self.mutation(self.population[i])
            
            sorted_pop = sorted(self.population, key = lambda a: self.get_fitness(a), reverse=False)
            worst['fitness'].append(self.get_fitness(sorted_pop[-1]))
            worst['individual'].append(sorted_pop[-1])
            best['fitness'].append(self.get_fitness(sorted_pop[0]))
            best['individual'].append(sorted_pop[0])
            mean.append(np.mean([self.get_fitness(individual) for individual in sorted_pop]))

        exe_time = time.time() - start_time
        return self.population, [self.get_fitness(individual) for individual in self.population], best, worst, mean, exe_time


if __name__ == "__main__":
    random.seed(args.seed)

    data = create_data_model_2(args)

    patients = [Patient(id, list(patient["fractions"].values()), patient["machines"]) for id, patient in data["patients"].items()]
    alg = GA(patients, list(data["bin_days"].values()), list(data["day_to_actual_days"].values()), args.pop_size, args.generations_num, 1, 0.8)
    print([alg.get_fitness(individual) for individual in alg.population])
    population, fitnesses, best, worst, mean, exe_time = alg.run()
    print(fitnesses)

    sorted_pop = sorted(population, key = lambda a: alg.get_fitness(a), reverse=False)
    fileName = f'{args.save_file}_{args.seed}.pkl'
    output_file = Path(fileName)
    output_file.parent.mkdir(exist_ok=True, parents=True)
    with open(fileName, 'wb') as handle:
        dill.dump({'best': best, 'worst': worst, 'mean': mean, 'time': exe_time, 'best_individual': sorted_pop[0]}, handle, protocol=dill.HIGHEST_PROTOCOL)
    # for day in sorted_pop[0]:
    #     print(day.date)
    #     for machine in day.machines.values():
    #         print(f"Machine {machine.id} with remaining space {machine.getRemaininSpace()}:")
    #         print(machine.get_patients())

    #save_plot(args, best, worst, mean)