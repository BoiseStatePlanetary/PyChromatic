import batman  # if you do not have this package use `!python -m pip install batman-package` in a cell above this one!
import numpy as np
import matplotlib.pyplot as plt
import statistics as stat

from scipy.optimize import curve_fit
from scipy.stats import median_abs_deviation as mad

from astropy.stats import sigma_clip
from astropy.table import Table

from utils import *

def load_phot_data():
    dat = np.loadtxt(...)
    return dat

# Now let's hold period and fit the other transit parameters
def fit_transit_depth(plaent_params, time, t0, rp, a, inc):

    per = planet_params[planet]["period"]
    u = np.array([])

    return calc_batman_curve(time, t0, per, rp, a, inc, u)

fig = plt.figure(figsize=(10*aspect_ratio, 10))
ax = fig.add_subplot(111)

ax.errorbar(time[::2], data[::2], yerr=fit_sigma[::2], marker='.', ls='', color=BoiseState_blue, alpha=0.5)
print(f"photometric error: {fit_sigma[0]}")

LM_popt, LM_pcov = curve_fit(fit_transit, time, data, sigma=fit_sigma, 
                             p0=[fit_t0, planet_params[planet]["rp"], planet_params[planet]["a"], planet_params[planet]["inc"]])
LM_unc = np.sqrt(np.diag(LM_pcov))
print("t0, rp, a, inc:")
print("fit params:", LM_popt) 
print("param uncertainty", LM_unc)
print("first (t0) fit", fit_t0, planet_params[planet]["rp"], planet_params[planet]["a"], planet_params[planet]["inc"])

LM_t0 = np.min(allLCdata["JD_UTC"]) + LM_popt[0]

# HATP23b_fit_t0 = popt[0]
# HATP23b_fit_t0_unc = unc[0]

# HATP23b_fit_rp = popt[1]
# HATP23b_fit_rp_unc = unc[1]

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
