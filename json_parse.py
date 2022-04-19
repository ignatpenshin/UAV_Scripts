import os
import json
import pandas as pd


df_dict = {"panoramaPointName" : [], "latitude" : [], "longitude" : [], "height" : []}

basic_dir = os.getcwd()

for path in [path for path in os.listdir() if os.path.isdir(path)]:
    basic_name = "IMG_"+path[-4:]+path[-7:-5]+path[:2]+"_"

    os.chdir(path)
    for num, js in enumerate(sorted(os.listdir())):
        file = json.load(open(js))

        path_num = js[:-5] + "_" #"0"*(6-len(str(num) + "00")) + str(num) + "00_" 
        track_name = basic_name + path_num
        try:
            for photo in file[0]['panoramas']:
                pano_num = photo['track'][0]['panoramaNum'] - 1
                pano_name = track_name + "0"*(6-len(str(pano_num))) + str(pano_num) + ".jpg"
                df_dict["panoramaPointName"].append(pano_name)
                df_dict["latitude"].append(photo['track'][0]['latitude'])
                df_dict["longitude"].append(photo['track'][0]['longitude'])
                df_dict["height"].append(photo['track'][0]['height'])
        except:
            continue
         
    os.chdir(basic_dir)

df = pd.DataFrame.from_dict(df_dict)
df.to_csv("panos.csv" , sep=";", header=True, index=False)
