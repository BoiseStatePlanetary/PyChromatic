# messy for now, just enough to make this work. 
import os
import numpy as np
import json
import matplotlib.pyplot as plt


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

def plot_data_with_curve(transit_dir, planet_name, date):
    plt.figure(figsize=(9, 6))
    phot = load_phot_data(transit_dir, planet_name, date)
    # calculate JD
    JD = int(red_flux[0,0])
    red_flux[:, 0] -= JD
    green_flux[:, 0] -= JD
    blue_flux[:, 0] -= JD
    # calculate model for RED 
    red_params = parse_final_params(transit_dir, "output_red_10min", f"FinalParams_{planet_name}_{date}.json", f"AAVSO_{planet_name}_{date}.txt")
    red_model = calc_model_fit(red_flux[:, 0]+JD, red_params)
    red_str = f'Mid-Transit Time (Tmid):\n{red_params["Tmid"]}+/-{red_params["Tmid_unc"]}BJD_TDB\nTransit Depth (Rp/R*)^2:\n{red_params["depth"]}+/-{red_params["depth_unc"]}'
    plt.text(red_flux[-1,0]+0.0125, 1.07, red_str, fontsize=12, color="r")
    # plot RED data & curve
    plt.errorbar(red_flux[:, 0], red_flux[:, 1]+0.1, yerr=red_flux[:, 2], color="r", marker='.', ls='none', alpha=0.7)
    plt.plot(red_flux[:, 0], red_model+0.1, lw=3.0, color="r")
    plt.plot(np.repeat(red_params["Tmid"]-JD,10), np.linspace(0.5, 1.2, 10), alpha=0.9, linestyle="--", color="r", zorder=0, linewidth=2.0) 
    
    # calculate model for GREEN 
    green_params = parse_final_params(transit_dir, "output_green_10min", f"FinalParams_{planet_name}_{date}.json", f"AAVSO_{planet_name}_{date}.txt")
    green_model = calc_model_fit(green_flux[:, 0]+JD, green_params)
    green_str = f'Mid-Transit Time (Tmid):\n{green_params["Tmid"]}+/-{green_params["Tmid_unc"]}BJD_TDB\nTransit Depth (Rp/R*)^2:\n{green_params["depth"]}+/-{green_params["depth_unc"]}'
    plt.text(green_flux[-1,0]+0.0125, 0.97, green_str, fontsize=12, color="g")
    # plot GREEN data & curve
    plt.errorbar(green_flux[:, 0], green_flux[:, 1], yerr=green_flux[:, 2], color="g", marker='.', ls='none', alpha=0.7)
    plt.plot(green_flux[:, 0], green_model, lw=3.0, color="g")
    plt.plot(np.repeat(green_params["Tmid"]-JD,10), np.linspace(0.5, 1.2, 10), alpha=0.9, linestyle="--", color="g", zorder=0, linewidth=2.0) 

    #  calculate model for BLUE 
    blue_params = parse_final_params(transit_dir, "output_blue_10min", f"FinalParams_{planet_name}_{date}.json", f"AAVSO_{planet_name}_{date}.txt")
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