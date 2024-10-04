import batman
import numpy as np

# One tiny trick I've adopted:
# I find that I often make figures that end up in Google slides/powerpoint presentations,
# so I give the figures the aspect ratio used by those presenations. 
aspect_ratio = 16./9 

# Also, just for fun, I use Boise State's official colors as my first two default colors. 
# In no way required, but just fun -- https://www.boisestate.edu/brand/visual-identity/colors/
BoiseState_blue = "#0033A0"
BoiseState_orange = "#D64309"

def calc_chi_sq(data, model, sigma):
    return np.sum(((data - model)/sigma)**2)

def calc_red_chi_sq(data, model, sigma, num_params):
    return calc_chi_sq(data, model, sigma)/(len(data) - num_params)
    
def calc_BIC(data, model, sigma, num_params):
    chi_sq = calc_chi_sq(data, model, sigma)
    return chi_sq + num_params*np.log(len(data))

def calc_batman_curve(time, t0, per, rp, a, inc, u, limb_dark="uniform", ecc=0, w=90.):
    # initial guesses
    params = batman.TransitParams()
    params.t0 = t0                       #time of inferior conjunction
    params.per = per                      #orbital period
    params.rp = rp                      #planet radius (in units of stellar radii)
    params.a = a                       #semi-major axis (in units of stellar radii)
    params.inc = inc                     #orbital inclination (in degrees)
    params.ecc = ecc                      #eccentricity
    params.w = w                       #longitude of periastron (in degrees)
    params.u = u                #limb darkening coefficient - using uniform, so no LDC
    params.limb_dark = limb_dark       #limb darkening model

    m = batman.TransitModel(params, time)    #initializes model
    flux = m.light_curve(params)          #calculates light curve

    return flux
