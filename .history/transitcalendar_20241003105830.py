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

def create_target(RA, DEC, name):
    '''_summary_

    Parameters
    ----------
    RA : _float_
        _description_
    DEC : _type_
        _description_
    name : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    '''
# Change the RA and DEC and name for target
    coords = SkyCoord(ra=RA*u.deg, dec=DEC*u.deg)
    tar = FixedTarget(coord=coords, name=name)
    target = FixedTarget.from_name('TOI316')   
    return target

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