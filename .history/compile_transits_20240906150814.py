# messy for now, just enough to make this work. 

def load_phot_data(self):
        txt_name = f"AAVSO_{self.PlanetName}_{self.ObservationDate}.txt"
        data_directory = os.path.join(self.TransitDirectory, self.ExoticOutputDirectory)
        phot_data = np.loadtxt(os.path.join(data_directory, txt_name), delimiter=",")
        return {"BJD_TDB" : phot_data[:, 0], 
                "flux" : phot_data[:, 1], 
                "error" : phot_data[:, 2]}

