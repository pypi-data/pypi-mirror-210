from pygeodesy.sphericalNvector import LatLon, perimeterOf, meanOf
import matplotlib.pyplot as plt
import numpy as np, shapefile, glob
import pandas as pd, os

gltiles = {
    "a10g": [50, 90, -180, -90, 1, 6098, 10800, 4800],
    "b10g": [50, 90, -90, 0, 1, 3940, 10800, 4800],
    "c10g": [50, 90, 0, 90, -30, 4010, 10800, 4800],
    "d10g": [50, 90, 90, 180, 1, 4588, 10800, 4800],
    "e10g": [0, 50, -180, -90, -84, 5443, 10800, 6000],
    "f10g": [0, 50, -90, 0, -40, 6085, 10800, 6000],
    "g10g": [0, 50, 0, 90, -407, 8752, 10800, 6000],
    "h10g": [0, 50, 90, 180, -63, 7491, 10800, 6000],
    "i10g": [-50, 0, -180, -90, 1, 2732, 10800, 6000],
    "j10g": [-50, 0, -90, 0, -127, 6798, 10800, 6000],
    "k10g": [-50, 0, 0, 90, 1, 5825, 10800, 6000],
    "l10g": [-50, 0, 90, 180, 1, 5179, 10800, 6000],
    "m10g": [-90, -50, -180, -90, 1, 4009, 10800, 4800],
    "n10g": [-90, -50, -90, 0, 1, 4743, 10800, 4800],
    "o10g": [-90, -50, 0, 90, 1, 4039, 10800, 4800],
    "p10g": [-90, -50, 90, 180, 1, 4363, 10800, 4800] }


files = [("lake1","/tmp/gshhg-shp-2.3.7/GSHHS_shp/i/GSHHS_i_L2.shp"),
         ("river1","/tmp/gshhg-shp-2.3.7/WDBII_shp/i/WDBII_river_i_L01.shp"),
         ("river2","/tmp/gshhg-shp-2.3.7/WDBII_shp/i/WDBII_river_i_L02.shp"),
         ("river3","/tmp/gshhg-shp-2.3.7/WDBII_shp/i/WDBII_river_i_L03.shp"),
         ("river4","/tmp/gshhg-shp-2.3.7/WDBII_shp/i/WDBII_river_i_L04.shp"),
         ("river5","/tmp/gshhg-shp-2.3.7/WDBII_shp/i/WDBII_river_i_L05.shp"),
         ("river6","/tmp/gshhg-shp-2.3.7/WDBII_shp/i/WDBII_river_i_L06.shp"),
         ("river7","/tmp/gshhg-shp-2.3.7/WDBII_shp/i/WDBII_river_i_L07.shp"),
         ("river8","/tmp/gshhg-shp-2.3.7/WDBII_shp/i/WDBII_river_i_L08.shp"),
         ("river9","/tmp/gshhg-shp-2.3.7/WDBII_shp/i/WDBII_river_i_L09.shp"),
         ("river10","/tmp/gshhg-shp-2.3.7/WDBII_shp/i/WDBII_river_i_L10.shp"),
         ("river11","/tmp/gshhg-shp-2.3.7/WDBII_shp/i/WDBII_river_i_L11.shp")
]

# Datafile is from https://www.ngdc.noaa.gov/mgg/topo/gltiles.html, download
# "all files in on zip", extract zip under /tmp
def preprocess_GLOBE():

    arrays= {}

    for x in glob.glob("/tmp/all10g/all10/*"):
        print (x, os.path.basename(x))
        lat_min, lat_max, lon_min, lon_max, elev_min, elev_max, cols, rows = gltiles['g10g']
        print (cols, rows)
        z = np.fromfile(x,dtype='<i2')
        z = np.reshape(z,(round(z.__len__()/cols), cols))

        lon = lon_min + 1/120*np.arange(cols)
        lat = lat_max - 1/120*np.arange(round(z.size/cols))
        downsample = 2
        lat_select = np.arange(0,len(lat),downsample)
        lon_select = np.arange(0,len(lon),downsample)

        zm = z[np.ix_(lat_select,lon_select)]    
        print (z.shape,zm.shape)
        arrays[os.path.basename(x)] = zm[:]

    np.savez_compressed('/tmp/gltiles.npz', \
                        a10g=arrays['a10g'], \
                        b10g=arrays['b10g'], \
                        c10g=arrays['c10g'], \
                        d10g=arrays['d10g'], \
                        e10g=arrays['e10g'], \
                        f10g=arrays['f10g'], \
                        g10g=arrays['g10g'], \
                        h10g=arrays['h10g'], \
                        i10g=arrays['i10g'], \
                        j10g=arrays['j10g'], \
                        k10g=arrays['k10g'], \
                        l10g=arrays['l10g'], \
                        m10g=arrays['m10g'], \
                        n10g=arrays['n10g'], \
                        o10g=arrays['o10g'])

def preprocess_GSHHS():
    
    res = []
    for type,file in files:
        print (file)
        sf = shapefile.Reader(file)
        r = sf.records()
        waters = sf.shapes()

        print (len(waters))
        for idx in range(len(waters)):
            water = waters[idx]
            name = r[idx]
            print (name,len(water.parts))
            bounds = list(water.parts) + [len(water.points)]
            for (previous, current) in zip(bounds, bounds[1:]):
                geo = [[x[1],x[0]] for x in water.points[previous:current]]
                if len(geo) < 1: continue
                latlons = [LatLon(a[0],a[1]) for a in geo]
                per = np.round(perimeterOf(latlons, radius=6371),2)
                mid = meanOf(latlons)
                res.append([mid.lat,mid.lon,per,type,geo])

    df = pd.DataFrame(res)
    df.columns = ['lat','lon','perimeter','type','polygon']
    df.to_csv('/tmp/lake_river.csv',index=None)


if __name__ == "__main__": 
    
    #preprocess_GSHHS()
    preprocess_GLOBE()
    
