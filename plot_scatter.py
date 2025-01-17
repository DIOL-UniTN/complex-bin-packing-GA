import matplotlib.pyplot as plt
import scienceplots
import numpy as np
import pandas as pd

def save_plot(save_file, c1, c2, c1_name, c2_name, limit_c1=14400, limit_c2=14400):
    plt.style.use(['science', 'nature', 'muted'])

    fig, ax = plt.subplots()

    ax.plot(c1, c2, 'o', markersize=4, markeredgecolor='black')

    # Traccia una linea orizzontale e una linea verticale
    ax.axhline(y=limit_c2, color='red', linestyle='--')
    ax.axvline(x=limit_c1, color='red', linestyle='--')

    # Imposta la scala logaritmica su entrambi gli assi
    ax.set_xscale('log')
    ax.set_yscale('log')

    # Imposta gli stessi limiti per entrambi gli assi
    max_limit = max(limit_c1, limit_c2) + 10**5
    plt.ylim(bottom=10**-3, top=max_limit)
    plt.xlim(left=10**-3, right=max_limit)

    # Traccia le linee diagonali con inclinazione di 45 gradi su scala logaritmica
    x_vals = np.logspace(-3, np.log10(limit_c2+10**5), 100)
    y_vals1 = x_vals * 0.1 # Prima linea diagonale (y = x)
    y_vals2 = x_vals * 10  # Seconda linea diagonale (y = 10x)
    y_vals3 = x_vals  # Seconda linea diagonale (y = 10x)
    ax.plot(x_vals, y_vals1, '--', color='green')
    ax.plot(x_vals, y_vals2, '--', color='green')
    ax.plot(x_vals, y_vals3, '--', color='darkgreen')

    # Colora l'area tra le due linee diagonali
    ax.fill_between(x_vals, y_vals1, y_vals2, where=(y_vals2 >= y_vals1), color='lightgreen', alpha=0.3)

    ax.set_xlabel(c1_name, fontsize=14)
    ax.set_ylabel(c2_name, fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=12)

    fig.savefig(f"{save_file}.pdf", format="pdf", dpi=300)
    plt.close()

def save_plot_fitness(save_file, c1, c2, c1_name, c2_name, limit_c1=300, limit_c2=300):
    plt.style.use(['science', 'nature', 'muted'])

    fig, ax = plt.subplots()

    ax.plot(c1, c2, 'C5o', markersize=4, markeredgecolor='black')

    # Traccia una linea orizzontale e una linea verticale
    ax.axhline(y=limit_c2, color='red', linestyle='--')
    ax.axvline(x=limit_c1, color='red', linestyle='--')

    # Imposta la scala logaritmica su entrambi gli assi
    ax.set_xscale('log')
    ax.set_yscale('log')

    # Imposta gli stessi limiti per entrambi gli assi
    max_limit = max(limit_c1, limit_c2) + 10**3
    # max_limit = max(limit_c1, limit_c2) + 10
    plt.ylim(bottom=1, top=max_limit)
    plt.xlim(left=1, right=max_limit)

    # Traccia le linee diagonali con inclinazione di 45 gradi su scala logaritmica
    x_vals = np.logspace(0, np.log10(limit_c2+10**3), 10)
    y_vals1 = x_vals * 10**(-0.5) # Prima linea diagonale (y = x)
    y_vals2 = x_vals * 10**(0.5)  # Seconda linea diagonale (y = 10x)
    y_vals3 = x_vals  # Seconda linea diagonale (y = 10x)
    # x_vals = np.linspace(1, limit_c2, 100)
    # y_vals1 = x_vals + 10 # Prima linea diagonale (y = x)
    # y_vals2 = x_vals - 10  # Seconda linea diagonale (y = 10x)
    # y_vals3 = x_vals  # Seconda linea diagonale (y = 10x)
    ax.plot(x_vals, y_vals1, '--', color='skyblue')
    ax.plot(x_vals, y_vals2, '--', color='skyblue')
    ax.plot(x_vals, y_vals3, '--', color='cadetblue')

    # Colora l'area tra le due linee diagonali
    ax.fill_between(x_vals, y_vals1, y_vals2, where=(y_vals2 >= y_vals1), color='powderblue', alpha=0.3)

    
    ax.set_xlabel(c1_name, fontsize=14)
    ax.set_ylabel(c2_name, fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=12)

    fig.savefig(f"{save_file}.pdf", format="pdf", dpi=300)
    plt.close()


def save_plot_not_log(save_file, c1, c2, c1_name, c2_name, limit_c1=300, limit_c2=300):
    plt.style.use(['science', 'nature', 'muted'])

    fig, ax = plt.subplots()

    ax.plot(c1, c2, 'C5o')

    # Traccia una linea orizzontale e una linea verticale
    ax.axhline(y=limit_c2, color='red', linestyle='--')
    ax.axvline(x=limit_c1, color='red', linestyle='--')

    # Imposta la scala logaritmica su entrambi gli assi
    # ax.set_xscale('log')
    # ax.set_yscale('log')

    # Imposta gli stessi limiti per entrambi gli assi
    max_limit = max(limit_c1, limit_c2) + 50
    plt.ylim(bottom=0, top=max_limit)
    plt.xlim(left=0, right=max_limit)

    # Traccia le linee diagonali con inclinazione di 45 gradi su scala logaritmica
    x_vals = np.array(limit_c2+50)
    y_vals1 = x_vals +5 # Prima linea diagonale (y = x)
    y_vals2 = x_vals -5  # Seconda linea diagonale (y = 10x)
    y_vals3 = x_vals  # Seconda linea diagonale (y = 10x)
    ax.plot(x_vals, y_vals1, '--', color='skyblue')
    ax.plot(x_vals, y_vals2, '--', color='skyblue')
    ax.plot(x_vals, y_vals3, '--', color='cadetblue')

    # Colora l'area tra le due linee diagonali
 #   ax.fill_between(x_vals, y_vals1, y_vals2, where=(y_vals2 >= y_vals1), color='powderblue', alpha=0.3)

    ax.set_xlabel(c1_name, fontsize=14)
    ax.set_ylabel(c2_name, fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=12)

    fig.savefig(f"{save_file}.pdf", format="pdf", dpi=1200)
    plt.close()


