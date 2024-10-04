import os
import json
import batman
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

class fit_transit_depth():
    def __init__(self, transit_directory=None, exotic_output_directory=None, planet_name=None, observation_date=None, telescope_name=None):
        # default colors 
        self.BoiseStateBlue = "#0033A0"
        self.BoiseStateOrange = "#D64309"
        # class variables
        self.TransitDirectory = transit_directory
        self.ExoticOutputDirectory = exotic_output_directory
        self.PlanetName = planet_name
        self.ObservationDate = observation_date
        self.TelescopeName = telescope_name
        self._BatmanParams = None
        self._PhotData = None
        self._Priors = None
        self._ExoticResults = None
        self._RpFit = None
        self._FitFlux = None

    @property
    def PhotData(self):
        """finds the photometry results file from exotic and creates a dictionary to hold it"""
        if self._PhotData is None: 
            self._PhotData = self.load_phot_data()
        return self._PhotData
    
    @property
    def Priors(self):
        if self._Priors is None: 
            self._Priors = self.parse_priors()
        return self._Priors
    
    @property
    def ExoticResults(self):
        if self._ExoticResults is None: 
            self._ExoticResults = self.parse_final_params()
        return self._ExoticResults
    
    @property
    def BatmanParams(self):
        """creates a batman params object for use throughout the class.. 
        pulls values from priors in EXOTIC output"""
        if self._BatmanParams is None: 
                self._BatmanParams = self.build_param_object()
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
        txt_name = f"AAVSO_{self.PlanetName}_{self.ObservationDate}.txt"
        data_directory = os.path.join(self.TransitDirectory, self.ExoticOutputDirectory)
        phot_data = np.loadtxt(os.path.join(data_directory, txt_name), delimiter=",")
        return {"BJD_TDB" : phot_data[:, 0], 
                "flux" : phot_data[:, 1], 
                "error" : phot_data[:, 2]}
    
    def parse_final_params(self):
        txt_name = f"AAVSO_{self.PlanetName}_{self.ObservationDate}.txt"
        data_directory = os.path.join(self.TransitDirectory, self.ExoticOutputDirectory)     
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

    def parse_priors(self):   
        txt_name = f"AAVSO_{self.PlanetName}_{self.ObservationDate}.txt"
        data_directory = os.path.join(self.TransitDirectory, self.ExoticOutputDirectory)     
        with open(os.path.join(data_directory, txt_name)) as fn:
            for line in fn: 
                if line.startswith("#PRIORS-XC"):
                    # extract the JSON-like string part
                    json_str = line.split("=", 1)[1].strip()
                    # parse the JSON string
                    priors_xc_data = json.loads(json_str)
        param_dict = dict()
        period = priors_xc_data["Period"]
        param_dict["per"] = float(period["value"])
        param_dict["per_unc"] = float(period["uncertainty"])
        inc = priors_xc_data["inc"]
        param_dict["inc"] = float(inc["value"])
        param_dict["inc_unc"] = float(inc["uncertainty"])
        ecc = priors_xc_data["ecc"]
        param_dict["ecc"] = float(ecc["value"])
        param_dict["ecc_unc"] = ecc["uncertainty"]
        param_dict["u"] =[float(priors_xc_data["u0"]["value"]), float(priors_xc_data["u1"]["value"]),
                        float(priors_xc_data["u2"]["value"]), float(priors_xc_data["u3"]["value"])]                             
        return param_dict

    def build_param_object(self):
        params = batman.TransitParams()
        params.t0 = self.Priors["Tmid"]    #time of inferior conjunction (midtime)
        params.per = self.Priors["per"]    #orbital period
        params.rp = self.Priors["Rp/R*"]   #planet radius (in units of stellar radii)
        params.a = self.Priors["a/R*"]     #semi-major axis (in units of stellar radii)
        params.inc = self.Priors["inc"]    #orbital inclination (in degrees)
        params.ecc = self.Priors["ecc"]    #eccentricity
        params.w = 90.                     #longitude of periastron (in degrees) - set to 90 for now.
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
                                    p0=self.Priors["Rp/R*"])
        LM_unc = np.sqrt(np.diag(LM_pcov))
        fit_rp = LM_popt[0]
        fit_rp_unc = LM_unc[0]
        fit_rp_flux = calc_batman_curve(self.PhotData["BJD_TDB"], fit_rp)
        print("fit depth:", (fit_rp**2)*100) 
        print("uncertainty:", (fit_rp_unc**2)*100)
        print("expected depth:", (self.Priors["Rp/R*"]**2)*100)
        print(self.Priors["Rp/R*"])
        return [fit_rp, fit_rp_unc], fit_rp_flux

    def plot_transit(self, save=False):
        fig = plt.figure(figsize=(16, 9))
        ax = fig.add_subplot(111)
        # adjust x-axis 
        time = self.PhotData["BJD_TDB"] - int(self.PhotData["BJD_TDB"][0])
        # plot the data points
        ax.errorbar(time, self.PhotData["flux"], yerr=self.PhotData["error"], marker='.', ls='', color=self.BoiseStateBlue, alpha=0.5)
        # plot transit light curve - EXOTIC
        prior_curve = batman.TransitModel(self.BatmanParams, self.PhotData["BJD_TDB"])
        prior_flux = prior_curve.light_curve(self.BatmanParams)
        ax.plot(time, prior_flux, linewidth = 1.0, color="k", label="EXOTIC fit")
        # plot our fitted transit light curve
        ax.plot(time, self.FitFlux, linewidth=1.5, color=self.BoiseStateOrange, label="Fit Rp only")
        # set plot formatting
        ax.grid(True)
        ax.tick_params(labelsize=20)
        ax.set_xlabel("Time - %s" % int(self.PhotData["BJD_TDB"][0]), fontsize=24)
        ax.set_ylabel("Flux (Arb. Units)", fontsize=24)
        ax.legend(fontsize=16, loc="lower right")
        # use the fit rp to calc the transit depth & add to plot with midtime
        depth = self.RpFit[0]**2
        depth_unc = self.RpFit[1]**2
        textstr = '\n'.join((f"Mid-transit time = {self.Priors["Tmid"]:.4f}" + r" $\pm$ " + f"{self.Priors["Tmid_unc"]:.6f}",
                             f"Depth =  {depth:.4f}" + r" $\pm$ " + f"{depth_unc:.4f}"))                
        ax.text(0.05, 0.05, textstr, transform=ax.transAxes, fontsize=16,
                verticalalignment='bottom')
        if save: 
            if self.TelescopeName is not None:
                fig.savefig(f"{self.TransitDirectory}/{self.TelescopeName}_{self.PlanetName}_{self.ObservationDate}_LC_FitRponly.png", dpi=300, bbox_inches="tight")
                print(f"Figure saved to {self.TransitDirectory}/{self.TelescopeName}_{self.PlanetName}_{self.ObservationDate}_LC_FitRponly.png")
            else:
                fig.savefig(f"{self.TransitDirectory}/{self.PlanetName}_{self.ObservationDate}_LC_FitRponly.png", dpi=300, bbox_inches="tight")
                print(f"Figure saved to {self.TransitDirectory}/{self.PlanetName}_{self.ObservationDate}_LC_FitRponly.png")
        else:
            plt.show()


if __name__ == "__main__":
    home_dir = os.path.expanduser('~')
    transit_dir = os.path.join(home_dir, "TrES-3b_Stacked_615")
    exotic_dir = "output_green"
    planet_name = "TrES-3 b"
    date = "06-15-2024"

    obj = fit_transit_depth(transit_dir, exotic_dir, planet_name, date)
    obj.plot_transit(save=True)
