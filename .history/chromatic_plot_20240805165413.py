import json
import csv
import os
import numpy as np
import matplotlib.pyplot as plt
import statistics as stat

from utils import *

home_dir = os.path.expanduser('~')

def load_transit_data(transit_dir, planet_name, date):
    red_data = np.loadtxt(os.path.join(transit_dir, "output_red", f"AAVSO_{planet_name}_{date}.txt"), delimiter=",")
    green_data = np.loadtxt(os.path.join(transit_dir, "output_green", f"AAVSO_{planet_name}_{date}.txt"), delimiter=",")
    blue_data = np.loadtxt(os.path.join(transit_dir, "output_blue", f"AAVSO_{planet_name}_{date}.txt"), delimiter=",")
    return red_data, green_data, blue_data

def parse_final_params(transit_dir, output_dir, json_name, txt_name):
    with open(os.path.join(transit_dir, output_dir, "temp", json_name)) as f:
        final_params_nested = json.load(f)
        final_params = final_params_nested['FINAL PLANETARY PARAMETERS']
    param_dict = dict()
    Tmid = final_params["Mid-Transit Time (Tmid)"].split()  # NOTE: units are BJD_TBD
    param_dict["Tmid"] = float(Tmid[0])
    param_dict["Tmid_unc"] = float(Tmid[2])
    rp = final_params["Ratio of Planet to Stellar Radius (Rp/R*)"].split()
    param_dict["Rp/R*"] = float(rp[0])
    param_dict["Rp/R*_unc"] = float(rp[2])
    a = final_params["Semi Major Axis/Star Radius (a/Rs)"].split()
    param_dict["a/R*"] = float(a[0])
    param_dict["a/R*_unc"] = float(a[2])
    transit_depth = final_params["Transit depth (Rp/Rs)^2"].split()
    param_dict["depth"] = float(transit_depth[0])
    param_dict["depth_unc"] = float(transit_depth[2])
    residuals = final_params["Scatter in the residuals of the lightcurve fit is"].split()
    param_dict["residuals"] = float(residuals[0])
    
    with open(os.path.join(transit_dir, output_dir, txt_name)) as fn:
        for line in fn: 
            if line.startswith("#PRIORS-XC"):
                # extract the JSON-like string part
                json_str = line.split("=", 1)[1].strip()
                # parse the JSON string
                priors_xc_data = json.loads(json_str)
    period = priors_xc_data["Period"]
    param_dict["per"] = float(period["value"])
    param_dict["per_unc"] = float(period["uncertainty"])
    inc = priors_xc_data["inc"]
    param_dict["inc"] = float(inc["value"])
    param_dict["inc_unc"] = float(inc["uncertainty"])
    param_dict["u"] =[float(priors_xc_data["u0"]["value"]), float(priors_xc_data["u1"]["value"]),
                      float(priors_xc_data["u2"]["value"]), float(priors_xc_data["u3"]["value"])]
    return param_dict


# next steps, get fits to plot. Using batman
def calc_model_fit(transit_times, param_dict):
    transit_model = calc_batman_curve(transit_times, param_dict["Tmid"], param_dict["per"], param_dict["Rp/R*"], 
                                      param_dict["a/R*"], param_dict["inc"], param_dict["u"], limb_dark="nonlinear")
    return transit_model

