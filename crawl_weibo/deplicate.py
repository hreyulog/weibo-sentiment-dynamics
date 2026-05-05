import pandas as pd
import os


def deplicate(filepath):
    df = pd.read_csv(filepath)
    df_unique = df.drop_duplicates()
    df_unique.to_csv(f'duplicates/{filepath.split("/")[-1]}', index=False)


if __name__ == "__main__":
    file_list = os.listdir('weibo')
    print(file_list)
    for file in file_list:
        if '.csv' in file:
            deplicate('weibo/' + file)
