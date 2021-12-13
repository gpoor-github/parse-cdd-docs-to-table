# define a dictionary with key value pairs

# open file for writing, "w" is writing
import json
import pickle

from parser_helpers import find_valid_path


def write(adict: dict, file_name: str):
    file_name = find_valid_path(file_name)

    with open(file_name, 'w') as file:
        file.write(json.dumps(adict))  # use `json.loads` to do the reverse
        file.close()


def read(file_name: str):
    file_name = find_valid_path(file_name)

    with open(file_name, newline='') as f:
        data = json.load(f)
        f.close()
        return data


def writep(adict: dict, file_name: str):
    file_name = find_valid_path(file_name)

    pickle_out = open(file_name, "wb")
    pickle.dump(adict, pickle_out)
    pickle_out.close()


def readp(file_name: str):
    file_name = find_valid_path(file_name)

    with open(file_name, 'rb') as file:
        data = pickle.load(file)
        file.close()
        return data
