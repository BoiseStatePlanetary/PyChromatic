# messy for now, just enough to make this work. 
import os
import numpy as np
import json
import matplotlib.pyplot as plt
from utils import *

# Use load_phot_data, parse_final_params, calc_model_fit, and plot_data_with_curve 
def load_phot_data(PlanetName, ObservationDate, TransitDirectory, data_set):
        txt_name = f"AAVSO_{PlanetName}_{ObservationDate}_{data_set}.txt"
        phot_data = np.loadtxt(os.path.join(TransitDirectory, txt_name), delimiter=",")
        return {"BJD_TDB" : phot_data[:, 0], 
                "flux" : phot_data[:, 1], 
                "error" : phot_data[:, 2]}

def parse_final_params(PlanetName, ObservationDate, TransitDirectory, data_set):
        txt_name = f"AAVSO_{PlanetName}_{ObservationDate}_{data_set}.txt"    
        with open(os.path.join(TransitDirectory, txt_name)) as fn:
            for line in fn: 
                if line.startswith("#RESULTS-XC"):
                    # extract the JSON-like string part
                    json_str = line.split("=", 1)[1].strip()
                    # parse the JSON string
                    results_xc_data = json.loads(json_str)
                elif line.startswith("#PRIORS-XC"):
                     # extract the JSON-like string part
                    json_str = line.split("=", 1)[1].strip()
                    # parse the JSON string
                    priors_xc_data = json.loads(json_str)
        param_dict = dict()
        Tmid = results_xc_data["Tc"]  # NOTE: units are BJD_TBD
        param_dict["Tmid"] = float(Tmid["value"])
        param_dict["Tmid_unc"] = float(Tmid["uncertainty"])
        rp = results_xc_data["Rp/R*"]
        param_dict["Rp/R*"] = float(rp["value"])
        param_dict["Rp/R*_unc"] = float(rp["uncertainty"])
        a = priors_xc_data["a/R*"]
        param_dict["a/R*"] = float(a["value"])
        param_dict["a/R*_unc"] = float(a["uncertainty"])
        per = priors_xc_data["Period"]
        param_dict["per"] = float(per["value"])
        param_dict["per_unc"] = float(per["uncertainty"])
        Am1 = results_xc_data["Am1"]
        param_dict["Am1"] = float(Am1["value"])
        param_dict["Am1_unc"] = float(Am1["uncertainty"])
        Am2 = results_xc_data["Am2"]
        param_dict["Am2"] = float(Am2["value"])
        param_dict["Am2_unc"] = float(Am2["uncertainty"])
        dur = results_xc_data["Duration"]
        param_dict["Duration"] = float(dur["value"])
        param_dict["Duration_unc"] = float(dur["uncertainty"])
        inc = priors_xc_data["inc"]
        param_dict["inc"] = float(inc["value"])
        param_dict["inc_unc"] = float(inc["uncertainty"])
        ecc = priors_xc_data["ecc"]
        param_dict["ecc"] = float(ecc["value"])
        param_dict["ecc_unc"] = ecc["uncertainty"]
        param_dict["u"] =[float(priors_xc_data["u0"]["value"]), float(priors_xc_data["u1"]["value"]),
                        float(priors_xc_data["u2"]["value"]), float(priors_xc_data["u3"]["value"])]   
        return param_dict

def calc_model_fit(transit_times, param_dict):
    transit_model = calc_batman_curve(transit_times, param_dict["Tmid"], param_dict["per"], param_dict["Rp/R*"], 
                                      param_dict["a/R*"], param_dict["inc"], param_dict["u"], limb_dark="nonlinear")
    return transit_model

def plot_data_with_curve(PlanetName, ObservationDate, TransitDirectory, data_set, color, shift):
    photdata = load_phot_data(PlanetName, ObservationDate, TransitDirectory, data_set)
    # calculate JD
    JD = int(photdata["BJD_TDB"][0])
    time = photdata["BJD_TDB"] - JD
    # calculate model 
    params = parse_final_params(PlanetName, ObservationDate, TransitDirectory, data_set)
    model = calc_model_fit(photdata["BJD_TDB"], params)
    str = f'Mid-Transit Time (Tmid):\n{params["Tmid"]-JD:.6f}+/-{params["Tmid_unc"]:.6f}BJD_TDB \n Rp/R*: {params["Rp/R*"]} +/- {params["Rp/R*_unc"]}'
    plt.text(time[-1]+0.0125, 1+shift, str, fontsize=12, color=color)
    
    plt.errorbar(time, photdata["flux"]+shift, yerr=photdata["error"], color=color, marker='.', markersize=5, ls='none', alpha=0.3, label=data_set)
    plt.plot(time, model+shift, lw=3.0, color=color)
    tmid_x = np.repeat(params["Tmid"]-JD,10)
    tmid_y = np.linspace(0.85, 1.6, 10)
    plt.plot(tmid_x, tmid_y, alpha=0.9, linestyle="--", color=color, zorder=0, linewidth=1.0)
    plt.fill_betweenx(tmid_y, tmid_x - params["Tmid_unc"], tmid_x + params["Tmid_unc"], color=color, alpha=0.5) 
    
    plt.title(f"{PlanetName}  {ObservationDate}")
    plt.legend()
    plt.ylim(0.875, 1.05)
    plt.subplots_adjust(left=0.065, right=0.6, top=0.926, bottom=0.092)
    plt.xlabel(f"Transit Mid-time (BJD_TDB) -{JD}")
    plt.ylabel("Relative Flux")

