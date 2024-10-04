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

def create

#### Change value to mid transit time.
primary_eclipse_time = Time(2458753.025, format='jd')  

### Change orbital period in days
orbital_period = 13.324* u.day

### Change to duration in days with a hour padded
eclipse_duration = (0.106708+(1/12))* u.day

# change name to target name
transit = EclipsingSystem(primary_eclipse_time=primary_eclipse_time,
                           orbital_period=orbital_period, duration=eclipse_duration,
                           name='TOI316')


obs_time = Time('2024-07-22 00:00') # Change to date that you want to start looking for transits
n_transits = 150 # number of transits
min_local_time = dt.time(2, 0) # local time plus 6 for utc constraint
max_local_time = dt.time(11, 0) # local time plus 6 for utc constraint
constraints = [AltitudeConstraint(min=30*u.deg), LocalTimeConstraint(min=min_local_time, max=max_local_time)]