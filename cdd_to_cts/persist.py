# define a dictionary with key value pairs

# open file for writing, "w" is writing
import json
import pickle

from cdd_to_cts import static_data


def write(adict: dict, file_name: str):
    with open(static_data.WORKING_ROOT+file_name, 'w') as file:
        file.write(json.dumps(adict))  # use `json.loads` to do the reverse


def read(file_name: str):
    with open(static_data.WORKING_ROOT+file_name, newline='') as f:
        data = json.load(f)
        return data


def writep(adict: dict, file_name: str):
    pickle_out = open(static_data.WORKING_ROOT+file_name, "wb")
    pickle.dump(adict, pickle_out)
    pickle_out.close()


def readp(file_name: str):
    with open(static_data.WORKING_ROOT+file_name, 'rb') as file:
        data = pickle.load(file)
        file.close()
        return data