def plot_data(PlanetName, ObservationDate, TransitDirectory, data_set, color, shift):
    photdata = load_phot_data(PlanetName, ObservationDate, TransitDirectory, data_set)
    # calculate JD
    JD = int(photdata["BJD_TDB"][0])
    time = photdata["BJD_TDB"] - JD
    plt.errorbar(time, photdata["flux"]+shift, yerr=photdata["error"], color=color, marker='.', ls='none', alpha=0.7, label=data_set)
    # plt.plot(np.repeat(params["Tmid"]-JD,10), np.linspace(0.5, 1.2, 10), alpha=0.9, linestyle="--", color=color, zorder=0, linewidth=1.0)
 
def plot_diff(PlanetName, ObservationDate, TransitDirectory, data_sets, standard, color, shift):
    #load data from the observation that data will be subtracted from. The "standard"
    standard_dat = load_phot_data(PlanetName, ObservationDate, TransitDirectory, standard)
    for idx, data in enumerate(data_sets):
        photdata = load_phot_data(PlanetName, ObservationDate, TransitDirectory, data)
        new_JD = int(photdata["BJD_TDB"][0]) 
        new_time = photdata["BJD_TDB"] - new_JD
        y = photdata["flux"] - standard_dat["flux"]
        plt.plot(new_time, y, color=color[idx], marker='.', ls='none', alpha=0.7, label=f"{data} - {standard}")
        plt.plot(np.linspace(new_time[0], new_time[-1], 25), np.repeat(0, 25), color=color[idx], marker=None)
    plt.title("Calibration Difference Plot")
    plt.legend()
    plt.xlabel(f"Transit Mid-time (BJD_TDB) -{new_JD}")
    plt.ylabel("Difference in Rel. Flux")
    plt.show()

def plot_diff_from_curve(PlanetName, ObservationDate, TransitDirectory, data_set, color, shift):
    photdata = load_phot_data(PlanetName, ObservationDate, TransitDirectory, data_set)
    # calculate JD
    JD = int(photdata["BJD_TDB"][0])
    time = photdata["BJD_TDB"] - JD
    # calculate model 
    params = parse_final_params(PlanetName, ObservationDate, TransitDirectory, data_set)
    model = calc_model_fit(photdata["BJD_TDB"], params)
    # str = f'Mid-Transit Time (Tmid):\n{params["Tmid"]-JD:.6f}+/-{params["Tmid_unc"]:.6f}BJD_TDB \n Rp/R*: {params["Rp/R*"]} +/- {params["Rp/R*_unc"]}'
    # plt.text(time[-1]+0.0125, 1+shift, str, fontsize=12, color=color)
    
    plt.plot(time, photdata["flux"]-model+shift, color=color, marker='.', markersize=5, ls='none', alpha=0.9, label=data_set)
    plt.plot(time, model+shift, lw=2.0, color=color)
    # tmid_x = np.repeat(params["Tmid"]-JD,10)
    # tmid_y = np.linspace(0.85, 1.6, 10)
    # plt.plot(tmid_x, tmid_y, alpha=0.9, linestyle="--", color=color, zorder=0, linewidth=1.0)
    # plt.fill_betweenx(tmid_y, tmid_x - params["Tmid_unc"], tmid_x + params["Tmid_unc"], color=color, alpha=0.5) 
    
    plt.title(f"{PlanetName}  {ObservationDate} Difference Plot")
    plt.legend()
    plt.ylim(0.875, 1.05)
    plt.subplots_adjust(left=0.065, right=0.6, top=0.926, bottom=0.092)
    plt.xlabel(f"Transit Mid-time (BJD_TDB) -{JD}")
    plt.ylabel("Difference of Rel. Flux")

def plot_multiple_curves(PlanetName, ObservationDate, TransitDirectory, compile_list, shifts, Diff=):
    plt.figure(figsize=(9, 6))
    color_dict = {"barbie" : "k",
                  "renormal_barbie": "fuchsia", 
                  "g" : "g", 
                  "r" : "r", 
                  "b" : "b", 
                  "gray" : "dimgrey", 
                  "d" : "k", 
                  "d_f" : "dimgrey", 
                  "d_f_df" : "navy"}
    for idx, data_set in enumerate(compile_list):
        if data_set == "aiwzhv":
            plot_data(PlanetName, ObservationDate, TransitDirectory, data_set, color_dict[data_set], shifts[idx])
        else:
            plot_data_with_curve(PlanetName, ObservationDate, TransitDirectory, data_set, color_dict[data_set], shifts[idx])
    
    plt.savefig(os.path.join(TransitDirectory, f"Compiled_LC_{PlanetName}_{ObservationDate}.png"), dpi=300, bbox_inches='tight')
    plt.close()
    # plt.show()

if __name__ == "__main__":
    home_dir = os.path.expanduser('~')
    maintransit_dir = os.path.join(home_dir, "TrES-3b_Stacked_615", "AAVSO_reports_grey_calibration")
    planet_name = "TrES-3 b"
    date = "15-06-2024"
    compile_list = ["d", "d_f", "d_f_df"]
    shifts=[-0.05, 0, 0.05, 0.1]
    plot_multiple_curves(planet_name, date, maintransit_dir, compile_list, shifts)
    # plot_diff(planet_name, date, maintransit_dir, ["d_f_df", "d_f"], "d", ["navy", "dimgrey"], [0, 0.05])
