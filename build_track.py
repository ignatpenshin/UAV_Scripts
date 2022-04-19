import os 
from tqdm import tqdm
import shutil
import json
import pandas as pd

base = os.getcwd()
os.chdir("TRACK_2021")
TRACK = os.getcwd()
os.chdir(base)

df = pd.read_csv('panos.csv', sep=";")

df_dict = {"id" : [], "name" : [], "header" : [], "latitude" : [], "longitude" : [], "height" : []}

counter = 0

for path in tqdm([path for path in os.listdir() if path.startswith("i00_2021")]):
    
    os.chdir(path)
    file = json.load(open('info.json'))
    js = ""
    for num in file['source'].split("\\")[-1]:
        if num.isdigit(): 
            js+=num
        else: break
    # js = file['source'][-16:-6]
    file_name = "IMG_" + path[4:-6] + js
    
    os.chdir("panos")
    for photo in [photo for photo in os.listdir() if photo.endswith(".jpg")]:
        photo_name = file_name + "_" + photo
        if photo_name in df["panoramaPointName"].values:
            shutil.copyfile(os.path.abspath(photo), TRACK+"/"+photo_name)
            
            df_dict['id'].append(counter) 
            df_dict['name'].append(photo_name)
            df_dict['header'].append(0)
            df_dict['latitude'].append(df.loc[df['panoramaPointName'] == photo_name]['latitude'].values[0])
            df_dict['longitude'].append(df.loc[df['panoramaPointName'] == photo_name]['longitude'].values[0])
            df_dict['height'].append(df.loc[df['panoramaPointName'] == photo_name]['height'].values[0])
            
            counter +=1 
    os.chdir(base)

os.chdir(TRACK)
df = pd.DataFrame.from_dict(df_dict)
df.to_csv("directions.csv" , sep=";", header=False, index=False)

