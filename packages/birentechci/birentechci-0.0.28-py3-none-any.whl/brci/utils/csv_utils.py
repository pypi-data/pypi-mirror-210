import csv
from typing import List


def load_csv(path: str):
    listData = []
    with open(path, mode="r", encoding="utf-8") as f:
        for line in csv.reader(f):
            listData.append([one.strip() for one in line])
            print(listData)
    return listData


def load_perf_csv(path: str, type: str):
    listData = []
    with open(path, mode="r", encoding="utf-8") as f:
        for line in csv.reader(f):
            case_type = str(line[len(line) - 1]).strip() 
            if case_type == type or case_type == "Type":
                sub_list = []
                for one in line:
                    if one != type and one != "Type":
                        sub_list.append(one.strip())
                listData.append(sub_list)
                # listData.append([one.strip() for one in line])
                print(listData)
    return listData


def csv_to_dict(data: List):
    if not data:
        return []
    out = []
    head = data[0]
    intLen = len(head)
    for o in data[1:]:
        row = {}
        for i in range(intLen):
            row[head[i]] = o[i]
        out.append(row)
    return out


def write_csv(path: str, data: List):
    with open(path, "w", encoding="utf-8") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(data)
    return
