import pandas as pd
import re
import numpy as np
import json
import matplotlib.pyplot as plt
import scienceplots
import holidays

import matplotlib.dates as mdates

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def sort_machines_key(machine_id):
    return int(re.findall(r'\d+', machine_id)[0])

def get_patient_by_day():
    df = pd.read_csv(f'data/2020_PatientArrivals.csv', sep=';', header=0)
    df_protocols = pd.read_csv('data/Protocols.csv', sep=';', header=0)
    df = df.sort_values(["CreationDate", "PatientID"])
    
    data = {}

    for index, row in df.iterrows():
        patient_id = row['PatientID']
        no_fractions = int(row['NoFractions'])
        session_time_first = int(row['SessionTimeFirst'])
        session_time_second = int(row['SessionTimeSecond'])
        protocol = row['RTTreatment']

        protocol_row = df_protocols[df_protocols['RTTreatment'] == protocol].iloc[0]  # Trova la riga del protocollo
        available_columns = df_protocols.columns
        machines_available = {f"M{i}" for i in range(1,11) if f'M{i}' in available_columns and protocol_row[f'M{i}'] == 1}
        # Per ordinarle in modo crescente
        machines_available_sorted = sorted(machines_available, key=sort_machines_key)
        date_format = str(pd.to_datetime(row['CreationDate']).date())
        if date_format not in data:
            data[date_format] = {
                "patients": {},
                "count" : 0
            }

        data[date_format]["patients"][patient_id] = {
            "fractions": no_fractions,
            "first_fraction_duration": session_time_first,
            "fractions_duration": session_time_second,
            "machines": machines_available_sorted
        }
        data[date_format]["count"] += 1

    return data 

def save_json(data):
    max_patients = (0,None)
    min_patients = (1000,None)
    for key, value in data.items():
        if value["count"] > max_patients[0]:
            max_patients = value["count"], key
        if value["count"] < min_patients[0]:
            min_patients = value["count"], key
        fractions = [patient["fractions"] for patient in value["patients"].values()]
        data[key]["fractions_average"] = np.mean(fractions)
        data[key]["max_fractions"] = np.max(fractions)
        data[key]["min_fractions"] = np.min(fractions)
        machines = [len(patient["machines"]) for patient in value["patients"].values()]
        data[key]["machines_average"] = np.mean(machines)
        data[key]["max_machines"] = np.max(machines)
        data[key]["min_machines"] = np.min(machines)

    print(max_patients)
    print(min_patients)

    data = dict(sorted(data.items(), key=lambda item: item[1]["count"]))

    keys = list(data)[0:3] + list(data)[len(data)-3:len(data)]

    data = dict(sorted(data.items(), key=lambda item: item[1]["max_fractions"]))

    keys = keys + list(data)[0:3] + list(data)[len(data)-3:len(data)]

    data = dict(sorted(data.items(), key=lambda item: item[1]["max_machines"]))

    keys = keys + list(data)[0:3] + list(data)[len(data)-3:len(data)]
    print(keys)
    print(set(keys))
    duplicates = {}
    for key in keys:
        if key not in duplicates:
            duplicates[key] = 0
        duplicates[key] += 1
        with open(f"data/instances.json", "w") as outfile:
            json.dump(data, outfile, cls=NpEncoder)

    with open(f"data/instances.json", "w") as outfile:
        json.dump(data, outfile, cls=NpEncoder)

    print(duplicates)

    return data

def plot_patients(data):
    plt.style.use(['science', 'nature', 'muted'])
    data = dict(sorted(data.items(), key=lambda item: item[0]))
    fig, ax = plt.subplots(figsize=(10, 2))
    #plt.plot(x, y, 'o')
    ax.plot(data.keys(), [val['count'] for val in data.values()], 'o')
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=range(1,13,2)))
    ax.set_xlabel('Days', fontsize=14)
    ax.set_ylabel('Patients count', fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=12)

    fig.savefig("patients_count.pdf", format="pdf", dpi=1200)
    plt.close()

def get_occupation():
    all_machines = [f"M{i}" for i in range(1, 11)]
    
    all_days = [pd.to_datetime(i, unit='D', origin=pd.Timestamp('01-01-2020')).date() for i in range(200)]
    all_days = [d for d in all_days if d not in holidays.BE(years=2020) and d.weekday() < 5]

    df = pd.read_csv('data/2020_InputScheduleFrom2019.csv', sep=';', header=0)

    df['Start time of appointment'] = pd.to_datetime(df['Start time of appointment'])
    df['End time of appointment'] = pd.to_datetime(df['End time of appointment'])
    df['Start date'] = df['Start time of appointment'].dt.date

    # Assumo che una macchina venga utilizzata per 4 ore al giorno (240 minuti)
    #total_minutes_per_day = 480
    total_minutes_per_day = 540
    machine_usage = df.groupby(['Start date', 'MachineID']).apply(
        lambda x: (x['End time of appointment'] - x['Start time of appointment']).sum().total_seconds() / 60
        , include_groups=False).to_dict()

    machine_minutes_used = {}
    for machine in all_machines:
        machine_minutes_used[machine] = {}
        for day in all_days:
            if (day, machine) in machine_usage:
                # Se la macchina è stata utilizzata, calcola la durata residua
                machine_minutes_used[machine][str(day)] = machine_usage[(day, machine)]
            else:
                machine_minutes_used[machine][str(day)] = 0
    
    return machine_minutes_used

def plot_machines(machines):
    plt.style.use(['science', 'nature', 'muted'])

    fig, ax = plt.subplots(figsize=(10, 3))
    for m_key, mac in machines.items():
        x = mac.keys()
        y = [(minutes*100)/540 for minutes in mac.values()]
        ax.plot(x, y, label=m_key)
    
    ax.legend(title='Machines')

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.set_yticks(range(0, 101, 20))
    ax.set_xlabel('Days', fontsize=14)
    ax.set_ylabel('Machine Occupation', fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=12)

    fig.savefig("machine_occupation.pdf", format="pdf", dpi=1200)
    plt.close()

def plot_box_plot(data):

    plt.style.use(['science', 'nature', 'muted'])

    boxes = [
        [patient["fractions"] for key, value in data.items() for patient in value["patients"].values()],
        [value["count"] for key, value in data.items()],
        [len(patient["machines"]) for key, value in data.items() for patient in value["patients"].values()],
    ]
    labels = ['fractions', 'patient count', 'machines']
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    
    medianprops = dict(linewidth=1.5, color='black')
    
    fig, ax = plt.subplots()
    ax.set_ylabel('frequence')

    bplot = ax.boxplot(boxes,
                    patch_artist=True,  # fill with color
                    tick_labels=labels,
                    medianprops=medianprops)  # will be used to label x-ticks

    # fill with colors
    for patch, color in zip(bplot['boxes'], colors):
        patch.set_facecolor(color)
    plt.savefig("boxplots.pdf", format="pdf")
    #plt.show()

if __name__ == "__main__":
    data = get_patient_by_day()
    data = save_json(data)
    machines = get_occupation()
    plot_box_plot(data)
    plot_patients(data)
    plot_machines(machines)