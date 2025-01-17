import argparse
from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model
from data_manipulation import create_data_model
import dill
from ortools.sat.sat_parameters_pb2 import SatParameters

parser = argparse.ArgumentParser(description='Plot fitnesses of same encoding but different seeds.')

parser.add_argument('-f', dest='arrivals_file', action='store',
                    help='File of patient arrivals (must be in folder "data")', default='instances/2020_PatientArrivals_instance_1')
parser.add_argument('-s', dest='save_file', action='store',
                    help='File of patient arrivals (must be in folder "data")', default='ILP_instance_1')

args = parser.parse_args()

def main(args):
    data = create_data_model(args, forceint=True)

    # print(data["bin_days"])
    # exit(1)
    # Create the CP solver.
    model = cp_model.CpModel()
    solver = cp_model.CpSolver()
    #solver.parameters.num_search_workers = 8

    if not solver or not model:
        return

    # Variables
    # x[j,k,i,d] = 1 if item j of patient k is packed in bin i of day d.
    x = {}
    for k, item_k in data["patients"].items():
        for j in item_k["fractions"]:
            for d, bin_d in data["bin_days"].items():
                for i in bin_d:
                    x[(j, k, i, d)] = model.NewIntVar(0, 1, f"x_{j}_{k}_{i}_{d}")

    # y[i, d] = 1 if bin i is used in day d.
    y = {}
    for d, bin_d in data["bin_days"].items():
        for i in bin_d:
            y[(i, d)] = model.NewIntVar(0, 1, f"y_{i}_{d}")

    # z[d] = 1 if a bin of day d is used
    z = {}
    for d, bin_d in data["bin_days"].items():
        z[d] = model.NewIntVar(0, 1, f"z_{d}")

    # Constraints
    # Each item of each patient must be in exactly one bin in one day.
    for k, item_k in data["patients"].items():
        for j in item_k["fractions"]:
            model.Add(sum(x[j, k, i, d] for i in bin_d for d, bin_d in data["bin_days"].items()) == 1)

    # Z[d] is 1 if a bin of day d is used (z[d] = min(1, sum(y[i, d] for i in bin_d)) linearized)
    for d, bin_d in data["bin_days"].items():
        model.Add(sum(y[i, d] for i in bin_d) <= len(bin_d) * z[d])
        model.Add(1 - sum(y[i, d] for i in bin_d) <= len(bin_d) * (1 - z[d]))

    # The amount packed in each bin cannot exceed its capacity.
    for d, bin_d in data["bin_days"].items():
        for i in bin_d:
            t = {}
            for k, item_k in data["patients"].items():
                for j in item_k["fractions"]:
                    t[(k,j)] = model.NewIntVar(0, 1000000, f"t1_{k}_{j}")
                    model.AddMultiplicationEquality(t[(k,j)], [x[(j, k, i, d)], data["patients"][k]["fractions"][j] ])
            # v = model.NewIntVar(0, 10000000, f"t2_{i}_{d}")
            # model.AddMultiplicationEquality(v, [y[(i,d)]], [data["bin_days"][d][i]])
            model.Add(sum(t[(k,j)] for k, item_k in data["patients"].items()
                                    for j in item_k["fractions"]) <=  data["bin_days"][d][i] * y[(i,d)])
            #print(f"Aggiunto vincolo per : day={d}, machine={i}, day_actual={day_actual}")

    # Items must be packed consecutively day by day: item j before item j+1
    for k, item_k in data["patients"].items():
        for j in item_k["fractions"]:
            for d, bin_d in data["bin_days"].items():
                if ((j + 1, k, i, d + 1) in x):
                    model.Add(
                        sum(x[(j, k, i, d)] for i in bin_d) ==
                        sum(x[(j + 1, k, i, d + 1)] for i in bin_d)
                    )

    # Each fraction j of patient k must be packed in the allowed bins for each day d
    for k, item_k in data["patients"].items():
        for j in item_k["fractions"]:
            for d, bin_d in data["bin_days"].items():
                model.Add(
                    sum(x[(j, k, i, d)] for i in bin_d if i not in item_k["machines"]) == 0
                )

    # Each patient cannot be scheduled on a day before their arrival
    for k, item_k in data["patients"].items():
        for j in item_k["fractions"]:
            for d, bin_d in {d: bin_d for d, bin_d in data["bin_days"].items() if d <item_k["arrival_day"]}.items():
                model.Add(sum(x[(j, k, i, d)] for i in bin_d) == 0)

    # Objective: minimize the number of days used
    # objective = model.NewIntVar(0, 100000, "objective")
    # model.Add(sum(z[d] * (d+1) for d, bin_d in data["bin_days"].items()) == objective)
    # model.minimize(objective)
    model.Minimize(sum(z[d] * (d+1) for d, bin_d in data["bin_days"].items()))
    print(f"Solving with CP-SAT solver")

    solver.parameters.max_time_in_seconds = 3600
    solver.parameters.num_search_workers = 8
    # solver.parameters.log_search_progress = True
    solver.parameters.cp_model_presolve = True
    solver.parameters.enumerate_all_solutions = False
    # print(dir(solver.parameters))
    solver.parameters.binary_minimization_algorithm = SatParameters.BINARY_MINIMIZATION_FIRST_WITH_TRANSITIVE_REDUCTION
    solver.parameters.search_branching = cp_model.PORTFOLIO_SEARCH
    solver.parameters.use_lns = True

    status = solver.Solve(model)

    print(f"Status: {solver.StatusName(status)}")

    with open(f"{args.save_file}.txt", "w") as outfile:
        save_dict = {}
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            num_days = 0
            delays = {}
            for d, bin_d in data["bin_days"].items():
                num_bins = 0
                for i in bin_d:
                    if solver.value(y[(i, d)]) == 1:
                        if str(data["day_to_actual_days"][d]) not in save_dict:
                            save_dict[str(data["day_to_actual_days"][d])] = {}
                        save_dict[str(data["day_to_actual_days"][d])][i] = []
                        bin_items = []
                        bin_weight = 540-data["bin_days"][d][i]
                        for k, item_k in data["patients"].items():
                            for j in item_k["fractions"]:
                                if solver.value(x[j, k, i, d]) > 0:
                                    bin_items.append((j, k))
                                    save_dict[str(data["day_to_actual_days"][d])][i].append({'patient': k, 'fraction': j})
                                    bin_weight += item_k["fractions"][j]
                                    if j == 1:
                                        delays[k] = d - item_k["arrival_day"]
                        if bin_items:
                            num_bins += 1
                            ttt = data["day_to_actual_days"][d]
                            outfile.write(f"Bin number {i}, day {ttt}")
                            outfile.write(f"\n  Items packed: {bin_items}")
                            outfile.write(f"\n  Total weight: {bin_weight}\n")
                if num_bins > 0:
                    num_days = d+1
            outfile.write(f"\nNumber of days used: {num_days}")
            save_dict['num_days'] = num_days
            save_dict['solver_time'] = solver.WallTime()
            status_str = "feasible" if status == cp_model.FEASIBLE else "optimal"
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