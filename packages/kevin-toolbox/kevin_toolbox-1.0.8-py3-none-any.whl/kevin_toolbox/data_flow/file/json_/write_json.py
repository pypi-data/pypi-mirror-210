import os
import json
import copy
from kevin_toolbox.data_flow.file.json_.converter import integrate, traverse


def write_json(content, file_path, sort_keys=False, converters=None):
    file_path = os.path.abspath(file_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if converters is not None:
        content = traverse(copy.deepcopy(content), converter=integrate(converters))

    with open(file_path, 'w') as f:
        json.dump(content, f, indent=4, ensure_ascii=False, sort_keys=sort_keys)
