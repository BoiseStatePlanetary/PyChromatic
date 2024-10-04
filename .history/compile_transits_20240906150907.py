# messy for now, just enough to make this work. 
import os
import numpy as np
import json


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

