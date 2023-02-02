# utils.py
from configparser import ConfigParser
from pathlib import Path
import os

config = ConfigParser()
config.read_file(open(f"{Path(__file__).parents[0]}/config.ini"))


def retrieve_from_config(section, key):
    return(config.get(section, key))


def write_to_config(section, key, value):
    config.set(section, key, value)
    with open(f"{Path(__file__).parents[0]}/config.ini", 'w') as f:
        config.write(f)


def exists_fa_file(FA_FILES, RESULTS_PATH):
    list_fas = [file for file in os.listdir(FA_FILES)]
    for file in os.listdir(RESULTS_PATH):
        if file.endswith(".xml"):
            file_name = os.path.basename(file)
            if (file_name in list_fas and
                    (os.path.splitext(file)[0]+".fa") in list_fas):
                return(True)
