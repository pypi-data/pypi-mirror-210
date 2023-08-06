# This file is part of TMart.
#
# Copyright 2022 Yulun Wu.
#
# TMart is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.


# %matplotlib qt


# Go up by 2 directory and import 

import sys
import os.path as path
two_up =  path.abspath(path.join(__file__ ,"../.."))
sys.path.append(two_up)


import tmart
import numpy as np
from Py6S.Params.atmosprofile import AtmosProfile

# Specify wavelength in nm
wl = 400

### DEM and reflectance ###
image_DEM = np.array([[0,0],[0,0]]) # in meters
image_reflectance = np.array([[0.1,0.1],[0.1,0.1]]) # unitless     
image_isWater = np.zeros(image_DEM.shape) # 1 is water, 0 is land

# Synthesize a surface object
my_surface = tmart.Surface(DEM = image_DEM,
                           reflectance = image_reflectance,
                           isWater = image_isWater,
                           cell_size = 10_000)  
                               
### Atmosphere ###
atm_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer) 
aerosol_type = 'Maritime'  
my_atm = tmart.Atmosphere(atm_profile, aot550 = 0, aerosol_type = 'Maritime'  )

### Running T-Mart ###
my_tmart = tmart.Tmart(Surface = my_surface, Atmosphere= my_atm, shadow=False)

sensor_coords=[51,50,0.1]



my_tmart.set_geometry(sensor_coords=sensor_coords, 
                      target_pt_direction=[0,0],
                      sun_dir=[0,0])

results = my_tmart.run(wl=wl, band=None, n_photon=10_000)

# Calculate reflectances using recorded photon information 
R = tmart.calc_ref(results)
for k, v in R.items():
    print(k, '     ' , v)



my_atm_profile = my_tmart.atm_profile_wl

np.sum(my_atm_profile.ot_rayleigh)
