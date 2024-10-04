## Testing the astroplan classes to make transit calendars for BSU. 
import astropy.units as u
from astropy.time import Time
from astroplan import FixedTarget, Observer, EclipsingSystem


from astropy.time import Time
import pytz
import astropy.units as u
from astroplan import EclipsingSystem
from astropy.coordinates import SkyCoord
from astroplan import FixedTarget, Observer, EclipsingSystem
from astroplan import (PrimaryEclipseConstraint, is_event_observable,
                       AtNightConstraint, AltitudeConstraint, LocalTimeConstraint)
import datetime as dt

# TOI3844.01
primary_eclipse_time = Time(2460021.755, format='jd')
orbital_period = 0.896 * u.day
eclipse_duration = 0.0415 * u.day

toi_sys = EclipsingSystem(primary_eclipse_time=primary_eclipse_time,
                           orbital_period=orbital_period, duration=eclipse_duration,
                           name='TOI 3844.01')

# Calculate next three mid-transit times which occur after ``obs_time``
obs_time = Time('2024-07-24 00:00')
print(toi_sys.next_primary_ingress_egress_time(obs_time, n_eclipses=10))
target = FixedTarget.from_name("TOI 3844.01")
boisestate = Observer.at_site()