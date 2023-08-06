def load_lines(path: str):
    with open(path, "r") as f:
        lLines = [one.strip() for one in f.readlines() if one.strip()]
    return lLines


def load_kvs(path: str, sep=":"):
    with open(path, "r") as f:
        listLines = [one.split(sep, 1) for one in f.readlines() if one.strip()]
        dictOut = {one[0]: one[1] for one in listLines}
    return dictOut
