## Testing the astroplan classes to make transit calendars for BSU. 
import astropy.units as u
from astropy.time import Time
from astroplan import FixedTarget, Observer, EclipsingSystem
from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
planet_properties = NasaExoplanetArchive.query_object('TrES-3 b', select='*', table='pscomppars')


# # get relevant planet properties
# epoch = Time(planet_properties['pl_tranmid'], format='jd')
# period = planet_properties['pl_orbper']
# transit_duration = planet_properties['pl_trandur']
# # Create an EclipsingSystem object for TrES-3 b
# tres3b_archive = EclipsingSystem(primary_eclipse_time=epoch, orbital_period=period,
#                                  duration=transit_duration)


# # primary_eclipse_time = Time(2457585.914587, format='jd')  # 2023 paper
# primary_eclipse_time = Time(2460473.89324, format='jd')
# orbital_period = 1.30618581 * u.day
# eclipse_duration = 0.05907 * u.day

# tres3b = EclipsingSystem(primary_eclipse_time=primary_eclipse_time,
#                            orbital_period=orbital_period, duration=eclipse_duration,
#                            name='TrES 3 b')

# # Calculate next three mid-transit times which occur after ``obs_time``
# obs_time = Time('2024-08-01 00:00')
# print("Archive")
# print(tres3b_archive.next_primary_eclipse_time(obs_time, n_eclipses=5))

# print("eclipsing system")
# print(tres3b.next_primary_eclipse_time(obs_time, n_eclipses=5))

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