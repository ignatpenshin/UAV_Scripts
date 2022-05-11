import os
import json
import pandas as pd


df_dict = {"panoramaName" : [], "latitude" : [], "longitude" : [], \
           "height" : [], "yaw" : [], "panoramaPointName": []}

basic_dir = os.getcwd()

for path in [path for path in os.listdir() if os.path.isdir(path)]:
    basic_name = "IMG_"+path[-4:]+path[-7:-5]+path[:2]+"_"

    os.chdir(path)
    for num, jsons in enumerate(sorted(i for i in os.listdir() if i.endswith(".json"))):
        with open(jsons, "r") as js:
            file = json.load(js)
            path_num = jsons[:-5] + "_" #"0"*(6-len(str(num) + "00")) + str(num) + "00_" 
            track_name = basic_name + path_num
            for i in range(len(file)):
                try:
                    for photo in file[i]['panoramas']:
                        pano_num = photo['track'][0]['panoramaNum'] - 1
                        pano_name = track_name + "0"*(6-len(str(pano_num))) + str(pano_num) + ".jpg"
                        df_dict["panoramaName"].append(pano_name)
                        df_dict["latitude"].append(photo['track'][0]['latitude'])
                        df_dict["longitude"].append(photo['track'][0]['longitude'])
                        df_dict["height"].append(photo['track'][0]['height'])
                        try: 
                            df_dict["yaw"].append(photo['track'][0]['yaw'])
                        except:
                            df_dict["yaw"].append('None')
                        df_dict["panoramaPointName"].append(photo['track'][0]['panoramaPointName'])
                        print(pano_name, photo['track'][0]['latitude'], photo['track'][0]['longitude'], photo['track'][0]['height'], photo['track'][0]['yaw'], '\n')
                except:
                    continue     
    os.chdir(basic_dir)

df = pd.DataFrame.from_dict(df_dict)
df.to_csv("panos_with_yaw.csv" , sep=";", header=True, index=False)
