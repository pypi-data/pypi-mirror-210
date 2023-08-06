from pygeodesy.sphericalNvector import LatLon
import pandas as pd, zipfile, sys, os, csv, io
import matplotlib.pyplot as plt
import numpy as np, json, shapefile
from simplegeomap.util import gltiles

GWIDTH = 200

def plot_water_df(df,clat,clon,zoom,ax):
    MAX = 60
    CENTER_DIST = (40000. / MAX)*(zoom+1)
    p1 = LatLon(clat,clon) 
    dist = df.apply(lambda x: p1.distanceTo(LatLon(x['lat'],x['lon']))/1000.0, axis=1)
    df2 = df[dist < CENTER_DIST]
    for idx,row in df2.iterrows():
        geo = np.array(json.loads(row['polygon']))
        if 'lake' in row['type']: 
            ax.fill(geo[:,1],geo[:,0],'blue',alpha=0.4)
        if 'river' in row['type']: 
            ax.plot(geo[:,1],geo[:,0],'blue',alpha=0.4)
    
def plot_water(clat,clon,zoom,ax=None):
    if not ax: fig, ax = plt.subplots()
    data_dir = os.path.dirname(__file__)    
    with zipfile.ZipFile(data_dir + '/lake_river.zip', 'r') as z:
        df =  pd.read_csv(z.open('lake_river.csv'))
        plot_water_df(df,clat,clon,zoom=zoom,ax=ax)

    df =  pd.read_csv(data_dir + '/lake_river_addn.csv')
    plot_water_df(df,clat,clon,zoom,ax=ax)
        
   
def plot_countries(clat,clon,zoom=7,incolor='lightyellow',outcolor='lightblue',country_color={},ax=None):
    if not ax: fig, ax = plt.subplots()
    data_dir = os.path.dirname(__file__)
    MAX = 20    
    CENTER_DIST = (40000. / MAX)*(zoom+1)
    xlims = (clon+(-180./MAX)*zoom, clon+(180./MAX)*zoom)
    ylims = (clat+(-90./MAX)*zoom, clat+(90./MAX)*zoom)
    p1 = LatLon(clat, clon)
    ax.set_facecolor(color=outcolor)
    sf = shapefile.Reader(data_dir + "/TM_WORLD_BORDERS-0.3.shp", encoding = "ISO8859-1")
    r = sf.records()
    countries = sf.shapes()
    for idx in range(len(countries)):
        country = countries[idx]
        name = r[idx]
        iso3 = r[idx][2]
        lat,lon = name[10],name[9] # middle point of country
        p2 = LatLon(lat, lon)
        d = p1.distanceTo(p2)/1000.0
        if d > CENTER_DIST: continue # skip if a country is too far        
        bounds = list(country.parts) + [len(country.points)]        
        ax.set_xlim(xlims)
        ax.set_ylim(ylims)        
        for previous, current in zip(bounds, bounds[1:]):    
            geo = [[x[0],x[1]] for x in country.points[previous:current]]
            if len(geo) < 1: continue
            geo = np.array(geo)
            if geo.shape[0] > 0:
                if iso3 in country_color: 
                    ax.fill(geo[:,0],geo[:,1],country_color[iso3],alpha=0.5)
                else:
                    ax.fill(geo[:,0],geo[:,1],incolor,alpha=0.5)
                ax.plot(geo[:,0],geo[:,1],'b')

def create_grid(clat,clon,dist):    
    p1 = LatLon(clat,clon)
    EARTH_RAD = 6371
    upright = p1.destination (dist, bearing=45, radius=EARTH_RAD)
    lowleft = p1.destination (dist, bearing=225, radius=EARTH_RAD)

    minlat = np.min([upright.lat,lowleft.lat])
    maxlat = np.max([upright.lat,lowleft.lat])
    minlon = np.min([upright.lon,lowleft.lon])
    maxlon = np.max([upright.lon,lowleft.lon])

    lats = np.linspace(minlat,maxlat,GWIDTH)
    lons = np.linspace(minlon,maxlon,GWIDTH)

    glatints = np.array(list(map(int, lats)))
    glonints = np.array(list(map(int, lons)))
    
    return lats,lons, np.unique(glatints), np.unique(glonints)

