from fileinput import filename
import os
from weakref import finalize 
from tqdm import tqdm
import numpy as np
import pyproj
import xml.etree.ElementTree as ET
import shutil
import json
import pandas as pd

# Create hotspot dict for every track
def hotspot_dir(xml_name='source.xml'):
    hotspot_d = {}
    with open(xml_name, 'rb') as xml_file:
        root = ET.parse(xml_file).getroot()
        for scene in root.findall('scene'):
            key = scene.get('name').lower()
            hotspot_d[key] = []
            for hotspot in scene.findall('hotspot'):
                hotspot_d[key].append([hotspot.get('name'), \
                    hotspot.get('ath'), hotspot.get('linkedscene')])
    return hotspot_d

# Calc azimuth
def azimuthAngle(long1, lat1, long2, lat2):
    geodesic = pyproj.Geod(ellps='WGS84')
    fwd_azimuth,back_azimuth,distance = geodesic.inv(long1, lat1, long2, lat2)
    if fwd_azimuth < 0:
        return fwd_azimuth + 360
    else:
        return fwd_azimuth

# lat, lon dict for every track
def track_dir(df, file_name):
    track = {}
    for column, value in df.iterrows():
        if value['panoramaName'].startswith(file_name):
            if value['panoramaPointName'].lower() not in track.keys():
                track[value['panoramaPointName'].lower()] = [value['latitude'], value['longitude']]
    return track

# List of (azimuth-ath) values 
def calc_az_ath(track, hotspots):
    final_dict = {}
    for scene in track.keys():
        lat1, lon1 = track[scene][0], track[scene][1]
        if scene in hotspots and len(hotspots[scene]) >= 1:
            for spot in hotspots[scene]:
                if spot[2].lower() in track:
                    lat2, lon2 = track[spot[2]][0], track[spot[2]][1] 
                    fwd_angle = azimuthAngle(lon1, lat1, lon2, lat2) - float(spot[1]) 
                    if scene not in final_dict:
                        final_dict[scene.lower()] = []
                    if fwd_angle >= 0 and fwd_angle < 360:    
                        final_dict[scene.lower()].append(fwd_angle)
                    elif fwd_angle > 360:
                        final_dict[scene.lower()].append(fwd_angle - 360)
                    else:
                        final_dict[scene.lower()].append(fwd_angle+360)
    return final_dict

# list of circular values -> median of angle
def circular_median(angles, azimuth=True):
    rads = np.deg2rad(angles)
    av_sin = np.median(np.sin(rads))
    av_cos = np.median(np.cos(rads))
    ang_rad = np.arctan2(av_sin,av_cos)
    ang_deg = np.rad2deg(ang_rad)
    if azimuth:
        ang_deg = np.mod(ang_deg,360.)
    return ang_deg

# Parse info_json to append JSON name to photo
def info_json_parse(path, info_file = "info.json"):
    os.chdir(path)
    with open(info_file, "r") as info:
        file = json.load(info)
        js = ""
        for num in file['source'].split("\\")[-1]:
            if num.isdigit(): 
                js+=num
            else: break
        file_name = "IMG_" + path[4:-6] + js
        print(file_name)
    return file_name

# Copy files to track and append photo_data to df_dict (directions.csv in future)
def build_track(file_name, TRACK, df_dict, df, base, counter):
    os.chdir("panos")
    for photo in [photo for photo in os.listdir() if photo.endswith(".jpg")]:
        photo_name = file_name + "_" + photo
        if photo_name in df["panoramaName"].values:
            if not os.path.exists(TRACK+"/"+photo_name):
                shutil.copyfile(os.path.abspath(photo), TRACK+"/"+photo_name)    
            df_dict['id'].append(counter) 
            df_dict['name'].append(photo_name)
            if df.loc[df['panoramaName'] == photo_name]['panoramaPointName'].values[0].lower() in final_dict:
                df_dict['header'].append(circular_median(final_dict[df.loc[df['panoramaName'] == photo_name]['panoramaPointName'].values[0].lower()]))
            else:
                df_dict['header'].append(df.loc[df['panoramaName'] == photo_name]['yaw'].values[0])
            df_dict['latitude'].append(df.loc[df['panoramaName'] == photo_name]['latitude'].values[0])
            df_dict['longitude'].append(df.loc[df['panoramaName'] == photo_name]['longitude'].values[0])
            df_dict['height'].append(df.loc[df['panoramaName'] == photo_name]['height'].values[0])
            counter +=1 
    os.chdir(base)
    return counter


base = os.getcwd()
os.chdir("TRACK_2021")
TRACK = os.getcwd()
os.chdir(base)

df = pd.read_csv('panos_with_yaw.csv', sep=";")

df_dict = {"id" : [], "name" : [], "header" : [], "latitude" : [], "longitude" : [], "height" : []}
counter = 0

for path in tqdm([path for path in os.listdir() if path.startswith("i00_2021")]):

    # Basic name for photos in path
    file_name = info_json_parse(path)
    # Fusion
    hotspots = hotspot_dir()
    track = track_dir(df, file_name)
    final_dict = calc_az_ath(track, hotspots)
    print(final_dict)
    # Build track
    counter = build_track(file_name, TRACK, df_dict, df, base, counter)

os.chdir(TRACK)
df = pd.DataFrame.from_dict(df_dict)
df.to_csv("directions.csv" , sep=";", header=False, index=False)

