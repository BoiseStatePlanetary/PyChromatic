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
        # default colors 
        self.BoiseStateBlue = "#0033A0"
        self.BoiseStateOrange = "#D64309"
        # class variables
        self.TransitDirectory = transit_directory
        self.PlanetName = planet_name
        self.ObservationDate = observation_date
        self._BatmanParams = None
        self._PhotData = None
        self._RpFit = None
        self._FitFlux = None

    @property
    def PhotData(self):
        """finds the photometry results file from exotic and creates a dictionary to hold it"""
        if self._PhotData is None: 
            self._PhotData, self._Priors = self.load_phot_data()
        return self._PhotData
    
    @property
    def Priors(self):
        if self._Priors is None: 
            self._PhotData, self._Priors = self.load_phot_data()
        return self._Priors
    
    @property
    def BatmanParams(self):
        """creates a batman params object for use throughout the class.. 
        pulls values from priors in EXOTIC output"""
        if self._BatmanParams is None: 
                self._BatmanParams = self.build_param_object(self.planet_name)
        return self._BatmanParams
    
    @property
    def RpFit(self):
        """returns list [Fit Rp, uncertainty]"""
        if self._RpFit is None:
            self._RpFit, self._FitFlux = self.fit_transit_depth()
        return self._RpFit
    
    @property
    def FitFlux(self):
        """returns flux values of the light curve given the fit"""
        if self._FitFlux is None:
            self._RpFit, self._FitFlux = self.fit_transit_depth()
        return self._FitFlux

    def load_phot_data(self):
        dat = np.loadtxt(...)
        priors = dict()
        return dat, priors

    def build_param_object(self):
        params = batman.TransitParams()
        params.t0 = self.Priors["t0"]             #time of inferior conjunction
        params.per = self.Priors["per"]           #orbital period
        params.rp = self.Priors["rp"]             #planet radius (in units of stellar radii)
        params.a = self.Priors["a"]               #semi-major axis (in units of stellar radii)
        params.inc = self.Priors["inc"]           #orbital inclination (in degrees)
        params.ecc = self.Priors["ecc"]           #eccentricity
        params.w = self.Priors["w"]               #longitude of periastron (in degrees)
        # For now, we will completely ignore limb darkening & set it as 0 now.
        params.u = np.array([])            #limb darkening coefficient
        params.limb_dark = "uniform"       #limb darkening model
        return params

    def fit_transit_depth(self):
        def calc_batman_curve(time, rp):
            params = self.BatmanParams
            params.rp = rp
            m = batman.TransitModel(params, time)
            flux = m.light_curve(params)
            return flux
        
        LM_popt, LM_pcov = curve_fit(calc_batman_curve, self.PhotData["BJD_TDB"], self.PhotData["flux"], sigma=self.PhotData["error"], 
                                    p0=self.Priors["rp"])
        LM_unc = np.sqrt(np.diag(LM_pcov))
        fit_rp = LM_popt[0]
        fit_rp_unc = LM_unc[0]
        fit_rp_flux = calc_batman_curve(self.PhotData["BJD_TDB"], fit_rp)
        print("fit depth:", fit_rp**2) 
        print("uncertainty:", fit_rp_unc**2)
        print("expected depth:", self.Priors["rp"]**2)
        return [fit_rp, fit_rp_unc], fit_rp_flux

    def plot_transit(self):
        fig = plt.figure(figsize=(16, 9))
        ax = fig.add_subplot(111)
        # adjust x-axis 
        
        # plot the data points
        ax.errorbar(self.PhotData["BJD_TDB"], self.PhotData["flux"], yerr=self.PhotData["error"], marker='.', ls='', color=self.BoiseStateBlue, alpha=0.5)
        # plot transit light curve - EXOTIC
        prior_curve = batman.TransitModel(self.Priors, self.PhotData["BJD_TDB"])
        prior_flux = prior_curve.light_curve(self.Priors)
        ax.plot(self.PhotData["BJD_TDB"], prior_flux, linewidth = 1.0, color="k", label="EXOTIC fit")
        # plot our fitted transit light curve

        ax.plot()
        # set plot formatting
        ax.grid(True)
        ax.tick_params(labelsize=24)
        ax.set_xlabel(f"Time - BJD_TDB", fontsize=36)
        ax.set_ylabel("Flux (Arb. Units)", fontsize=36)
        ax.legend(fontsize=16, loc="lower right")
        # use the fit rp to calc the transit depth & add to plot with midtime
        depth = self.RpFit[0]**2
        depth_unc = self.RpFit[1]**2
        textstr = '\n'.join((f"Mid-transit time = {self.Rpfit[1]:.4f}" + r" $\pm$ " + f"{LM_unc[1]:.4f}",
                             f"Depth =  {depth:.4f}" + r" $\pm$ " + f"{depth_unc:.4f}"))                
        ax.text(0.05, 0.05, textstr, transform=ax.transAxes, fontsize=16,
                verticalalignment='bottom')

# Fit parameters mostly agree with those reported in the literature except the limb-darkening parameter, 
# but that's the one we're least sensitive to (and it depends on the bandpass, which we haven't accounted for).
fig.savefig(f"figures/{obs_date}_{planet}_litVSLM_lightcurve.png", dpi=300, bbox_inches="tight")
print(f"Figure saved to figures/{obs_date}_{planet}_litVSLM_lightcurve.png")