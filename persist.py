

# define a dictionary with key value pairs

# open file for writing, "w" is writing
import json
import pickle


def write(adict: dict, file_name: str):
    with open(file_name, 'w') as file:
        file.write(json.dumps(adict))  # use `json.loads` to do the reverse


def read(file_name: str):
    with open(file_name, newline='') as f:
        data = json.load(f)
        return data

def writep(adict: dict, file_name: str):
    pickle_out = open(file_name, "wb")
    pickle.dump(adict, pickle_out)
    pickle_out.close()


def readp(file_name: str):
    with open(file_name, 'rb') as file:
        data = pickle.load(file)
        file.close()
        return data
