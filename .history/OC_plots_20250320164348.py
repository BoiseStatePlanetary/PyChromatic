import os
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
from utils import *
from pprint import pprint
from susie.timing_data import TimingData
from susie.ephemeris import Ephemeris

def read_exoWatch_json_data(json_file):
    with open(json_file) as f: 
        json_data = json.load(f)
        period = json_data["priors"]["Period"]["value"]
        T0 = json_data["priors"]["Tc"]["value"]
        ephem_dict = json_data['ephemeris']
        epochs_1 = ephem_dict["nea_epochs"]
        mid_times = [float(x) for x in ephem_dict["nea_tmids"]]
        mid_times_err = [float(x) for x in ephem_dict["nea_tmids_err"]]
        src_flg = ["NASA Exoplanet Archive"] * len(mid_times)
        epochs_str = epochs_1 + ephem_dict["epochs"]
        epoch_float = [float(x) for x in epochs_str]
        epochs = np.array(epoch_float, dtype="int")
        obs_dict = json_data["observations"]
        for obs in obs_dict:
            if obs["data_flag_ephemeris"] == True: 
                # print(obs.keys())
                dat = obs["parameters"]
                mid_times.append(float(dat['Tc']))
                mid_times_err.append(float(obs["errors"]["Tc"]))
                # observers.append(obs["obscode"]["id"])
                if len(obs["secondary_obscodes"]) == 0:
                    src_flg.append("AAVSO")
                else:
                    for observer in obs["secondary_obscodes"]:
                        if observer["id"] == "UNIS":
                            src_flg.append("Unistellar")
                        elif observer["id"] == "MOBS":
                            src_flg.append("MOBS/EXOTIC")
        # print(list(dict.fromkeys(sec_observers)))
        # print(len(list(dict.fromkeys(observers))))
        # print(ephem_dict["Tcs"])
        # print(mid_times)
        return epochs, np.array(mid_times), np.array(mid_times_err), src_flg, float(period), float(T0)
    
def read_Elisbeth_data(file_name):
    data = pd.read_csv(file_name, comment='#', header=0)
    # print(data.columns)
    epochs = np.array(data["N_tr"].astype('int'))
    mid_times = np.array(data["Midtime"])
    mid_times_errs = np.array(data["Midtime_err_days"])
    return epochs, mid_times, mid_times_errs

def read_Athano22_data(file_name="Athano2022_Table6.csv"):
    data = pd.read_csv(file_name, comment='#', header=0)
    # print(data.columns)
    epochs = np.array(data["Epoch"].astype('int'))
    # For A-thano+ 2022 the mid-ties must be corrected. they are in -2450000 BJD_TDB
    mid_times = np.array(data["Tm"])
    adjusted_midtimes = mid_times + 2450000
    mid_times_errs = np.array(data["sigma_Tm"])
    src_flg = ["Athano+ 2022"] * len(epochs)
    return epochs, adjusted_midtimes, mid_times_errs

def get_epochs(T, T0, P, E0=0):
    """
    T: float
        Mid-time for your new point
    T0: float
        The mid-time of the very first epoch (corresponding to epoch=0)
    P: float
        Orbital period
    E0: int
        The first epoch number, if not zero. Will be added to make sure initial epoch number is accounted for
    """
    N = (T-T0)/P
    return int(N + E0)

#instantiate susie object
def make_susie_plot(json_file, csv_file):
    epochs, mid_times, mid_time_err, src_flg, period, T0 = read_exoWatch_json_data(json_file)
    epochs2, mid_times2, mid_time_errs2 = read_Elisbeth_data(csv_file)
    E_src_flg = ["Elisabeth's Data"] * len(epochs2)
    new_epochs = np.array([get_epochs(m, T0, period) for m in np.hstack((mid_times, mid_times2))]) # recalculate epochs given Tc prior from EXOTIC
    sort_idx = np.argsort(new_epochs)
    all_midtimes = np.hstack((mid_times, mid_times2))
    all_err = np.hstack((mid_time_err, mid_time_errs2))    
    timing_obj = TimingData('jd', new_epochs[sort_idx], all_midtimes[sort_idx], all_err[sort_idx], time_scale='tdb')
    timing_obj = TimingData('jd', epochs2, mid_times2, mid_time_errs2, time_scale="tdb")
    ephemeris_obj = Ephemeris(timing_obj)
    ax = ephemeris_obj.plot_oc_plot("quadratic")
    oc_vals = ephemeris_obj.oc_vals
    epochs = ephemeris_obj.timing_data.epochs
    all_src_flgs = np.hstack((src_flg, E_src_flg))
    colors = {'NASA Exoplanet Archive': 'b', 
              'AAVSO': 'g', 
              'Unistellar': 'r',
              'MOBS/EXOTIC': 'y', 
              "Elisabeth's Data" : 'k'}
    for data_point, time, src in zip(epochs, oc_vals, all_src_flgs[sort_idx]):
        ax.scatter(data_point, time, label=src, color=colors[src], zorder=110)
    handles, labels = ax.get_legend_handles_labels()
    unique_labels = set(labels)
    handles = [handles[labels.index(label)] for label in unique_labels]
    labels = list(unique_labels)
    ax.legend(handles, labels)
    plt.show()

    ephemeris_obj.plot_running_delta_bic("linear", "quadratic")
    plt.show()

