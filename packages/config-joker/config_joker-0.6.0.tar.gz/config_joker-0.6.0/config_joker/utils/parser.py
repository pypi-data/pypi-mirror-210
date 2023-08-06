from typing import Union, List, Any, Dict
import regex as re


def transform_splited_by_brackets(value: str) -> Union[str, int]:
    try:
        return int(value)
    except ValueError:
        return value


def flatten(lst):
    result = []
    for item in lst:
        if item=='':
            continue
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


def path_parser(path: str) -> List[Union[str, int]]:
    dots_pattern = r"\."
    brackets_pattern = r"\[(.*?)\]"
    splited_by_brackets = [transform_splited_by_brackets(v) for v in re.split(brackets_pattern, path) if bool(v)]
    neasted_result = [re.split(dots_pattern, subpath) if isinstance(subpath, str) else subpath for subpath in splited_by_brackets]
    return flatten(neasted_result)


def dict_extractor(path: str, data: str) -> Any:
    parsed_path = path_parser(path=path)
    for key in parsed_path:
        data = data[key]
    return data


class MissingKeyNameInListOfDicts(Exception):
    def __init__(self, k: str, v: str, data: str) -> None:
        msg = f'Components missing keys "{k}" or "{v}" in data: {data}'
        super().__init__(msg)


def parse_list_of_dicts(data: List[Dict], k_name: str, v_name: str) -> Dict:
    result = {}
    if not isinstance(data, list):
        raise TypeError(f'data must be a list, value passed: {data}')
    try:
        _ = [result.update({d[k_name]: d[v_name]}) for d in data]
    except KeyError:
        raise MissingKeyNameInListOfDicts(k=k_name, v=v_name, data=data)
    return result
