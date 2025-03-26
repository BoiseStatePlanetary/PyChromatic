# quick routine to renormalize baseline after a meridian flip
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

def renormalize_data(PhotData, ingress_time):
      # pull out data before ingress
      ingress_idx = np.argmin(np.abs(PhotData["BJD_TDB"]-ingress_time))  
      baseline_fluxes = PhotData["flux"][:ingress_idx]
      # calculate the median flux
      median_b_flux = np.median(baseline_fluxes)
    
      # Find break in data set - meridian flip
      mer_flip_idx = np.diff(PhotData["BJD_TDB"]).argmax()

      # normalize fluxes BEFORE meridian flip by dividing by the median of pre-ingress flux
      normalized_b_flux = PhotData["flux"][:mer_flip_idx]/median_b_flux

      # calculate the median after flip (note that flip occures AFTER egress)
      after_flip_fluxes = PhotData["flux"][mer_flip_idx:]
      median_flux = np.median(after_flip_fluxes)
      normalized_flux_after = after_flip_fluxes / median_flux
      PhotData["normalized_flux"] = np.concatenate((normalized_b_flux, normalized_flux_after), axis=None)
      return PhotData

def plot_data(photdata):
      plt.figure(figsize=(9, 6))
      JD = int(photdata["BJD_TDB"][0])
      time = photdata["BJD_TDB"] - JD
      plt.plot(time, photdata["flux"], color="fuchsia", marker='o', linestyle=None, label="raw")
      plt.plot(time, photdata["normalized_flux"], color='k', marker='.', linestyle=None, alpha=0.7, label="normalized")
      plt.legend()
      plt.xlabel(f"Transit Mid-time (BJD_TDB) -{JD}")
      plt.ylabel("Relative Flux")
      plt.show()
      


if __name__ == "__main__":
    home_dir = os.path.expanduser('~')
    maintransit_dir = os.path.join(home_dir, "TrES-3b_Stacked_615")
    planet_name = "TrES-3 b"
    date = "15-06-2024"
    photdata = load_phot_data(planet_name, date, maintransit_dir, "barbie")
    ingressT = 2460477.78 # note this number is specific to 6/15 transit
    photdata2 = renormalize_data(photdata, ingressT)
    plot_data(photdata2)