import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np

search_result = lk.search_lightcurve('HAT-P-37')
filter_24 = np.where(search_result.table["year"] == 2024)
light_curves_24 = search_result[filter_24]
lc = light_curves_24.download()
print(lc)