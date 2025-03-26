import numpy as np
from astropy import time
from astropy import coordinates as coord
from astropy import units as u

def convert_times(time_data, format, scale, obj_coords, obs_coords):
        """Validates object and observatory information and populates Astropy objects for barycentric light travel time correction.

        Checks that object coordinates (right ascension and declination) and are of correct types. If correct object 
        coordinates are given, will create an Astropy SkyCoord object. Checks that observatory coordinates (longitude 
        and latitude) are given and of correct types. If given, will populate an Astropy EarthLocation object. If not
        given, will populate Astropy EarthLocation with gravitational center of Earth at North Pole. Passes the validated
        SkyCoord, EarthLocation, and Time objects to the `_calc_barycentric_time` correction function to convert times
        to BJD TDB timing format and scale.

        Parameters
        ----------
            time_data: np.ndarray[float]
                An array of timing data values. This will either be mid times or the mid time uncertainties.
            format: str
                A valid Astropy abbreviation of the data's time system.
            scale: str
                A valid Astropy abbreviation of the data's time scale.
            obj_coords: (float, float)
                Tuple of the right ascension and declination in degrees of the object being observed.
            obs_coords: (float, float)    
                Tuple of the longitude and latitude in degrees of the site of observation.
            warn: Boolean
                If True, will raise warnings to the user.

        Returns
        -------
            An array of timing data converted to Barycentric Julian Date timing format and scale (Astropy JD format, TDB scale).

        Raises
        ------
            ValueError:
                Error if None recieved for object_ra or object_dec.
            Warning:
                Warning if no observatory coordinates are given.
                Warning notifying user that barycentric light travel time correction is taking place with the given
                information.
        """
        # Get observatory and object location
        obs_location = coord.EarthLocation.from_geodetic(obs_coords[0], obs_coords[1])
        obj_location = coord.SkyCoord(ra=obj_coords[0], dec=obj_coords[1], unit="deg", frame="icrs")
        # Create time object and convert format to JD
        time_obj = time.Time(time_data, format=format, scale=scale, location=obs_location)
        time_obj_converted_format = time.Time(time_obj.to_value("jd"), format="jd", scale=scale, location=obs_location)
        # Perform barycentric correction for scale conversion, will return array of corrected times
        return time_obj_converted_format
    
if __name__ == "__main__":
    test = convert_times(time_data, format, scale, obj_coords, obs_coords)
    print test)