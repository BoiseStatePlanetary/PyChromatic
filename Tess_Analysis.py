import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def search_database(target_name="HAT-P-37"):
    search_result = lk.search_lightcurve(target_name, exptime=120)
    filter_24 = np.where(search_result.table["year"] == 2024)
    light_curves_24 = search_result[filter_24]
    print(light_curves_24)
    lc_collection = light_curves_24.download_all()
    for lc in lc_collection:
        lc.plot()
    plt.show()
        # start_time = lc.time[0]
        # df = lc.to_pandas()
        # df.to_csv(f"{target_name}_{start_time}_TESS.csv")


if __name__ == "__main__":
    search_database()