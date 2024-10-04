## Testing the astroplan classes to make transit calendars for BSU. 
import numpy as np
from astropy.time import Time
import pytz
import astropy.units as u
from astroplan import EclipsingSystem
from astropy.coordinates import SkyCoord
from astroplan import FixedTarget, Observer, EclipsingSystem
from astroplan import (PrimaryEclipseConstraint, is_event_observable,
                       AtNightConstraint, AltitudeConstraint, LocalTimeConstraint)
import datetime as dt

### Set global variable Boise State Observer 
boiseState = Observer(longitude=-116.208710*u.deg, latitude=43.602*u.deg,
                  elevation=821*u.m, name="BoiseState", timezone="US/Mountain")

def create_target(RA, DEC, target_name):
    '''Creates a FixedTarget object from a given RA/DEC with object name. 

    Parameters
    ----------
    RA : float
        Right Acesenion given in degrees
    DEC : float
        Declination given in degrees
    target_name : str
        Name of the target

    Returns
    -------
    FixedTarget obj
        _description_
    '''
    coords = SkyCoord(ra=RA*u.deg, dec=DEC*u.deg)
    target_obj = FixedTarget(coord=coords, name=target_name)
    # target = FixedTarget.from_name('TOI316')   
    return target_obj

def create_eclipsingsystem(primary_eclipse_time, orbital_period, eclipse_duration, target_name):
    '''Takes in planetary parameters and creates and EclipsingSystem object

    Parameters
    ----------
    primary_eclipse_time : Time
        Mid-transit time or T0 MUST be given as time object in Julian Date
    orbital_period : float
        Orbital period of system, given in days
    eclipse_duration : float
        length of eclipse. We add an hour of padding to the duration. Units of days
    target_name : str
        Name of the system

    Returns
    -------
    EclipsingSystem object
    '''
    if type(orbital_period) is float: 
        orbital_period = orbital_period*u.day
    if type(eclipse_duration) is float:
        observing_duration = (eclipse_duration+(1/12)) * u.day 
    else: 
        observing_duration = eclipse_duration + (1/12)*u.day 
    system = EclipsingSystem(primary_eclipse_time=primary_eclipse_time,
                           orbital_period=orbital_period, duration=observing_duration,
                           name=target_name)
    return system

def calculate_next_transits(start_time, dusk, dawn, number_of_transits, target, system):
    '''_summary_

    Parameters
    ----------
    start_time : _type_
        _description_
    dusk : _type_
        _description_
    dawn : _type_
        _description_
    number_of_transits : _type_
        _description_
    target : _type_
        _description_
    system : _type_
        _description_
    '''
    ## NOTE: LocalTimeConstraint DOES NOT USE LOCAL TIME. min & max times must be in UTC for it to be funcitonal..
    #  
    constraints = [AltitudeConstraint(min=30*u.deg), LocalTimeConstraint(min=dusk, max=dawn)]
    ing_egr = system.next_primary_ingress_egress_time(start_time, n_eclipses=number_of_transits)
    # Convert ingress/egress times from JD to ISO format
    ingress_times_iso = [Time(t[0], format="jd").iso for t in ing_egr]
    egress_times_iso = [Time(t[1], format="jd").iso for t in ing_egr]
    # print all transits
    for i, (ingress, egress) in enumerate(np.column_stack((ingress_times_iso, egress_times_iso))):
        print(f"Transit {i+1}: Padded Ingress: {ingress}, Padded Egress: {egress}")
    # filter transits to observable ones & print
    observable_bool = is_event_observable(constraints, boiseState, target, times_ingress_egress=ing_egr)
    filtered_transits = [time for time, is_observable in zip(np.column_stack((ingress_times_iso, egress_times_iso)), 
                                                             observable_bool[0]) if is_observable]
    for i, (ingress, egress) in enumerate(filtered_transits):
        print(f"Transit {i}: Padded Ingress (UTC): {ingress}, Padded Egress (UTC): {egress}")


def calculate_TrES3b_transits(start_time, number_of_transits):

    fixed_target = create_target(RA=268.0291, DEC=37.54633, target_name="TrES-3b")
    TrES3b = create_eclipsingsystem(primary_eclipse_time=Time(2454185.9104, format="jd"), 
                                    orbital_period=1.30618581, 
                                    eclipse_duration=0.05907, 
                                    target_name="TrES-3b")
    dusk = dt.time(19, 0)  # 7pm at Boise State
    dawn = dt.time(4, 0)  # 4am at Boise State
    calculate_next_transits(start_time, dusk, dawn, number_of_transits, fixed_target, TrES3b)

if __name__ == "__main__":
    # test new functions with TrES-3b
    obs_time = Time('2024-10-01 18:00') # Change to date that you want to start looking for transits
    n_transits = 10 # number of transits
    calculate_TrES3b_transits(obs_time, n_transits)