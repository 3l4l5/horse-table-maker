import os
import json
import pandas as pd
import pandas as pd
import numpy as np
import glob
import pickle
from tqdm import tqdm
import datetime

MOUNT_POINT = os.environ["MOUNT_POINT"]
IS_TEST = True

def convert_horse_table(race_df, race_df_index, horse_id):
        horse_data_dict = {}
        race_df_oneline = race_df.iloc[race_df_index]
        horse_id = str(race_df_oneline["horse_id"])
        race_date = datetime.datetime.strptime(race_df_oneline["date"], "%Y/%m/%d")
        horse_df = get_horse_df(horse_id)
        peds_info = get_peds_dict(horse_id)
        if not (horse_df is None or peds_info is None):
            # NOTE: convert to date_str to datetime type.
            horse_df["date"] = pd.to_datetime(horse_df["date"])
            horse_df_before_race = horse_df[horse_df["date"]<race_date]
            appearances_num = len(horse_df_before_race)
            horse_data_dict["appearances_num"] = appearances_num
            if appearances_num > 0:
                # NOTE: create Feature value part.

                mean_3_prize   = np.nanmean(horse_df_before_race.iloc[:3]["prize"])
                mean_5_prize   = np.nanmean(horse_df_before_race.iloc[:5]["prize"])
                mean_all_prize = np.nanmean(horse_df_before_race["prize"])
                horse_data_dict["mean_3_prize"] = mean_3_prize
                horse_data_dict["mean_5_prize"] = mean_5_prize
                horse_data_dict["mean_all_prize"] = mean_all_prize

                # NOTE: 今までの着順について
                numeric_order_list  = pd.to_numeric(horse_df_before_race["order"], errors="coerce").values
                mean_3_order   = np.nanmean(numeric_order_list[:3])
                mean_5_order   = np.nanmean(numeric_order_list[:5])
                mean_all_order = np.nanmean(numeric_order_list)
                horse_data_dict["mean_3_order"] = mean_3_order
                horse_data_dict["mean_5_order"] = mean_5_order
                horse_data_dict["mean_all_order"] = mean_all_order

                # NOTE: 今まで走ったレースのタイプについて
                grass_rate = sum(horse_df_before_race["race_type"] == "芝") / appearances_num
                dart_rate  = sum(horse_df_before_race["race_type"] == "ダ") / appearances_num
                obst_rate  = sum(horse_df_before_race["race_type"] == "障") / appearances_num
                horse_data_dict["grass_rate"] = grass_rate
                horse_data_dict["dart_rate"] = dart_rate
                horse_data_dict["obst_rate"] = obst_rate

                # NOTE: 今まで搭乗したjockeyについて
                today_jockey_id = str(race_df_oneline["hockey_id"]).zfill(5)
                today_jockey_rate = sum(horse_df_before_race["jockey_id"] == today_jockey_id) / appearances_num
                horse_data_dict["today_jockey_rate"] = today_jockey_rate

                # NOTE: 今まで走ったレースの長さについて
                mean_race_length = horse_df_before_race["length"].mean()
                sum_race_length = horse_df_before_race["length"].sum()
                horse_data_dict["mean_race_length"] = mean_race_length
                horse_data_dict["sum_race_length"] = sum_race_length


                # NOTE: 勝ち馬の情報について
                # NOTE: データが存在しない可能性があるので見送り

                # NOTE: 前回のレースの情報について
                # NOTE: データが存在しない可能性があるのであるもののみ
                latest_race_id = str(horse_df_before_race.iloc[0]["race_id"])
                latest_race_df = race_df.query(f'race_id == "{latest_race_id}"')
                latest_race_racehorses_num = len(latest_race_df)
                if latest_race_racehorses_num > 0:
                    latest_race_max_prize = latest_race_df["max_prize"].values[0]
                else:
                    latest_race_max_prize = -1000
                horse_data_dict["latest_race_max_prize"] = latest_race_max_prize

            else:
                horse_data_dict["mean_3_prize"] = 0
                horse_data_dict["mean_5_prize"] = 0
                horse_data_dict["mean_all_prize"] = 0

                horse_data_dict["mean_3_order"] = 20
                horse_data_dict["mean_5_order"] = 20
                horse_data_dict["mean_all_order"] = 20

                horse_data_dict["grass_rate"] = 0
                horse_data_dict["dart_rate"] = 0
                horse_data_dict["obst_rate"] = 0

                horse_data_dict["today_jockey_rate"] = 0

                horse_data_dict["mean_race_length"] = 0
                horse_data_dict["sum_race_length"] = 0

                horse_data_dict["latest_race_max_prize"] = 0
            return horse_data_dict


def race_horse_concater(race_df):
    horse_result_dict_list = []
    peds_dict_list = []
    convert_race_df_list = []
    for race_df_index in tqdm(range(len(race_df))):
        try:
            race_df_oneline = race_df.iloc[race_df_index]
            horse_id = str(race_df_oneline["horse_id"])
            horse_table_converted = convert_horse_table(race_df, race_df_index, horse_id)
            peds_dict = get_peds_dict(horse_id)
            if type(horse_table_converted) == dict and not peds_dict is None:
                horse_result_dict_list.append(horse_table_converted)
                peds_dict_list.append(peds_dict)
                convert_race_df_list.append(pd.DataFrame(race_df_oneline).T)
        except Exception as e:
            print(e)
    race_table = pd.concat(convert_race_df_list)
    race_table.index = [n for n in range(len(race_table))]
    horse_table = pd.DataFrame.from_dict(horse_result_dict_list)
    peds_table = pd.DataFrame.from_dict(peds_dict_list)
    converted_df = pd.concat([race_table, horse_table, peds_table], axis=1, join='outer')
    return converted_df


def get_race_df(n_of_race=None):
    race_pathlist = []
    race_pathlist = sorted(glob.glob(os.path.join(MOUNT_POINT, "csvs","race", "*")))
    if n_of_race is None:
        get_race_path_list = race_pathlist
    else:
        get_race_path_list = race_pathlist[::-1][:n_of_race][::-1]
    df_list = []
    for csv_path in tqdm(get_race_path_list):
        try:
            race_id = os.path.basename(csv_path).split(".")[0]
            df = pd.read_csv(csv_path)
            df["race_id"] = [race_id] * len(df)
            df_list.append(df)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(csv_path)

    return pd.concat(df_list)

def get_horse_df(horse_id):
    horse_csv_path = sorted(glob.glob(os.path.join(MOUNT_POINT, "csvs","horse", "data", horse_id, "*.csv")))[0]
    try:
        horse_csv = pd.read_csv(horse_csv_path)
    except Exception as e:
        print(e)
        horse_csv = None
    return horse_csv

def get_peds_dict(horse_id):
    peds_dict_path = os.path.join(MOUNT_POINT, "csvs","peds", horse_id+".json")
    if os.path.exists(peds_dict_path):
        with open(peds_dict_path, "r") as f:
            peds_dict = json.load(f)
        return peds_dict
    else:
        return None





def main(is_test):
    race_df = get_race_df()
    all_df = race_horse_concater(race_df)

    if not is_test:
        file_path = os.path.join(MOUNT_POINT, "all_data.csv")
    else:
        file_path = os.path.join(MOUNT_POINT, "test", "all_data.csv")
    all_df.to_csv(file_path)


if __name__ == "__main__":
    main(is_test=False)