import glob
import os
import tqdm

MOUNT_POINT = os.environ["MOUNT_POINT"]

if __name__ == "__main__":
    horse_dir_list = glob.glob(os.path.join(MOUNT_POINT, "csvs", "horse", "data", "*"))
    for horse_dir in tqdm.tqdm(horse_dir_list):
        for horse_data_path in glob.glob(os.path.join(horse_dir, "*")):
            correct_horse_data_path = horse_data_path.replace(".html", ".csv")
            os.rename(horse_data_path, correct_horse_data_path)