import tomllib
import os

file_path = os.path.dirname(__file__)

def print_path():
    print(os.path.join(file_path,".\\pyproject.toml"))
    with open(os.path.join(file_path,".\\pyproject.toml"),"rb") as toml_file:
        version = tomllib.load(toml_file)["project"]["version"]
        print(version)
    