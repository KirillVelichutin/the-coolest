import json
import pandas as pd
import os

def load_dataset(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    ext = file_path.split('.')[-1].lower()
    
    if ext == 'csv':
        return _load_from_csv(file_path)
    elif ext == 'json':
        return _load_from_json(file_path)
    elif ext in ['jsonl', 'jl']:
        return _load_from_jsonl(file_path)
    else:
        raise ValueError(f"Unsupported format: {ext}")

def _load_from_csv(file_path):
    df = pd.read_csv(file_path)
    message_col = None
    for col in ['message', 'text', 'content', 'sentence']:
        if col in df.columns:
            message_col = col
            break
    if message_col is None:
        message_col = df.columns[0]
    result = []
    for text in df[message_col].dropna():
        if isinstance(text, str) and text.strip():
            result.append({"message": text.strip()})
    return result

def _load_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, list):
        return _process_json_list(data)
    elif isinstance(data, dict):
        if 'data' in data and isinstance(data['data'], list):
            return _process_json_list(data['data'])
        elif 'items' in data and isinstance(data['items'], list):
            return _process_json_list(data['items'])
        else:
            for key, value in data.items():
                if isinstance(value, list):
                    return _process_json_list(value)
    raise ValueError("Unsupported JSON structure")

def _load_from_jsonl(file_path):
    result = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            if isinstance(item, dict) and 'message' in item:
                text = item['message']
                if isinstance(text, str) and text.strip():
                    result.append({"message": text.strip()})
            else:
                for key in ['text', 'content', 'sentence']:
                    if key in item and isinstance(item[key], str) and item[key].strip():
                        result.append({"message": item[key].strip()})
                        break
    return result

def _process_json_list(data_list):
    result = []
    for item in data_list:
        if not isinstance(item, dict):
            continue
        message_value = None
        for field in ['message', 'text', 'content', 'sentence']:
            if field in item and isinstance(item[field], str) and item[field].strip():
                message_value = item[field].strip()
                break
        if message_value is None:
            for key, value in item.items():
                if isinstance(value, str) and value.strip():
                    message_value = value.strip()
                    break
        if message_value:
            result.append({"message": message_value})
    return result

def save_dataset(data, output_path, output_format):
    output_format = output_format.lower()
    
    if output_format == 'json':
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    elif output_format == 'csv':
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    elif output_format in ['jsonl', 'jl']:
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    else:
        raise ValueError(f"Unsupported format: {output_format}")

def convert_dataset(input_file, output_format):
    data = load_dataset(input_file)
    base_name = os.path.splitext(input_file)[0]
    output_path = f"{base_name}_converted.{output_format}"
    save_dataset(data, output_path, output_format)
    return output_path