if __name__ == "__main__":
    times = pd.read_csv('times.csv', sep=',', header=0)
    instances = {
        'GA 1 (100p 200g)': [],
        'GA 1 (200p 100g)': [],
        'GA 2 (100p 200g)': [],
        'GA 2 (200p 100g)': [],
        'SCIP': [],
        'SAT': [],
        'CP': []
    }
    for index, row in times.iterrows():
        instances['GA 1 (100p 200g)'].append(row['GA 1 (100p 200g)'])
        instances['GA 1 (200p 100g)'].append(row['GA 1 (200p 100g)'])
        instances['GA 2 (100p 200g)'].append(row['GA 2 (100p 200g)'])
        instances['GA 2 (200p 100g)'].append(row['GA 2 (200p 100g)'])
        instances['SCIP'].append(row['SCIP'])
        instances['SAT'].append(row['SAT'])
        instances['CP'].append(row['CP'])

    save_plot('GA_1_100_200_vs_GA_1_200_100', instances['GA 1 (100p 200g)'], instances['GA 1 (200p 100g)'], 'GA 1 (100p 200g)', 'GA 1 (200p 100g)')
    save_plot('GA_1_100_200_vs_GA_2_100_200', instances['GA 1 (100p 200g)'], instances['GA 2 (100p 200g)'], 'GA 1 (100p 200g)', 'GA 2 (100p 200g)')
    save_plot('GA_1_100_200_vs_GA_2_200_100', instances['GA 1 (100p 200g)'], instances['GA 2 (200p 100g)'], 'GA 1 (100p 200g)', 'GA 2 (200p 100g)')
    save_plot('GA_1_100_200_vs_SCIP', instances['GA 1 (100p 200g)'], instances['SCIP'], 'GA 1 (100p 200g)', 'SCIP')
    save_plot('GA_1_100_200_vs_SAT', instances['GA 1 (100p 200g)'], instances['SAT'], 'GA 1 (100p 200g)', 'SAT')
    save_plot('GA_1_100_200_vs_CP', instances['GA 1 (100p 200g)'], instances['CP'], 'GA 1 (100p 200g)', 'CP')

    save_plot('GA_1_200_100_vs_GA_2_100_200', instances['GA 1 (200p 100g)'], instances['GA 2 (100p 200g)'], 'GA 1 (200p 100g)', 'GA 2 (100p 200g)')
    save_plot('GA_1_200_100_vs_GA_2_200_100', instances['GA 1 (200p 100g)'], instances['GA 2 (200p 100g)'], 'GA 1 (200p 100g)', 'GA 2 (200p 100g)')
    save_plot('GA_1_200_100_vs_SCIP', instances['GA 1 (200p 100g)'], instances['SCIP'], 'GA 1 (200p 100g)', 'SCIP')
    save_plot('GA_1_200_100_vs_SAT', instances['GA 1 (200p 100g)'], instances['SAT'], 'GA 1 (200p 100g)', 'SAT')
    save_plot('GA_1_200_100_vs_CP', instances['GA 1 (200p 100g)'], instances['CP'], 'GA 1 (200p 100g)', 'CP')

    save_plot('GA_2_100_200_vs_GA_2_200_100', instances['GA 2 (100p 200g)'], instances['GA 2 (200p 100g)'], 'GA 2 (100p 200g)', 'GA 2 (200p 100g)')
    save_plot('GA_2_100_200_vs_SCIP', instances['GA 2 (100p 200g)'], instances['SCIP'], 'GA 2 (100p 200g)', 'SCIP')
    save_plot('GA_2_100_200_vs_SAT', instances['GA 2 (100p 200g)'], instances['SAT'], 'GA 2 (100p 200g)', 'SAT')
    save_plot('GA_2_100_200_vs_CP', instances['GA 2 (100p 200g)'], instances['CP'], 'GA 2 (100p 200g)', 'CP')

    save_plot('GA_2_200_100_vs_SCIP', instances['GA 2 (200p 100g)'], instances['SCIP'], 'GGA2V2', 'SCIP')
    save_plot('GA_2_200_100_vs_SAT', instances['GA 2 (200p 100g)'], instances['SAT'], 'GGA2V2', 'SAT')
    save_plot('GA_2_200_100_vs_CP', instances['GA 2 (200p 100g)'], instances['CP'], 'GGA2V2', 'CP')

    save_plot('SCIP_vs_SAT', instances['SCIP'], instances['SAT'], 'SCIP', 'SAT')
    save_plot('SCIP_vs_CP', instances['SCIP'], instances['CP'], 'SCIP', 'CP')

    save_plot('SAT_vs_CP', instances['SAT'], instances['CP'], 'SAT', 'CP')