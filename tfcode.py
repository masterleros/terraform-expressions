import hcl2
import json
import subprocess


def expand_blocks(j_data: dict):

    # If block
    if isinstance(j_data, dict):
        if j_data.pop("__block__", None):
            j_data.update({"__start_line__": None, "__end_line__": None})

    # Walk child
    match type(j_data).__name__:
        case list.__name__:
            [expand_blocks(j) for j in j_data]
        case dict.__name__:
            [expand_blocks(j_data[j]) for j in j_data]

    return j_data


def write(path: str, j_data: dict):
    # json.dumps(expand_blocks(j_data), indent=4)
    with open(path, "w") as file:
        file.write(hcl2.writes(hcl2.reverse_transform(expand_blocks(j_data))))

    # # Format
    # process = subprocess.Popen(["terraform", "fmt"])


def read(path: str):
    with open(path, "r") as file:
        return hcl2.load(file, True)
