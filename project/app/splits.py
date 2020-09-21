from datetime import datetime

splits = []

for i in range(2009, 2021):
    for j in range(1, 13):
        splits.append(datetime(i, j, 1))

if __name__ == "__main__":
    print(splits)