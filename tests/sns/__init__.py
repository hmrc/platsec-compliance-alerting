from json import load
from os import path
from typing import Any


def load_json_resource(filename: str) -> Any:
    with open(path.join("tests", "resources", filename), "r") as json_file:
        resource = load(json_file)
    return resource
