import datetime
import json;

def my_print(message = ""):
    ct = datetime.datetime.now()
    print(f"{ct}: {message}")

def cut_string(string, cut_len = 400):
    if len(string) > cut_len:
        return string[:cut_len] + "..."
    return string

def trim_dict_values(obj):
    if isinstance(obj, dict):
        return {k: trim_dict_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [trim_dict_values(v) for v in obj]
    elif isinstance(obj, str):
        return cut_string(obj)
    else:
        return obj

def trim_obj(obj):
    trimmed_obj = trim_dict_values(obj)
    json_str = json.dumps(trimmed_obj)
    return json_str