def find_tile(lat,lon):
    res = [lat >= x[0] and lon < x[1] and lon >= x[2] and lon < x[3] for x in gltiles.values()]
    return res.index(True)

def plot_elevation(clat,clon,zoom,levels=None,ax=None):
    import scipy.interpolate
    from scipy.ndimage import gaussian_filter
    if not ax: fig, ax = plt.subplots()    
    data_dir = os.path.dirname(__file__)
    npz_file = data_dir + "/gltiles.npz"
    tkeys = np.array(list(gltiles.keys()))
    CENTER_DIST = 2000 * zoom

    glat,glon,glatints,glonints = create_grid(clat,clon,CENTER_DIST)
    
    zm = np.load(npz_file)
    tile = tkeys[find_tile(clat,clon)]
    elevs = zm[tile]

    lat_min, lat_max, lon_min, lon_max, elev_min, elev_max, cols, rows = gltiles[tile]
    lon = lon_min + 1/120*np.arange(cols)
    lat = lat_max - 1/120*np.arange(rows)
    downsample = 2
    lat_select = np.arange(0,len(lat),downsample)
    lon_select = np.arange(0,len(lon),downsample)
    y = lat[lat_select]
    x = lon[lon_select]

    xi = np.array(list(map(int, x)))
    yi = np.array(list(map(int, y)))

    xg, yg = np.meshgrid(x, y)
    xig, yig = np.meshgrid(xi, yi)

    xbool = np.isin(xig, glonints) & np.isin(yig, glatints)
    interpx = xg[xbool].flatten()
    interpy = yg[xbool].flatten()
    interpz = elevs[xbool].flatten()
    
    np.random.seed(0)
    ridx = np.random.choice(range(len(interpx)), size=8*1000, replace=False)

    interpx = interpx[ridx]
    interpy = interpy[ridx]
    interpz = interpz[ridx]

    interp = scipy.interpolate.LinearNDInterpolator(list(zip(interpx, interpy)), interpz)

    newx,newy = np.meshgrid(glon,glat)
    newz = interp(newx,newy)
    newz = gaussian_filter(newz, sigma=1.0)
    if not levels:
        CS=plt.contour(newx,newy,newz,cmap=plt.cm.binary,levels=[500,1000,1500,2000,3000])
    else:
        CS=plt.contour(newx,newy,newz,cmap=plt.cm.binary,levels=levels)
    plt.clabel(CS, fontsize=10, inline=1)
    
def plot_line(regarr,ax,color='black',linestyle='solid'):
    ax.plot(regarr[:,1],regarr[:,0],color=color,linestyle=linestyle)
       
def plot_region(regarr,ax,color='lightgray',alpha=0.5):
    ax.fill(regarr[:,1],regarr[:,0],color=color,alpha=alpha)
    
def find_city(name,country):
    data_dir = os.path.dirname(__file__)
    zip_file    = zipfile.ZipFile(data_dir + '/cities.zip')
    items_file  = zip_file.open('cities.csv')
    items_file  = io.TextIOWrapper(items_file)
    rd = csv.reader(items_file)
    headers = {k: v for v, k in enumerate(next(rd))}
    res = []
    for row in rd:
        if name.lower() == row[headers['nameascii']].lower().strip() and \
           country.lower() == row[headers['country_name']].lower().strip():
            res.append(row[:])
    return res

def get_country_name_iso3():
    data_dir = os.path.dirname(__file__)
    sf = shapefile.Reader(data_dir + "/TM_WORLD_BORDERS-0.3.shp", encoding = "ISO8859-1")
    r = sf.records()
    countries = sf.shapes()
    name_iso3_dict = {}
    for idx in range(len(countries)):
        country = countries[idx]
        iso3,name = r[idx][2],r[idx][4]
        name_iso3_dict[name] = iso3
    return name_iso3_dict

def get_country_geo():
    data_dir = os.path.dirname(__file__)
    sf = shapefile.Reader(data_dir + "/TM_WORLD_BORDERS-0.3.shp", encoding = "ISO8859-1")
    r = sf.records()
    countries = sf.shapes()
    country_geo = {}
    for idx in range(len(countries)):
        iso3 = r[idx][2]
        lat,lon = r[idx][10],r[idx][9] # middle point of country
        country_geo[iso3] = (lat,lon)
    return country_geo
