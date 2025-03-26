def convert_times(time_data, format, scale, obj_coords, obs_coords, warn=False):
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
        obs_location = get_obs_location(obs_coords, warn)
        obj_location = get_obj_location(obj_coords)
        \
        # Create time object and convert format to JD
        time_obj = time.Time(time_data, format=format, scale=scale, location=obs_location)
        time_obj_converted_format = time.Time(time_obj.to_value("jd"), format="jd", scale=scale, location=obs_location)
        # Perform barycentric correction for scale conversion, will return array of corrected times
        return self._calc_barycentric_time(time_obj_converted_format, obj_location)
    
    def _get_obj_location(self, obj_coords):
        """Creates the Astropy SkyCoord object for BJD time conversions.

        Parameters
        ----------
            obj_coords: (float, float)
                Tuple of the right ascension and declination in degrees of the object being observed.
        
        Returns
        -------
            An Astropy SkyCoord object with the right ascension and declination in degrees.

        Raises
        ------
            ValueError is there is no data for right ascension and/or declination.
        """
        # check if there are objects coords, raise error if not
        if all(elem is None for elem in obj_coords):
            raise ValueError("Recieved None for object right ascension and/or declination. " 
                             "Please enter ICRS coordinate values in degrees for object_ra and object_dec for TransitTime object.")
        # Create SkyCoord object
        return coord.SkyCoord(ra=obj_coords[0], dec=obj_coords[1], unit="deg", frame="icrs")
    
    def _get_obs_location(self, obs_coords, warn):
        """Creates the EarthLocation object for the BJD time conversion.

        Parameters
        ----------
            obs_coords: (float, float)
                Tuple of the longitude and latitude in degrees of the site of observation.
            warn: Boolean
                If True, will raise warnings to the user.
        
        Returns
        -------
            An Astropy EarthLocation object with the latitude and longitude in degrees.
        """
        # Check if there are observatory coords, raise warning and use earth grav center coords if not
        if all(elem is None for elem in obs_coords):
            if warn:
                logging.warning(f"Unable to process observatory coordinates {obs_coords}. "
                                "Using gravitational center of Earth.")
            return coord.EarthLocation.from_geocentric(0., 0., 0., unit=u.m)
        else:
            return coord.EarthLocation.from_geodetic(obs_coords[0], obs_coords[1])