# -*- coding: utf-8 -*-
"""
CLEOPE - ONDA
Developed by Serco Italy - All rights reserved

@author: GCIPOLLETTA
Contact me: Gaia.Cipolletta@serco.com

Main package aimed at CGLS processing.
"""
from ipywidgets import widgets, interact, Layout, interactive, VBox, HBox
from IPython.display import display
import pandas as pd
import numpy as np
import json, os, glob, xarray, warnings
from datetime import datetime, timedelta

# Create output directory
dirName = 'out'
try:
    os.mkdir(dirName)
except FileExistsError:
    flag = 1

def sensing():
    """Create a widget to select sensing range

    Return: date pickers for sensing start and stop (ipywidgets objects)
    """
    start = widgets.DatePicker(
        description='Pick a date:',
        disabled=False)
    return start

def _b_(color="peachpuff"):
    """Define widgets button color

    Parameters:
        color (str): widget python color property; default: peachpuff

    Return: styled button color (ipywidgets)
    """
    b = widgets.Button(description="OK",layout=Layout(width='auto'))
    b.style.button_color = color
    return b

def _select_():
    """Main selector for CGLS datasets to be processed. Widgets objects (ipywidgets) are displayed on screen while selection inputs dumped into files.

    Return: None
    """
    stdate = sensing()
    btn_1 = _b_()
    box_1 = (HBox([stdate,btn_1],layout=Layout(width='65%', height='80px')))
    btn_2 = _b_()
    variable = _variable_()
    box_2 = HBox([variable,btn_2],layout=Layout(width='90%'))
    BOX = VBox([box_1,box_2],layout=Layout(width='auto', height='auto'))
    display(BOX)
    def sens_input(b):
        v = stdate.value
        dates = check_if_date_none(v)
        print("Sensing: %s"%dates)
        save_s(dates)
    btn_1.on_click(sens_input)
    def var_input(b):
        var = convert_var(variable.value)
        print("Variable to monitor: %s" %var)
        save_var(var)
    btn_2.on_click(var_input)

def check_if_date_none(date):
    """Check if date selection is valid, otherwise fix with today.

    Return: date (datetime)
    """
    if date == None:
        print("None is not a date!")
        return datetime.strftime(datetime.now(),"%Y-%m-%d")
    else:
        return date

def check_sensing(date):
    """Check if sensing range selection is valid, otherwise fix with today.

    Return: date (datetime)
    """
    if datetime.strptime(date,"%Y-%m-%d")>datetime.now() or datetime.strptime(date,"%Y-%m-%d")<datetime(2017,6,1):
        print("Wrong datetime range, fixing with the current month")
        return datetime.strftime(datetime.now(),"%Y-%m-%d")
    else:
        return date

def save_s(data):
    """Save sensing range selection into file, named `out/dates.log` by default.

    Parameters:
        data (pandas DataFrame): sensing range information (from function: sensing)

    Return: None
    """
    dest = os.path.join(os.getcwd(),"out")
    file = os.path.join(dest,"dates.log")
    df = pd.DataFrame(np.nan,index=range(1),columns=["date"])
    df["date"] = data
    df.to_csv(file)

def save_var(data):
    """Save CGLS variable selection into file, named `out/variable.log` by default.

    Parameters:
        data (pandas DataFrame): CGLS variable name information (from function: _variable_)

    Return: None
    """
    dest = os.path.join(os.getcwd(),"out")
    file = os.path.join(dest,"variable.log")
    with open(file, 'w') as outfile:
        json.dump(data, outfile)

def convert_var(argument):
    """Define CGLS variable dictionary on options displayed via the widgets.

    Parameters:
        argument (str): input string selected

    Return: CGLS product name property (str)
    """
    switcher = {
        "Normalized_Difference_Vegetation_Index":"NDVI",
        "Frac_Absorbed_Photosynthetically_Active_Radiation_1km":"FAPAR",
        "Fraction_green_Vegetation_Cover_1km":"FCOVER",
        "Leaf_Area_Index_1km":"LAI",
    }
    return switcher.get(argument, "Invalid input")

