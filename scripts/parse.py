import json

import spacy
from spacy.tokens import DocBin
import json


nlp = spacy.load("ru_core_news_sm")
def transmute(dict, key):

    new_dict = {key: []}

    try:
        for item in dict[key]:
            new_dict[key].append((item[0], item[1], item[2]))
    except:
        print('incorrect data format')

    return new_dict

def examples(path):

    with open(path, 'r') as f:
        data = json.load(f)
        training_data = []

        for item in data:
            text = item['text']
            entities = transmute(item, 'entities')
            training_data.append((text, entities))

    return training_data # [(text, {'entities': [()]})]
                         # to use as spacy Example: examples = [Example.from_dict(nlp.make_doc(text), example) for text, example in data]

def to_spacy(path, save_to):

    nlp = spacy.load('ru_core_news_sm')
    doc_bin = DocBin()
    
    with open(path, "r") as f:
        data = json.load(f)
    
    for item in data:
        doc = nlp.make_doc(item["text"])
        
        # Add entities
        if "entities" in item:
            entities = []
            for start, end, label in item["entities"]:
                span = doc.char_span(start, end, label=label)
                if span is not None:
                    entities.append(span)
            doc.ents = entities
        
        # Add categories
        if "cats" in item:
            doc.cats = item["cats"]
        
        doc_bin.add(doc)
    
    doc_bin.to_disk(save_to)
    print(f"Converted {len(data)} documents to {save_to}")

def jsonl_to_json(path):
    with open(path) as f:
        lines = f.read().split('\n')
        obj = [json.loads(line) for line in lines]
    return obj


#to_spacy('data/processed_data_ts.json', 'test_data_1.spacy')