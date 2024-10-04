# messy for now, just enough to make this work. 
import os
import numpy as np
import json
import matplotlib.pyplot as plt
from utils import *


def load_phot_data(PlanetName, ObservationDate, TransitDirectory, ExoticOutputDirectory):
        txt_name = f"AAVSO_{PlanetName}_{ObservationDate}.txt"
        data_directory = os.path.join(TransitDirectory, ExoticOutputDirectory)
        phot_data = np.loadtxt(os.path.join(data_directory, txt_name), delimiter=",")
        return {"BJD_TDB" : phot_data[:, 0], 
                "flux" : phot_data[:, 1], 
                "error" : phot_data[:, 2]}

def parse_final_params(PlanetName, ObservationDate, TransitDirectory, ExoticOutputDirectory):
        txt_name = f"AAVSO_{PlanetName}_{ObservationDate}.txt"
        data_directory = os.path.join(TransitDirectory, ExoticOutputDirectory)     
        with open(os.path.join(data_directory, txt_name)) as fn:
            for line in fn: 
                if line.startswith("#RESULTS-XC"):
                    # extract the JSON-like string part
                    json_str = line.split("=", 1)[1].strip()
                    # parse the JSON string
                    results_xc_data = json.loads(json_str)
        param_dict = dict()
        Tmid = results_xc_data["Tc"]  # NOTE: units are BJD_TBD
        param_dict["Tmid"] = float(Tmid["value"])
        param_dict["Tmid_unc"] = float(Tmid["uncertainty"])
        rp = results_xc_data["Rp/R*"]
        param_dict["Rp/R*"] = float(rp["value"])
        param_dict["Rp/R*_unc"] = float(rp["uncertainty"])
        a = results_xc_data["a/R*"]
        param_dict["a/R*"] = float(a["value"])
        param_dict["a/R*_unc"] = float(a["uncertainty"])
        Am1 = results_xc_data["Am1"]
        param_dict["Am1"] = float(Am1["value"])
        param_dict["Am1_unc"] = float(Am1["uncertainty"])
        Am2 = results_xc_data["Am2"]
        param_dict["Am2"] = float(Am2["value"])
        param_dict["Am2_unc"] = float(Am2["uncertainty"])
        dur = results_xc_data["Duration"]
        param_dict["Duration"] = float(dur["value"])
        param_dict["Duration_unc"] = float(dur["uncertainty"])
        return param_dict

def calc_model_fit(transit_times, param_dict):
    transit_model = calc_batman_curve(transit_times, param_dict["Tmid"], param_dict["per"], param_dict["Rp/R*"], 
                                      param_dict["a/R*"], param_dict["inc"], param_dict["u"], limb_dark="nonlinear")
    return transit_model

def plot_data_with_curve(PlanetName, ObservationDate, TransitDirectory, ExoticOutputDirectory, y_val, color):
    plt.figure(figsize=(9, 6))
    photdata = load_phot_data(PlanetName, ObservationDate, TransitDirectory, ExoticOutputDirectory)
    # calculate JD
    JD = int(photdata["BJD_TDB"][0])
    time = photdata["BJD_TDB"] - JD
    # calculate model 
    params = parse_final_params(PlanetName, ObservationDate, TransitDirectory, ExoticOutputDirectory)
    model = calc_model_fit(photdata["flux"]+JD, params)
    str = f'Mid-Transit Time (Tmid):\n{params["Tmid"]}+/-{params["Tmid_unc"]}BJD_TDB\nTransit Depth (Rp/R*)^2:\n{params["depth"]}+/-{params["depth_unc"]}'
    plt.text(photdata["flux"][-1,0]+0.0125, y_val, str, fontsize=12, color=color)
    # plot RED data & curve
    plt.errorbar(time, photdata["flux"], yerr=photdata["error"], color=color, marker='.', ls='none', alpha=0.7)
    plt.plot(time, model, lw=3.0, color=color)
    plt.plot(np.repeat(params["Tmid"]-JD,10), np.linspace(0.5, 1.2, 10), alpha=0.9, linestyle="--", color=color, zorder=0, linewidth=1.0) 
    
    plt.title(f"{PlanetName}  {ObservationDate}")
    plt.subplots_adjust(left=0.075, right=0.6, top=0.926, bottom=0.092)
    plt.ylim(0.8, 1.15)
    plt.xlabel(f"Transit Mid-time (BJD_TDB) -{JD}")
    plt.ylabel("Relative Flux")


def plot_multiple_curves(PlanetName, ObservationDate, TransitDirectory, compile_list):
    y_val = 1.38
    colors = [BoiseState_blue, BoiseState_orange, "g", ]
    for color, data_set in colors, compile_list:
        y_val -= 0.23
        plot_data_with_curve(PlanetName, ObservationDate, os.path.join(TransitDirectory, data_set), "output_green", y_val, color)
    
    plt.savefig(f"Compiled_LC_{PlanetName}_{ObservationDate}.png", dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    home_dir = os.path.expanduser('~')
    maintransit_dir = os.path.join(home_dir, "TrES-3b_85")
    planet_name = "TrES-3 b"
    date = "05-08-2024"
    compile_list = ["Annie", "Hypatia", "Melba"]