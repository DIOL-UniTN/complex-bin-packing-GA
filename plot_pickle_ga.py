import matplotlib.pyplot as plt
import scienceplots
import numpy as np
import dill

def save_plot(save_file, best, worst, mean):
    plt.style.use(['science', 'nature', 'muted'])

    fig, ax = plt.subplots(figsize=(6, 3))

    ax.plot(best, label='best')
    ax.plot(worst, label='worst')
    ax.plot(mean, label='mean')
    ax.legend(fontsize=12)
    ax.autoscale(tight=True)

    ax.set_xlabel('Generations', fontsize=14)
    ax.set_ylabel('Fitness', fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=12)

    plt.ylim(bottom=np.min(best)-10, top=np.max(worst)+10)
    fig.savefig(f"{save_file}.pdf", format="pdf", dpi=300)
    plt.close()

def get_fitness(individual):
    f = 0
    days_len = len(individual)
    for i in range(1, days_len+1):
        if(sum([1 for machine in individual[-i].machines.values() if machine.occupation > 0]) != 0):
            f += days_len-i
            break
    for day in individual:
        f += 0 * sum([1 for machine in day.machines.values() if machine.getRemaininSpace() < 0])

    return f

def time_average():
    for ga in ['GA_1', 'GA_2']:
        for conf in ["100_200", "200_100"]:
            for ind in range(1, 19):
                times = []
                for seed in [398, 2367, 9845, 92465, 2364782, 28, 1845, 72965, 83672, 5399472]:
                    with open(f"solutions/{ga}/{conf}_{seed}/{conf}_nstance_{ind}_{seed}.pkl", "rb") as f:
                        ga_data = dill.load(f)
                        times.append(ga_data['time'])

                print(f"{ga} {conf} inst_{ind}", np.mean(times), np.std(times))

def fitness_average():
    for ga in ['GA_1', 'GA_2']:
        for conf in ["100_200", "200_100"]:
            for ind in range(1, 19):
                fitness = []
                times = []
                for seed in [398, 2367, 9845, 92465, 2364782, 28, 1845, 72965, 83672, 5399472]:
                    with open(f"solutions/{ga}/{conf}_{seed}/{conf}_nstance_{ind}_{seed}.pkl", "rb") as f:
                        ga_data = dill.load(f)
                        fitness.append(ga_data['best']['fitness'][-1])
                        times.append(ga_data['time'])
                print(f"{ga} {conf} inst_{ind}", np.mean(fitness), np.std(fitness))
                print(f"{ga} {conf} inst_{ind}", np.mean(times), np.std(times))

def plot_results():
    ga_results = {
        'GA_1': None,
        'GA_2': None
    }
    for ga in ['GA_1', 'GA_2']:
        ga_data_seeds = {}
        for ind in range(1, 19):
            ga_data_seeds[ind] = {
                '100_200': {
                    'best': [],
                    'mean': [],
                    'worst': []
                },
                '200_100': {
                    'best': [],
                    'mean': [],
                    'worst': []
                }
            }
            for seed in [398, 2367, 9845, 92465, 2364782, 28, 1845, 72965, 83672, 5399472]:
                with open(f"solutions/{ga}/100_200_{seed}/100_200_nstance_{ind}_{seed}.pkl", "rb") as f:
                    ga_data = dill.load(f)
                    ga_data_seeds[ind]['100_200']['best'].append(ga_data['best']['fitness'])
                    ga_data_seeds[ind]['100_200']['mean'].append(ga_data['mean'])
                    ga_data_seeds[ind]['100_200']['worst'].append(ga_data['worst']['fitness'])
                    #save_plot(f"solutions/{ga}/100_200_{seed}/100_200_nstance_{ind}_{seed}", ga_data['best']['fitness'], ga_data['worst']['fitness'], ga_data['mean'])
                    #print(f"{ga} 100 200 inst_{ind} {seed}", ga_data['time'])
                
                with open(f"solutions/{ga}/200_100_{seed}/200_100_nstance_{ind}_{seed}.pkl", "rb") as f:
                    ga_data = dill.load(f)
                    ga_data_seeds[ind]['200_100']['best'].append(ga_data['best']['fitness'])
                    ga_data_seeds[ind]['200_100']['mean'].append(ga_data['mean'])
                    ga_data_seeds[ind]['200_100']['worst'].append(ga_data['worst']['fitness'])
                    #save_plot(f"solutions/{ga}/200_100_{seed}/200_100_nstance_{ind}_{seed}", ga_data['best']['fitness'], ga_data['worst']['fitness'], ga_data['mean'])
                    #print(f"{ga} 200 100 inst_{ind} {seed}", ga_data['time'])


            ga_data_seeds[ind]['100_200']['best'] = [np.mean([bests[gen] for bests in ga_data_seeds[ind]['100_200']['best']]) for gen in range(200)]
            ga_data_seeds[ind]['100_200']['mean'] = [np.mean([bests[gen] for bests in ga_data_seeds[ind]['100_200']['mean']]) for gen in range(200)]
            ga_data_seeds[ind]['100_200']['worst'] = [np.mean([bests[gen] for bests in ga_data_seeds[ind]['100_200']['worst']]) for gen in range(200)]
            

            ga_data_seeds[ind]['200_100']['best'] = [np.mean([bests[gen] for bests in ga_data_seeds[ind]['200_100']['best']]) for gen in range(100)]
            ga_data_seeds[ind]['200_100']['mean'] = [np.mean([bests[gen] for bests in ga_data_seeds[ind]['200_100']['mean']]) for gen in range(100)]
            ga_data_seeds[ind]['200_100']['worst'] = [np.mean([bests[gen] for bests in ga_data_seeds[ind]['200_100']['worst']]) for gen in range(100)]
            save_plot(f"solutions/{ga}/100_200_nstance_{ind}", ga_data_seeds[ind]['100_200']['best'], ga_data_seeds[ind]['100_200']['worst'], ga_data_seeds[ind]['100_200']['mean'])
            save_plot(f"solutions/{ga}/200_100_nstance_{ind}", ga_data_seeds[ind]['200_100']['best'], ga_data_seeds[ind]['200_100']['worst'], ga_data_seeds[ind]['200_100']['mean'])
       
        ga_results[ga] = ga_data_seeds

    # with open(f'ga_results_averages.pkl', 'wb') as handle:
    #     dill.dump(ga_results, handle, protocol=dill.HIGHEST_PROTOCOL)

if __name__ == "__main__":
    plot_results()
    #time_average()
    #fitness_average()