def _variable_():
    """Create a widget with CGLS variables options.

    Return: widget (ipywidgets)
    """
    options = ["Normalized_Difference_Vegetation_Index","Frac_Absorbed_Photosynthetically_Active_Radiation_1km","Fraction_green_Vegetation_Cover_1km","Leaf_Area_Index_1km"]
    m = widgets.Dropdown(options=options,layout=Layout(width='50%'),description="Variable")
    return m

def read_var():
    """Read the CGLS variable name input from the file named out/variable.log by default; from function: save_var

    Return: variable name input selection (str)
    """
    dest = os.path.join(os.getcwd(),"out")
    file = os.path.join(dest,"variable.log")
    with open(file, 'r') as fp:
        var = json.load(fp)
    return var

def read_sen():
    """Read the sensing range input from the file named out/dates.log by default; from function: save_s

    Return: sensing range input selection (list)
    """
    dest = os.path.join(os.getcwd(),"out")
    file = os.path.join(dest,"dates.log")
    df = pd.read_csv(file)
    return df.date.values[0] # string

# monthly sampling for clands due to their non uniform sensing frenquence
# function goes one month back
def one_month_back(t):
    """Adjust monthly sampling for CGLS due to their non uniform sensing frequences by going one month back if necessary.

    Parameters:
        t (datetime): sensing date

    Return: previous month (datetime) if conditions are met
    """
    # t is a datetime object
    one_day = timedelta(days=1)
    one_month_back = t - one_day
    while one_month_back.month == t.month:
        one_month_back -= one_day
    target_month = one_month_back.month
    while one_month_back.day > t.day:
        one_month_back -= one_day
        if one_month_back.month != target_month:  # gone too far
            one_month_back += one_day
            break
    return one_month_back

def compose_pseudopath():
    """Call the function: dates_list to compose ENS pseudopaths given the input sensing date and the CGLS product name.

    Return: ENS pseudopaths (list)
    """
    root = "/mnt/Copernicus/Copernicus-land/"
    var = read_var()
    sens = check_sensing(read_sen())
    temp = datetime.strptime(sens,"%Y-%m-%d")
    now = datetime.strftime(temp,"/%Y/%m/")
    pseudopath = str(root)+str(var)+str(now)
    item = check_item()
    products = [p for p in glob.glob(pseudopath+"/**/"+item,recursive=True)]
    # check if products exists loop: goes one month back if no products are found during the current month
    if not products:
        old_date = temp
        while len(products) == 0:
#             print("No item matching datetime: %s >>> Going one month back"%datetime.strftime(old_date,"%Y-%b "))
            new_date = one_month_back(old_date) # one month back
            date = datetime.strftime(new_date,"/%Y/%m/")
            pseudopath = str(root)+str(var)+str(date)
            products = [p for p in glob.glob(pseudopath+"/**/"+item,recursive=True)]
            if products:
#                 print("Products found during: %s"%datetime.strftime(new_date,"%Y-%b "))
                sort_products = sorted(products)
                return sort_products[-1] # return the last datetime available for that variable
            else:
                old_date = new_date
                continue
    else:
        sort_products = sorted(products)
        return sort_products[-1] # return the last datetime available for that variable

def check_item():
    """Check for input validity on variable Name and convert to ENS compliant variable

    Return: CGLS variable name shown into ENS pseudopath (str)
    """
    var = read_var()
    if var == "NDVI":
        return "c_gls_NDVI_*.nc"
    elif var == "FAPAR":
        return "c_gls_FAPAR_*.nc"
    elif var == "FCOVER":
        return "c_gls_FCOVER_*.nc"
    elif var == "LAI":
        return "c_gls_LAI_*.nc"
    else:
        warnings.warn("No match found Error")
        return None

def dataset():
    """Main function to open and read CGLS datasets given all the user selections via ENS, calling function compose_pseudopath. Final dataset is selected on time dimension.

    Return: CGLS dataset (xarray) with flattened time dimension, CGLS sensing date property (numpy datetime)
    """
    variable = read_var()
    item = compose_pseudopath()
    ds = xarray.open_dataset(item)[str(variable)]
    return ds.isel(time=0),np.datetime_as_string(ds.time.data[0], timezone='UTC',unit='m')
