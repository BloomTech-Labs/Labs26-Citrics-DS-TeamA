import os
import pandas as pd

# Measuring length of .csv data

csv_files = [file for file in os.listdir(os.path.join("data", "weather")) if file[-3:]  == "csv"]
data_len = dict()

for file in csv_files:
    df = pd.read_csv(os.path.join("data", "weather", file))
    data_len[file] = len(df.index)

for file in data_len:
    if data_len[file] == 16440:
        data_len[file] = "short"
        
    elif data_len[file] == 17044 or data_len[file] == 17056:
        data_len[file] = "long"

if __name__ == "__main__":
    print(data_len)