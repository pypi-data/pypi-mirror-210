import json


def load_json(path):
    with open(path, mode="r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    with open(path, mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return
