import pickle


def load():
    with open("./data/system.plk", "rb") as fd:
        return pickle.load(fd)


def save(lib):
    with open("./data/system.plk", "wb") as fd:
        return pickle.dump(lib, fd)
