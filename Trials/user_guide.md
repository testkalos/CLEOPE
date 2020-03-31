# ONDA data access dedicated trial notebooks
This set of trial notebooks is aimed at facilitating the data access on Cloud, in particular:
 - the way to access ONDA EO data offer via Jupyter Notebook using the Elastic Node Server (ENS);
 - the way to download and order archived products using the OData API provided interface;
 - the way to browse geographical areas of interest via Jupyter Notebook.
 
## DISCOVER_ONDA trial notebook
This notebook is an easy introduction to the use of [ENS](https://www.onda-dias.eu/cms/knowledge-base/adapi-introduction/) and to the product download via Jupyter notebooks. Both methods allow users to access the online ONDA data offer.

### Discover ENS
Within CLEOPE a dedicated ENS access point exposes products in their native format so that they are accessible to users who can process them without any previous download. The trial notebook finds a product in the remote file system, if:
 - the single product name is given, or
 - a list of product names stored in a 📄`.txt` file is given.
 
📌 The remote position (i.e. _pseudopath_) of products is saved into a temporary file into 📁`resources`.<br>
⚠️ A warning message is raised if any of the input products show the `offline` status set to `True`, meaning that the product is not still available to ENS browsing.<br> In this case 📑 `ORDER.ipynb` ready-to-use notebook is suited for ordering archived products.

### How to download products
Alternatively to ENS, users can call the `download` function to perform a download of products via their own Jupyter Notebook. The function is written in the 📄`qm.py` script, which can be called anywhere in users own workspace as long as its path is imported:
````python
import os, sys
sys.path.append(os.path.join(os.path.expanduser("~"),"Trials/modules"))
import qm
qm.download(product,"onda_username","onda_pswd")
````
where the product field is the requested item.
Users need to specify their ONDA username and password and the product name they are interested in, including its native format (i.e. zip, netCDF).

## ORDER trial notebook
This trial notebook provides the possibility to order an archived product via Jupyter. Archived products, in fact, are not available to ENS browsing nor to the download via 🌍ONDA Catalogue. [Read more here](https://www.onda-dias.eu/cms/knowledge-base/cloudarchive-overview/).<br>
Given the product name as input, `ORDER.ipynb` notebook orders the product via [OData HTTP POST protocol](https://www.onda-dias.eu/cms/knowledge-base/cloudarchive-via-odata-api/), suited to perform this kind of action. A progress bar is displayed for checking the time left; no worry if the action may take up to 30 minutes to be completed!🕕🕡 It includes the time needed to refresh ♻️ ENS as well.  

## SEARCH trial notebook
This trial notebook allows the geographical search of ONDA EO data offer by simutating a little 🌍ONDA Catalogue via a Jupyter Notebook. Geographical search works with few simple steps:
 1. ✏️ Select an area of interest on a map drawing a rectangle, a polygon or a polyline. The selected geo-coordinates are saved in a 📄`.json` file;
 2. ✔️ (optional) select mission, product type and sensing range filters. Please note that in case many results are expected, the performace can be impacted, so it is strongly recommended to set filters on;
 3. 🌐 Visualize products footprint layers on the map;
 4. 📝 (optional) save a batch of selected products in a dedicated file named `list.txt` located by default into the `outputs` folder (but any other destinations are allowed within users own workspace).

# Mission dedicated trial notebooks
This collection of trial notebooks has been published with the purpose of leading users into data processing of EO products exploiting the ONDA data offer in a few mission dedicated tutorials. The current version supports:
 - 🌱 Land applications (S2 and S3)
 - 🏭 Atmospheric applications (S5P and Copernicus Atmosphere Monitoring Services)

## S2 trial notebook
[![N|Solid](https://sentinel.esa.int/documents/247904/250463/Sentinel-2-bw-120.jpg)](https://sentinel.esa.int/documents/247904/250463/Sentinel-2-bw-120.jpg)

Sentinel-2 trial notebook is a useful introduction to Sentinel-2 products processing. 
This notebook loads a custom list of products, which can be the one saved in `SEARCH.ipynb`, and filters the S2 products. Module `data_processing_S2` directly finds products pseudopath and unpack raster data with the purposes of:
 - Compose and visualize a true RGB stack in a few computational steps:
    - open S2 red, green and blue channels as raster data matrixes;
    - compose the 3D matrix of colors;
    - equalize the image
    - show the image. 📷
 - Compose and visualize the _Normalised_ _Burnt_ _Index_ (NBR) on a timeseries. This operation is interesting if applied on a dataframe containing the same S2 tile subject to hard changes in the vegetation richness (e.g fires 🔥) on different sensing dates, so that to detect changes in the vegetation water content. 
 - Compose and visualise a false color image (using SWIR and NIR bands) aimed at enhancing the snow coverage on the image representation. Computational steps are identical to the RGB stack.
 - Compose and visualise the _Normalised_ _Difference_ _Snow_ _Index_ (NDSI) on a timeseries. This computation is interesting if applied on the same area analysed during different seasons so that it is possible to see changes in the snow/ice ❄️ content. 

All generated plots are geo-referenced, through the extraction of coordinates from raster data.<br> 
The dataframe of S2 tiles is customisable according to users choices.

## S3 trial notebook
[![N|Solid](https://sentinel.esa.int/documents/247904/251193/Sentinel-3-ocean-120.jpg)](https://sentinel.esa.int/documents/247904/251193/Sentinel-3-ocean-120.jpg)

Sentinel-3 trial notebook is an introduction to the processing and visualization of Sentinel-3 OLCI Full Resolution Land and Water product types (LFR and WFR), allowing a colormap visualization of the extracted datasets.
The notebook loads a list of custom products, which can be the one saved via the `SEARCH.ipynb`, filters the S3 OLCI full resolution products via two dedicated functions called `land` and `water` for OLCI LFR and WFR respectively, and finally allows the visualisation of the variables of interest in a geo-referenced plot. 

The following table shows the possible variables available in the notebook.

| `land`       |   | `water`       | | 
| ------------- | ------ |-------------|-------------|
| OTCI     | _OLCI_ _Terrestrial_ _Chlorophyll_ _Index_| TSM | _Total_ _Suspended_ _Matter_ |
|OGVI      |_OLCI_ _Global_ _Vegetation_ _Index_ | CHL_OC4ME |Algal Pigment Concentration  |
| IWV | _Integrated_ _Water_ _Vapour_ |IWV | _Integrated_ _Water_ _Vapour_|



## S5P trial notebook 

[![N|Solid](https://sentinel.esa.int/documents/247904/1624461/Sentinel-5P_tm.jpg/4dbebdc6-4fb2-47ec-bcb3-065581896ad2?t=1505136035800)](https://sentinel.esa.int/documents/247904/1624461/Sentinel-5P_tm.jpg/4dbebdc6-4fb2-47ec-bcb3-065581896ad2?t=1505136035800)

Sentinel-5P trial notebook is an introduction about the composition of stacked frames of TROPOMI L2 variables in a geo-referenced plot. The notebook loads a list of custom products, which can be the one saved via the `SEARCH.ipynb`, filtering the following TROPOMI L2 variable of interest: CH4, NO2, O3, HCHO, SO2 and CO. Input data sets are then cut by taking as input the vertexes dumped in `polygon.json` reference file, which descends from the `SEARCH.ipynb` notebook (i.e. ✏️ it is the drawn rectangle). In general this operation may induce a loss of resolution in the data visualization since no mosaicing technique is performed on data sets at this level. It is useful, though, due to the hugeness of S5P footprints. <br>
Sentinel-5P tutorial is developed into two case study taken under analysis.
1. The carbon monoxide (CO) variation over the western Australia, a region which was hit by several fire episodes during December 2019 and January 2020;
2. The nitrogen dioxide (NO2) overall decline over Italy due to the lockdown during the emergency of COVID-19 virus in February/March 2020.

## CAMS trial notebook
[![N|Solid](https://atmosphere.copernicus.eu/themes/custom/ce/logo.svg)](https://atmosphere.copernicus.eu/themes/custom/ce/logo.svg)

ONDA provides access to data and tools related to the Copernicus Atmosphere Monitoring Services with an extensive catalogue of products coming from a variety of sources. These products are released in the form of maps and charts, being an ensemble of air quality models processed by diverse data centres. <br>
The CAMS oriented trial notebook is an interactive tool aimed at data visualisation of _Analysis_ _Surface Fields_ products, powered by ENS. Users can choose a period of interest and a sampling frequency within it (i.n. days, weeks or months), slicing the map in the way of need. 

# Read more
Trial notebooks make the use of packages and modules that don't come as part of the standard Python library, so CLEOPE is provided with additional modules specifically related to each one.

| | processing|visualization|
| ------------- | ------ |-------------|
| `S2`| `rasterio`,`cv2`| `matplotlib`,`holoviews`|
| `S3`| `netCDF4`| `matplotlib`|
| `S5P`|`netCDF4`|`holoviews`|
| `CAMS`| `xarray` | `hvplot`|
| `SEARCH`|`requests`|`ipyleaflet`|
| `ORDER`|`requests`| |

Moreover, CLEOPE supports the possibility to install complementary or additional libraries. Read more details [here](#packages).

# Python 3 Packages
<a id="packages"></a>
Users can call 
```python
!pip list
```
shell command directly into a notebook cell in order to list all the installed packages and version. 
New packages can be easily installed running:
```python
!pip install <package_name>
```
or specifying the version
```python
!pip install <package_name>==<version>
```
# Add modules to local path
By default, Python looks for its modules and packages in its absolute `PATH`. Within a python script, you can add path(s) occasionally to the default path by adding the following lines in the head section of your python application or script:
```python
import sys
sys.path.append('/home/jupyter-user/directory')
```
