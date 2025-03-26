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

def renormalize_data(PhotData):
      # Find break in data set
      mer_flip_idx = np.diff(PhotData["BJD_TDB"]).argmax()
      # normalize baseline after flip
      after_flip_fluxes = PhotData["flux"][mer_flip_idx:]
      median_flux = np.median(after_flip_fluxes)
      normalized_flux_after = after_flip_fluxes / median_flux
      print("after: /n", normalized_flux_after)
      # normalize baseline before flip
      # pull out data befor ingress
      ingress_idx = np.argmin(np.abs(PhotData["BJD_TDB"]-2460477.78))  # note this number is specific to 6/15 transit
      print(PhotData["BJD_TDB"][ingress_idx])
      baseline_fluxes = PhotData["BJD_TDB"][:ingress_idx]
      median_b_flux = np.median(baseline_fluxes)
      normalized_flux = PhotData["flux"]/
      print("after: /n", normalized_flux)


if __name__ == "__main__":
    home_dir = os.path.expanduser('~')
    maintransit_dir = os.path.join(home_dir, "TrES-3b_Stacked_615")
    planet_name = "TrES-3 b"
    date = "15-06-2024"
    photdata = load_phot_data(planet_name, date, maintransit_dir, "barbie")
    renormalize_data(photdata)