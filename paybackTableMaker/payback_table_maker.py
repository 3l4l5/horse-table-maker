import os
import glob
from numpy import place
import pandas as pd

MOUNT_POINT = os.environ["MOUNT_POINT"]


def translate(payback_dict):
    translate_pair = {
        "単勝": "win",
        "複勝": "place",
        "三連単": "trifecta",
        "三連複": "triple",
        "ワイド": "wide",
        "馬単": "quinella",
        "馬連": "extra",
        "枠連": "braket",
    }
    translated_dict = {}
    for key in payback_dict:
        en_key = translate_pair[key]
        translated_dict[en_key] = payback_dict[key]
    return translated_dict


def convert_dict(payback_dict):
    return_dict = {}
    transrated_dict = translate(payback_dict)
    print(transrated_dict)
    for key in transrated_dict:
        if key=="win":
            win_dict = transrated_dict[key]
            win_horse_num = int(win_dict["win_horse"])
            win_prize = int(win_dict["payback"].replace(",", ""))
            return_dict["win"] = {
                "horse": win_horse_num,
                "payback": win_prize
            }
        elif key=="place":
            place_dict = transrated_dict[key]
            win_horses = [int(horse_num) for horse_num in place_dict["win_horse"].split("br")]
            win_prizes = [int(payback.replace(",", "")) for payback in place_dict["payback"].split("br")]
            return_dict["place"] = {
                "horses": win_horses,
                "paybacks": win_prizes
            }
        elif key=="trifecta":
            trifecta_dict = transrated_dict[key]
            win_horses = [int(horse) for horse in trifecta_dict["win_horse"].split(" → ")]
            win_prize = int(trifecta_dict["payback"].replace(",", ""))
            return_dict["trifecta"] = {
                "horses": win_horses,
                "win_prize": win_prize
            }
        elif key=="triple":
            triple_dict = transrated_dict[key]
            win_horses = [int(horse) for horse in triple_dict["win_horse"].split(" - ")]
            win_prize = int(triple_dict["payback"].replace(",", ""))
            return_dict["triple"] = {
                "horses": win_horses,
                "win_prize": win_prize
            }
        elif key=="wide":
            wide_dict = transrated_dict[key]
            win_horses = [[int(horse) for horse in wide_horse.split(" - ")] for wide_horse in wide_dict["win_horse"].split("br")]
            win_prizes = [int(payback.replace(",", "")) for payback in wide_dict["payback"].split("br")]
            return_dict["wide"] = {
                "horses": win_horses,
                "paybacks": win_prizes
            }
        #elif key=="quinella":








    return return_dict

def main():
    payback_table_path_list = glob.glob(os.path.join(MOUNT_POINT, "csvs", "payback", "*"))
    payback_table_path_list = payback_table_path_list[:1]

    table_dict = {}
    for payback_table_path in payback_table_path_list:
        race_id = os.path.basename(payback_table_path).split(".")[0]
        payback_dict = pd.read_csv(payback_table_path, index_col=0).T.to_dict()
        table_dict[race_id] = convert_dict(payback_dict)

    return table_dict



if __name__ == "__main__":
    main()
