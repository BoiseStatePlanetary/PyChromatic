import os
import glob
import batman
import numpy as np
import matplotlib.pyplot as plt
import statistics as stat
from scipy.optimize import curve_fit
from scipy.stats import median_abs_deviation as mad
from astropy.stats import sigma_clip
from astropy.table import Table

class fit_transit_depth():
    def __init__(self, transit_directory=None, planet_name=None, observation_date=None):
        self.TransitDirectory = transit_directory
        self.PlanetName = planet_name
        self.ObservationDate = observation_date
        self._BatmanParams = None
        self._PhotData = None

    @property
    def BatmanParams(self):
        """creates a batman params object for use throughout the class.. pulls values from ?"""
        if self._BatmanParams is None: 
                self._BatmanParams = self.build_param_object(self.planet_name)
        return self._BatmanParams
    
    @property
    def PhotData(self):
        """finds the photometry results file from exotic and creates a dictionary to hold it"""
        if self._PhotData is None: 
            self._PhotData = self.load_phot_data()
        return self._PhotData

    def load_phot_data(self):
        dat = np.loadtxt(...)
        return dat

    def build_param_object(self):
        params = batman.TransitParams()
        params.t0 = t0             #time of inferior conjunction
        params.per = per           #orbital period
        params.rp = rp             #planet radius (in units of stellar radii)
        params.a = a               #semi-major axis (in units of stellar radii)
        params.inc = inc           #orbital inclination (in degrees)
        params.ecc = ecc           #eccentricity
        params.w = w               #longitude of periastron (in degrees)
        # For now, we will completely ignore limb darkening & set it as 0 now.
        params.u = np.array([])            #limb darkening coefficient
        params.limb_dark = "uniform"       #limb darkening model
        return params

    def calc_batman_curve(self):
        
        return m = batman.TransitModel(params, time)    #initializes model
    flux = m.light_curve(params) 

def fit_transit_depth(phot_data, planet_params):
    LM_popt, LM_pcov = curve_fit(calc_curve, phot_data["BJD_TDB"], phot_data["flux"], sigma=phot_data["error"], 
                             p0=planet_params["rp"])
    LM_unc = np.sqrt(np.diag(LM_pcov))
    print("fit depth:", LM_popt) 
    print("uncertainty:", LM_unc)
    print("expected depth:", planet_params["rp"])
    return LM_popt, LM_unc

def plot_transit(phot_data, planet_params, rp):
    fig = plt.figure(figsize=(10*aspect_ratio, 10))
    ax = fig.add_subplot(111)
    # plot the data points
    ax.errorbar(phot_data["BJD_TDB"], phot_data["flux"], yerr=phot_data["error"], marker='.', ls='', color=BoiseState_blue, alpha=0.5)
    # calculate transit light curve and plot
    fit_depth = fit_transit_depth(planet_params, phot_data["BJD_TDB"], rp)
    ax.plot()
    


# this plot shows the difference between the above plot (green) and fitting the rest of the parameters (orange)
ax.plot(time, fit_transit(time, fit_t0, planet_params[planet]["rp"], planet_params[planet]["a"], planet_params[planet]["inc"]), 
        lw=5, color=BoiseState_orange, zorder=-1, label=f"{planet_params[planet]['literature']}")
ax.plot(time, fit_transit(time, *LM_popt), lw=3, color="k", label="Levenberg-Marquardt Best Fit")
ax.axvline(LM_popt[0], lw=3, ls='--', color="k", label=f"Tmid = {LM_t0:.5f} +{LM_unc[0]:.5f}/-{LM_unc[0]:.5f}")


ax.grid(True)
ax.tick_params(labelsize=24)
min_time = np.min(allLCdata["JD_UTC"])
ax.set_xlabel(f"Time - {min_time:.3f}", fontsize=36)
ax.set_ylabel("Flux (Arb. Units)", fontsize=36)
ax.legend(fontsize=16, loc="lower right")

# add rest of fit parameters to plot
textstr = '\n'.join((f"Rp = {LM_popt[1]:.4f}" + r" $\pm$ " + f"{LM_unc[1]:.4f}",
                     f"a = {LM_popt[2]:.3f}" + r" $\pm$ " + f"{LM_unc[2]:.3f}",
                     f"inc = {LM_popt[3]:.3f}" + r" $\pm$ " + f"{LM_unc[3]:.3f}"))                
ax.text(0.05, 0.05, textstr, transform=ax.transAxes, fontsize=16,
        verticalalignment='bottom')

# Fit parameters mostly agree with those reported in the literature except the limb-darkening parameter, 
# but that's the one we're least sensitive to (and it depends on the bandpass, which we haven't accounted for).
fig.savefig(f"figures/{obs_date}_{planet}_litVSLM_lightcurve.png", dpi=300, bbox_inches="tight")
print(f"Figure saved to figures/{obs_date}_{planet}_litVSLM_lightcurve.png")