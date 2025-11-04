import json

def read_train_data(train_data_path):
    with open(f"{train_data_path}", "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "entities" in data:
        data = data["entities"]

    train_data = []
    for item in data:
        text = item["text"]
        entities = [(start, end, label) for start, end, label in item["entities"]]
        train_data.append((text, {"entities": entities}))
        
    return train_data
        
        
        
def read_val_data(val_data_path):
    with open(f"{val_data_path}", "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "entities" in data:
        data = data["entities"]

    eval_data = []
    for item in data:
        text = item["text"]
        entities = [(start, end, label) for start, end, label in item["entities"]]
        eval_data.append((text, {"entities": entities}))
        
    return eval_data