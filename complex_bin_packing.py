import argparse
from ortools.linear_solver import pywraplp
from data_manipulation import create_data_model
import dill


parser = argparse.ArgumentParser(description='Plot fitnesses of same encoding but different seeds.')

parser.add_argument('-f', dest='arrivals_file', action='store',
                    help='File of patient arrivals (must be in folder "data")', default='instances/2020_PatientArrivals_instance_1')
parser.add_argument('-s', dest='save_file', action='store',
                    help='File of patient arrivals (must be in folder "data")', default='ILP_instance_1')
parser.add_argument('-b', dest='backend_solver', action='store',
                    help='ILP solver (either SCIP or SAT)', default='SCIP')

args = parser.parse_args()

def main(args):
    data = create_data_model(args)

    #print(data)
    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver(args.backend_solver)
    #solver.parameters.num_search_workers = 8

    if not solver:
        return

    # Variables
    # x[j,k,i,d] = 1 if item j of patient k is packed in bin i of day d.
    x = {}
    for k, item_k in data["patients"].items():
        for j in item_k["fractions"]:
            for d, bin_d in data["bin_days"].items():
                for i in bin_d:
                    x[(j, k, i, d)] = solver.IntVar(0, 1, f"x_{j}_{k}_{i}_{d}")

    # y[i, d] = 1 if bin i is used in day d.
    y = {}
    for d, bin_d in data["bin_days"].items():
        for i in bin_d:
            y[(i, d)] = solver.IntVar(0, 1, f"y_{i}_{d}")

    # z[d] = 1 if a bin of day d is used
    z = {}
    for d, bin_d in data["bin_days"].items():
        z[d] = solver.IntVar(0, 1, f"z_{d}")

    # Constraints
    # Each item of each patient must be in exactly one bin in one day.
    for k, item_k in data["patients"].items():
        for j in item_k["fractions"]:
            solver.Add(sum(x[j, k, i, d] for i in bin_d for d, bin_d in data["bin_days"].items()) == 1)

    # Z[d] is 1 if a bin of day d is used (z[d] = min(1, sum(y[i, d] for i in bin_d)) linearized)
    for d, bin_d in data["bin_days"].items():
        solver.Add(sum(y[i, d] for i in bin_d) <= len(bin_d) * z[d])
        solver.Add(1 - sum(y[i, d] for i in bin_d) <= len(bin_d) * (1 - z[d]))

    # The amount packed in each bin cannot exceed its capacity.
    for d, bin_d in data["bin_days"].items():
        for i in bin_d:
            solver.Add(
                sum(x[(j, k, i, d)] * data["patients"][k]["fractions"][j]
                    for k, item_k in data["patients"].items()
                    for j in item_k["fractions"]
                    ) <= y[(i,d)] * data["bin_days"][d][i]
            )
            #print(f"Aggiunto vincolo per : day={d}, machine={i}, day_actual={day_actual}")

    # Items must be packed consecutively day by day: item j before item j+1
    for k, item_k in data["patients"].items():
        for j in item_k["fractions"]:
            for d, bin_d in data["bin_days"].items():
                if ((j + 1, k, i, d + 1) in x):
                    solver.Add(
                        sum(x[(j, k, i, d)] for i in bin_d) ==
                        sum(x[(j + 1, k, i, d + 1)] for i in bin_d)
                    )

    # Each fraction j of patient k must be packed in the allowed bins for each day d
    for k, item_k in data["patients"].items():
        for j in item_k["fractions"]:
            for d, bin_d in data["bin_days"].items():
                solver.Add(
                    sum(x[(j, k, i, d)] for i in bin_d if i not in item_k["machines"]) == 0
                )

    # Each patient cannot be scheduled on a day before their arrival
    for k, item_k in data["patients"].items():
        for j in item_k["fractions"]:
            for d, bin_d in {d: bin_d for d, bin_d in data["bin_days"].items() if d <item_k["arrival_day"]}.items():
                solver.Add(
                    sum(x[(j, k, i, d)] for i in bin_d) == 0
                )

    # Objective: minimize the number of days used
    solver.Minimize(solver.Sum([z[d] * (d+1) for d, bin_d in data["bin_days"].items()]))
    print(f"Solving with {solver.SolverVersion()}")
    status = solver.Solve()

    with open(f"{args.save_file}.txt", "w") as outfile:
        save_dict = {}
        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            num_days = 0
            delays = {}
            for d, bin_d in data["bin_days"].items():
                num_bins = 0
                for i in bin_d:
                    if y[(i, d)].solution_value() == 1:
                        if str(data["day_to_actual_days"][d]) not in save_dict:
                            save_dict[str(data["day_to_actual_days"][d])] = {}
                        save_dict[str(data["day_to_actual_days"][d])][i] = []
                        bin_items = []
                        bin_weight = 540-data["bin_days"][d][i]
                        for k, item_k in data["patients"].items():
                            for j in item_k["fractions"]:
                                if x[j, k, i, d].solution_value() > 0:
                                    bin_items.append((j, k))
                                    save_dict[str(data["day_to_actual_days"][d])][i].append({'patient': k, 'fraction': j})
                                    bin_weight += item_k["fractions"][j]
                                    if j == 1:
                                        delays[k] = d - item_k["arrival_day"]
                        if bin_items:
                            num_bins += 1
                            outfile.write(f"Bin number {i}, day {data["day_to_actual_days"][d]}")
                            outfile.write(f"\n  Items packed: {bin_items}")
                            outfile.write(f"\n  Total weight: {bin_weight}\n")
                if num_bins > 0:
                    num_days = d+1
            outfile.write(f"\nNumber of days used: {num_days}")
            save_dict['num_days'] = num_days
            save_dict['solver_time'] = solver.WallTime()
            status_str = "feasible" if status == pywraplp.Solver.FEASIBLE else "optimal"
            outfile.write(f"\nSolution found: {status_str}")
            outfile.write(f"\nTime = {solver.WallTime()} milliseconds")
            outfile.write(f"\n\nDelays: {dict(sorted(delays.items()))}")
        else:
            outfile.write("The problem does not have an optimal solution.")

    with open(f"{args.save_file}.pkl", "wb") as handle:
        dill.dump(save_dict, handle, protocol=dill.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    main(args)
    with open(f"{args.save_file}.pkl", "rb") as f:
        ilp_data = dill.load(f)
        print(ilp_data)