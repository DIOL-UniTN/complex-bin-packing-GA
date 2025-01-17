import pandas as pd
import re
from ortools.linear_solver import pywraplp
import holidays

# Funzione per estrarre il numero da una stringa come 'm1', 'm2', .. ,  'm10'
def sort_machines_key(machine_id):
    return int(re.findall(r'\d+', machine_id)[0])


def create_data_model(args, forceint=False):
    # df = pd.read_csv('2020_PatientArrivals_relaxed.csv', sep=';', header=0)
    df = pd.read_csv(f'data/{args.arrivals_file}.csv', sep=';', header=0)
    df_protocols = pd.read_csv('data/Protocols.csv', sep=';', header=0)
    data = {"patients": {},
            "bin_days": {}}
    
    #all_machines = df['MachineID'].unique()
    all_machines = [f"M{i}" for i in range(1, 11)]  # Lista con tutte le macchine ordinate da M1 a M10
    # all_machines = [f"M{i}" for i in range(1, 4)]  # Lista con tutte le macchine ordinate da M1 a M3
    
    all_days = [pd.to_datetime(i, unit='D', origin=pd.Timestamp('01-01-2020')).date() for i in range(365)]
    all_days = [d for d in all_days if d not in holidays.BE(years=2020) and d.weekday() < 5]

    data['day_to_actual_days'] = {i: all_days[i] for i in range(len(all_days))}
    data['actual_days_to_day'] = {all_days[i]: i for i in range(len(all_days))}

    # all_days = df['Start date'].unique()

    for index, row in df.iterrows():
        patient_id = row['PatientID']
        no_fractions = int(row['NoFractions'])
        session_time_first = int(row['SessionTimeFirst'])
        session_time_second = int(row['SessionTimeSecond'])
        protocol = row['RTTreatment']

        patient_sessions = {1: session_time_first}

        for i in range(2, no_fractions + 1):
            patient_sessions[i] = session_time_second

        protocol_row = df_protocols[df_protocols['RTTreatment'] == protocol].iloc[0]  # Trova la riga del protocollo
        available_columns = df_protocols.columns
        machines_available = {f"M{i}" for i in range(1,11) if f'M{i}' in available_columns and protocol_row[f'M{i}'] == 1}
        # Per ordinarle in modo crescente
        machines_available_sorted = sorted(machines_available, key=sort_machines_key)
        data["patients"][patient_id] = {
            "fractions": patient_sessions,
            "machines": machines_available_sorted,
            "arrival_day": data['actual_days_to_day'][pd.to_datetime(row['CreationDate']).date()]
        }

    # df = pd.read_csv('2020_InputScheduleFrom2019_relaxed.csv', sep=';', header=0)
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

    bin_capacity = {}
    for day in all_days:
        for machine in all_machines:
            if (day, machine) in machine_usage:
                # Se la macchina è stata utilizzata, calcola la durata residua
                used_minutes = machine_usage[(day, machine)]
                residual_minutes = total_minutes_per_day - used_minutes
            else:
                # Se la macchina non è stata utilizzata, la durata residua è l'intera giornata (480 minuti)
                residual_minutes = total_minutes_per_day

            if day not in bin_capacity:
                bin_capacity[day] = {}
            bin_capacity[day][machine] = int(residual_minutes) if forceint else residual_minutes

    # Raggruppo le macchine per ogni giorno
    #days = df.groupby('Start date')['MachineID'].apply(lambda x: list(x.unique())).to_dict()

    # Converto i giorni sequenzialmente
    #days = {i: days[day] for i, day in enumerate(days)}
    #days = {i: sorted(all_machines, key=sort_machines_key) for i in range(len(all_days))}

    bin_capacity_sorted = {}

    # Ordiniamo i giorni (le chiavi di bin_capacity) in ordine crescente
    total_fractions = sum([len(item['fractions']) for item in data["patients"].values()])

    index = 0
    for day in sorted(bin_capacity):
        bin_capacity_sorted[index] = {machine: bin_capacity[day][machine] for machine in
                                    sorted(bin_capacity[day], key=sort_machines_key)}
        index += 1
        if index >= total_fractions:
            break

    #data['days'] = days
    data['bin_days'] = bin_capacity_sorted
    """
    # Provo ad estrarre la capacità residua di una macchina in un determinato giorno
    day = pd.to_datetime('2020-01-02').date()
    machine_id = 'M8'
    if day in bin_capacity and machine_id in bin_capacity[day]:
        capacity = bin_capacity[day][machine_id]
        print(f"La capacità residua della macchina {machine_id} nel giorno {day} è di {capacity} minuti.")
    else:
        print(f"Nessuna capacità trovata per la macchina {machine_id} nel giorno {day}.")
    """

    #print(data)
    return data