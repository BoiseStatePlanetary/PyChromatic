## Testing the astroplan classes to make transit calendars for BSU. 
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
    target_name : float
        _description_

    Returns
    -------
    _type_
        _description_
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

    constraints = [AltitudeConstraint(min=30*u.deg), LocalTimeConstraint(min=dusk, max=dawn)]
    ing_egr = target.

obs_time = Time('2024-07-22 00:00') # Change to date that you want to start looking for transits
n_transits = 150 # number of transits
min_local_time = dt.time(2, 0) # local time plus 6 for utc constraint
max_local_time = dt.time(11, 0) # local time plus 6 for utc constraint
constraints = [AltitudeConstraint(min=30*u.deg), LocalTimeConstraint(min=min_local_time, max=max_local_time)]