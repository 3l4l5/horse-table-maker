import os
import glob
import pandas as pd
import tqdm
import json

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

    for key in transrated_dict:
        if key == "win":
            win_dict = transrated_dict[key]
            win_horse_num = int(win_dict["win_horse"].split("br")[0])
            win_prize = int(win_dict["payback"].split("br")[0].replace(",", ""))
            return_dict["win"] = {
                "horse": win_horse_num,
                "payback": win_prize
            }
        elif key == "place":
            place_dict = transrated_dict[key]
            win_horses = [int(horse_num) for horse_num in place_dict["win_horse"].split("br")]
            win_prizes = [int(payback.replace(",", "")) for payback in place_dict["payback"].split("br")]
            return_dict["place"] = {
                "horse": win_horses,
                "payback": win_prizes
            }
        elif key == "trifecta":
            trifecta_dict = transrated_dict[key]
            win_horses = [int(horse) for horse in trifecta_dict["win_horse"].split("br")[0].split(" → ")]
            win_prize = int(trifecta_dict["payback"].split("br")[0].replace(",", ""))
            return_dict["trifecta"] = {
                "horse": win_horses,
                "win_prize": win_prize
            }
        elif key == "triple":
            triple_dict = transrated_dict[key]
            win_horses = [int(horse) for horse in triple_dict["win_horse"].split("br")[0].split(" - ")]
            win_prize = int(triple_dict["payback"].split("br")[0].replace(",", ""))
            return_dict["triple"] = {
                "horse": win_horses,
                "win_prize": win_prize
            }
        elif key == "wide":
            wide_dict = transrated_dict[key]
            win_horses = [[int(horse) for horse in wide_horse.split(" - ")] for wide_horse in wide_dict["win_horse"].split("br")]
            win_prizes = [int(payback.replace(",", "")) for payback in wide_dict["payback"].split("br")]
            return_dict["wide"] = {
                "horse": win_horses,
                "payback": win_prizes
            }
        elif key == "quinella":
            quinella_dict = transrated_dict[key]
            win_horses = [int(horse) for horse in quinella_dict["win_horse"].split("br")[0].split(" → ")]
            win_prize = int(quinella_dict["payback"].split("br")[0].replace(",", ""))
            return_dict["quinella"] = {
                "horse": win_horses,
                "payback": win_prize
            }
        elif key == "extra":
            extra_dict = transrated_dict[key]
            win_horse = [int(horse) for horse in extra_dict["win_horse"].split("br")[0].split(" - ")]
            win_prize = int(extra_dict["payback"].split("br")[0].replace(",", ""))
            return_dict["extra"] = {
                "horse": win_horse,
                "payback": win_prize
            }
        elif key == "braket":
            braket_dict = transrated_dict[key]
            win_horse = [int(horse) for horse in braket_dict["win_horse"].split("br")[0].split(" - ")]
            win_prize = int(braket_dict["payback"].split("br")[0].replace(",", ""))
            return_dict["braket"] = {
                "horse": win_horse,
                "payback": win_prize
            }

    return return_dict


def main():
    payback_table_path_list = glob.glob(os.path.join(MOUNT_POINT, "csvs", "payback", "*"))
    table_dict = {}
    for payback_table_path in tqdm.tqdm(payback_table_path_list):
        race_id = os.path.basename(payback_table_path).split(".")[0]
        payback_dict = pd.read_csv(payback_table_path, index_col=0).T.to_dict()
        table_dict[race_id] = convert_dict(payback_dict)
    with open(os.path.join(MOUNT_POINT, "all_payback.json"), "w") as f:
        json.dump(table_dict, f, indent=4)


if __name__ == "__main__":
    main()
