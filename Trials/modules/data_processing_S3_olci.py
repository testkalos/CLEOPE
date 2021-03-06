# -*- coding: utf-8 -*-
"""
 * Data and Information access services (DIAS) ONDA - For Space data distribution. 
 *
 * This file is part of CLEOPE (Cloud Earth Observation Processing Environment) software sources.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 
@author: GCIPOLLETTA

Main module aimed at S3 OLCI WFR and LFR data handling and visualisation.
"""
import os, glob, xarray
import numpy as np
import warnings

switcher = {
        "TSM_NN":"tsm_nn.nc",
        "CHL_OC4ME":"chl_oc4me.nc",
        "CHL_NN":"chl_nn.nc",
        "IWV":"iwv.nc",
        "OTCI":"otci.nc",
        "OGVI":"ogvi.nc",
    }

def products(file):
    """Read an input product list returning a list of products suitable for reading.

    Parameters:
        file (str): full path of the input file listing target products

    Return: lines of file read (list)
    """
    with open(file,"r") as f:
        data = f.readlines()
        list = [d.split("\n")[0] for d in data]
    return list

def key2file(argument):
    """Convert dataset OLCI variable name into the file format.

    Parameters:
        argument (str): OLCI variable name

    Return: S3 OLCI filename (str)
    """
    return switcher.get(argument, "Invalid input, choices: %s"%list(switcher.keys()))

def check_file(files):
    """Check for file list completeness, removing non-OLCI.

    Parameters:
        files (list): input full path product list

    Return: file list cleaned (list), flag (int)
    """
    flag = []
    cleanf = files.copy()
    for f in files:
        if "_OL_2_WFR" in f:
            flag.append(0)
        elif "_OL_2_LFR" in f:
            flag.append(1)
        else:
            cleanf.remove(f)
            continue
    return cleanf,flag

def open_da(products,key):
    """Open OLCI dataset, both variable and coordinates.

    Parameters:
        products (list): input file list of products
        key (str): OLCI-compliant variable name

    Return: variable dataset (xarray Dataset), coordinates dataset (xarray Dataset)
    Raise Exception if NetCDF HDF error is encountered (possible if using ENS)
    """
    files,flag = check_file(products)
    c,v = [],[]
    ncfile = key2file(key)
    if ncfile not in list(switcher.values()):
        print("Invalid input for key value, choices: %s"%list(switcher.keys()))
        return
    for p in files:
        geos = glob.glob(p+"/**/geo_coordinates.nc",recursive=True)
        bands = glob.glob(p+"/**/"+str(ncfile),recursive=True)
        if len(geos)>0 and len(bands)>0:
            try:
                coords = xarray.open_dataset(geos[0])
                var = xarray.open_dataset(bands[0])
            except:
                raise Exception("HDF error when handling %s"%p)
            c.append(coords)
            v.append(var)
        else:
            warnings.warn("%s not found"%p)
    return c,v # list of merged datasets

def make_ds(files,key,bounds=None):
    """Main function to generate a dataset given an input file list and the OLCI variable product name. Allows data clipping if clipping bounds are provided.

    Parameters:
        files (list): input full path products (from funcion: products)
        key (str): OLCI variable native name; default options list: switcher.keys()
        bounds (tuple): input vertexes of the clipping rectangle, provided in the order (lon_min,lon_max,lat_min,lat_max); default set to None

    Return: dataset concatenated along time dimension (xarray Dataset)
    Raise Exception for non time-ordered input products
    """
    if bounds:
        xmin,xmax,ymin,ymax = bounds
    c,v = open_da(files,key)
    dataset = []
    for coords,var in zip(c,v):
        dam = xarray.merge([coords,var],join="exact") # merge
        if bounds:
            ind_y = np.logical_and(dam.latitude>ymin,dam.latitude<ymax)
            ind_x = np.logical_and(dam.longitude>xmin,dam.longitude<xmax)
            ind = np.logical_and(ind_x,ind_y)
            daclip = dam.where(ind)
        else:
            daclip = dam.copy()
        dtime64 = np.datetime64(var.attrs["start_time"]) # sensing start
        # create the clipped dataset
        darr = xarray.Dataset({str(key):(['rows', 'columns'],daclip[str(key)].data)},
                                coords={'lat': (['rows', 'columns'],daclip.latitude.data),
                                        'lon': (['rows', 'columns'],daclip.longitude.data),
                                        'time': dtime64})
        # give attrs
        darr.attrs = var.attrs
        darr[str(key)].attrs = var[str(key)].attrs
        if key in list(switcher.keys())[-2:]: # OTCI and OGVI do not have units
            darr[str(key)].attrs['units'] = str(key)
        darr.lat.attrs = coords.latitude.attrs
        darr.lon.attrs = coords.longitude.attrs
        dataset.append(darr)
        dam,darr = None,None
    c,v = None,None
    if len(dataset)>1:
        try:
            return xarray.concat(dataset,dim='time')
        except:
            raise Exception("Error when concat along time dimension: data must be time ordered")
    else:
        return dataset[0]
