import pandas as pd
import numpy as np

def get_data_info():
    df = pd.read_csv('data/2020_PatientArrivals.csv', sep=';', header=0)

    patient_count_per_day = df.groupby('CreationDate').size().to_dict()

    patient_count_mean = np.mean(list(patient_count_per_day.values()))

    df_2019 = pd.read_csv('data/2020_InputScheduleFrom2019.csv', sep=';', header=0)
    df_2019['StartAppDate'] = pd.to_datetime(df_2019['Start time of appointment']).dt.date

    schedule_count_per_day = df_2019.groupby('StartAppDate').size().to_dict()

    schedule_count_mean = np.mean(list(schedule_count_per_day.values()))

    return patient_count_per_day, patient_count_mean, schedule_count_per_day, schedule_count_mean

def get_reduced_data_info():
    df = pd.read_csv('data/2020_PatientArrivals_relaxed.csv', sep=';', header=0)

    patient_count_per_day = df.groupby('CreationDate').size().to_dict()

    patient_count_mean = np.mean(list(patient_count_per_day.values()))

    df_2019 = pd.read_csv('data/2020_InputScheduleFrom2019_relaxed.csv', sep=';', header=0)
    df_2019['StartAppDate'] = pd.to_datetime(df_2019['Start time of appointment']).dt.date

    schedule_count_per_day = df_2019.groupby('StartAppDate').size().to_dict()

    schedule_count_mean = np.mean(list(schedule_count_per_day.values()))

    print(patient_count_per_day)
    print(schedule_count_per_day)
    print(patient_count_mean, schedule_count_mean)

if __name__ == '__main__':
    get_reduced_data_info()