def plot_data_with_curve(transit_dir, planet_name, date):
    plt.figure(figsize=(9, 6))
    red_flux, green_flux, blue_flux = load_transit_data(transit_dir, planet_name, date)
    # calculate JD
    JD = int(red_flux[0,0])
    red_flux[:, 0] -= JD
    green_flux[:, 0] -= JD
    blue_flux[:, 0] -= JD
    # calculate model for RED 
    red_params = parse_final_params(transit_dir, "output_red", f"FinalParams_{planet_name}_{date}.json", f"AAVSO_{planet_name}_{date}.txt")
    red_model = calc_model_fit(red_flux[:, 0]+JD, red_params)
    red_str = f'Mid-Transit Time (Tmid):\n{red_params["Tmid"]}+/-{red_params["Tmid_unc"]}BJD_TDB\nTransit Depth (Rp/R*)^2:\n{red_params["depth"]}+/-{red_params["depth_unc"]}'
    plt.text(red_flux[-1,0]+0.0125, 1.07, red_str, fontsize=12, color="r")
    # plot RED data & curve
    plt.errorbar(red_flux[:, 0], red_flux[:, 1]+0.1, yerr=red_flux[:, 2], color="r", marker='.', ls='none', alpha=0.7)
    plt.plot(red_flux[:, 0], red_model+0.1, lw=3.0, color="r")
    plt.plot(np.repeat(red_params["Tmid"]-JD,10), np.linspace(0.5, 1.2, 10), alpha=0.9, linestyle="--", color="r", zorder=0, linewidth=2.0) 
    
    # calculate model for GREEN 
    green_params = parse_final_params(transit_dir, "output_green", f"FinalParams_{planet_name}_{date}.json", f"AAVSO_{planet_name}_{date}.txt")
    green_model = calc_model_fit(green_flux[:, 0]+JD, green_params)
    green_str = f'Mid-Transit Time (Tmid):\n{green_params["Tmid"]}+/-{green_params["Tmid_unc"]}BJD_TDB\nTransit Depth (Rp/R*)^2:\n{green_params["depth"]}+/-{green_params["depth_unc"]}'
    plt.text(green_flux[-1,0]+0.0125, 0.97, green_str, fontsize=12, color="g")
    # plot GREEN data & curve
    plt.errorbar(green_flux[:, 0], green_flux[:, 1], yerr=green_flux[:, 2], color="g", marker='.', ls='none', alpha=0.7)
    plt.plot(green_flux[:, 0], green_model, lw=3.0, color="g")
    plt.plot(np.repeat(green_params["Tmid"]-JD,10), np.linspace(0.5, 1.2, 10), alpha=0.9, linestyle="--", color="g", zorder=0, linewidth=2.0) 

    #  calculate model for BLUE 
    blue_params = parse_final_params(transit_dir, "output_blue", f"FinalParams_{planet_name}_{date}.json", f"AAVSO_{planet_name}_{date}.txt")
    blue_model = calc_model_fit(blue_flux[:, 0]+JD, blue_params)
    blue_str = f'Mid-Transit Time (Tmid):\n{blue_params["Tmid"]}+/-{blue_params["Tmid_unc"]}BJD_TDB\nTransit Depth (Rp/R*)^2:\n{blue_params["depth"]}+/-{blue_params["depth_unc"]}'
    plt.text((blue_flux[-1,0]+0.0125), 0.87, blue_str, fontsize=12, color="b")
    # plot BLUE data & curve
    plt.errorbar(blue_flux[:, 0], blue_flux[:, 1]-0.1, yerr=blue_flux[:, 2], color="b", marker='.', ls='none', alpha=0.7)
    plt.plot(blue_flux[:, 0], blue_model-0.1, lw=3.0, color="b") 
    plt.plot(np.repeat(blue_params["Tmid"]-JD,10), np.linspace(0.5, 1.2, 10), alpha=0.9, linestyle="--", color="b", zorder=0, linewidth=2.0)

    plt.title(f"{planet_name}  {date}")
    plt.subplots_adjust(left=0.075, right=0.6, top=0.926, bottom=0.092)
    plt.ylim(0.8, 1.15)
    plt.xlabel(f"Transit Mid-time (BJD_TDB) -{JD}")
    plt.ylabel("Relative Flux")
    plt.savefig(os.path.join(transit_dir, f"Chromatic_LC_{planet_name}_{date}.png"), dpi=300, bbox_inches='tight')
    plt.close()

def plot_RGB_vals(transit_dir, planet_name, date):
    #pull params for the color-separated runs
    red_params = parse_final_params(transit_dir, "output_red_", f"FinalParams_{planet_name}_{date}.json", f"AAVSO_{planet_name}_{date}.txt")
    green_params = parse_final_params(transit_dir, "output_green", f"FinalParams_{planet_name}_{date}.json", f"AAVSO_{planet_name}_{date}.txt")
    blue_params = parse_final_params(transit_dir, "output_blue", f"FinalParams_{planet_name}_{date}.json", f"AAVSO_{planet_name}_{date}.txt")

    #establish x axis
    x = ["R", "G", "B"]
    # create RGB vs mid-time plot
    midtimes = [red_params["Tmid"], green_params["Tmid"], blue_params["Tmid"]]
    JD = int(midtimes[0])
    mid_unc = [red_params["Tmid_unc"], green_params["Tmid_unc"], blue_params["Tmid_unc"]]
    plt.errorbar(0, midtimes[0] - JD, mid_unc[0], color="r", marker='.', ls='none')
    plt.errorbar(1, midtimes[1] - JD, mid_unc[1], color="g", marker='.', ls='none')
    plt.errorbar(2, midtimes[2] - JD, mid_unc[2], color="b", marker='.', ls='none')
    plt.xticks(range(len(x)), x)
    plt.ylabel(f"Transit Mid-time (BJD_TDB) -{JD}")
    plt.tight_layout()
    plt.savefig(os.path.join(transit_dir, f"RGB-vs-Midtime_{planet_name}_{date}_10min.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # create RGB vs transit depth plot
    plt.errorbar(0, red_params["depth"], red_params["depth_unc"], color="r", marker='.', ls='none')
    plt.errorbar(1, green_params["depth"], green_params["depth_unc"], color="g", marker='.', ls='none')
    plt.errorbar(2, blue_params["depth"], blue_params["depth_unc"], color="b", marker='.', ls='none')
    plt.xticks(range(len(x)), x)
    plt.ylabel(f"Transit Depth (%)")
    plt.tight_layout()
    plt.savefig(os.path.join(transit_dir, f"RGB-vs-Depth_{planet_name}_{date}_10min.png"), dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    transit_dir = os.path.join(home_dir, "TrES-3b_Stacked_615")
    planet_name = "TrES-3b"
    date = "15-06-2024"

    plot_data_with_curve(transit_dir, planet_name, date)
    # plot_RGB_vals(transit_dir, planet_name, date)