def susie_for_exowatch_only(json_file):
    epochs, mid_times, mid_time_err, src_flg, period, T0 = read_exoWatch_json_data(json_file)   
    timing_obj = TimingData('jd', epochs, mid_times, mid_time_err, time_scale='tdb')
    ephemeris_obj = Ephemeris(timing_obj)
    ax = ephemeris_obj.plot_oc_plot("quadratic")
    oc_vals = ephemeris_obj.oc_vals
    epochs = ephemeris_obj.timing_data.epochs
    colors = {'NASA Exoplanet Archive': 'b', 
              'AAVSO': 'g', 
              'Unistellar': 'r',
              'MOBS/EXOTIC': 'y'}
    for data_point, time, src in zip(epochs, oc_vals, src_flg):
        ax.scatter(data_point, time, label=src, color=colors[src], zorder=110)
    handles, labels = ax.get_legend_handles_labels()
    unique_labels = set(labels)
    handles = [handles[labels.index(label)] for label in unique_labels]
    labels = list(unique_labels)
    ax.legend(handles, labels)
    plt.show()

    ephemeris_obj.plot_running_delta_bic("linear", "quadratic")
    plt.show()

def make_susie_plot_Athano_exowatch(json_file):
    epochs, mid_times, mid_time_err, src_flg, period, T0_no = read_exoWatch_json_data(json_file)
    epochs2, mid_times2, mid_time_errs2, src_flg2 = read_Athano22_data()
    T0 = 24
    new_epochs = np.array([get_epochs(m, T0, period) for m in np.hstack((mid_times, mid_times2))]) # recalculate epochs given Tc prior from EXOTIC
    sort_idx = np.argsort(new_epochs)
    all_midtimes = np.hstack((mid_times, mid_times2))
    all_err = np.hstack((mid_time_err, mid_time_errs2))    
    timing_obj = TimingData('jd', new_epochs[sort_idx], all_midtimes[sort_idx], all_err[sort_idx], time_scale='tdb')
    timing_obj = TimingData('jd', epochs2, mid_times2, mid_time_errs2, time_scale="tdb")
    ephemeris_obj = Ephemeris(timing_obj)
    ax = ephemeris_obj.plot_oc_plot("quadratic")
    oc_vals = ephemeris_obj.oc_vals
    epochs = ephemeris_obj.timing_data.epochs
    all_src_flgs = np.hstack((src_flg, src_flg2))
    colors = {'NASA Exoplanet Archive': 'b', 
              'AAVSO': 'g', 
              'Unistellar': 'r',
              'MOBS/EXOTIC': 'y', 
              "Elisabeth's Data" : 'k'}
    for data_point, time, src in zip(epochs, oc_vals, all_src_flgs[sort_idx]):
        ax.scatter(data_point, time, label=src, color=colors[src], zorder=110)
    handles, labels = ax.get_legend_handles_labels()
    unique_labels = set(labels)
    handles = [handles[labels.index(label)] for label in unique_labels]
    labels = list(unique_labels)
    ax.legend(handles, labels)
    plt.show()

    ephemeris_obj.plot_running_delta_bic("linear", "quadratic")
    plt.show()

if __name__ == "__main__":
    json_name = "WASP-52 b.json"
    elisabeth_file = "oMinusC_WASP-52b.csv"
    # make_susie_plot(json_name, elisabeth_file)

    hatp37_exowatch = "HAT-P-37 b.json"
    # susie_for_exowatch_only(hatp37_exowatch)
    dat = read_Athano22_data()
    print(dat)
    
