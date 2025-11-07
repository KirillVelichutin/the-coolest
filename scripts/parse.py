import json

import spacy
from spacy.tokens import DocBin
from spacy.training import offsets_to_biluo_tags


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

def check_alignment(path, verbose=True):
    with open(path) as f:
        file = json.load(f)
        total_misalligned = 0
        data = []
        for obj in file:
            text = obj['text']

            entities = obj['entities']
            doc = nlp.make_doc(text)
            ent_data = []
            for start, end, label in entities:
                entity_text = text[start:end]
                tokens_in_entity = []
                for token in doc:
                    if start <= token.idx < end:
                        tokens_in_entity.append(token.text)
                ent_data.append({
                    'text': entity_text,
                    'label': label,
                    'coords': f'{start}-{end}',
                    'tokens': tokens_in_entity
                })

            
            bilou_tags = offsets_to_biluo_tags(doc, entities)
            total_misalligned += bilou_tags.count('-')
            data.append({
                'text': text,
                'ent_data': ent_data, 
                'bilou_tags': bilou_tags,
                'misaligned': f'{bilou_tags.count("-")}'
            })
        if verbose:
            faulty = 0
            for item in data:
                if item['misaligned'] != '0':
                    print(f'"{item["text"]}"')
                    print(f'entities: {item["ent_data"]}')
                    print(f'bilou tags: {item["bilou_tags"]}')
                    print(f'misaligned: {item["misaligned"]}')
                    print('---')
                    faulty += 1
            ratio = round(faulty / (len(data)/100))
            print(f'\nTOTAL MISALLIGNED: {total_misalligned}\nTOTAL FAULTY EXAMPLES: {faulty}\nFAULTY PERCENTAGE: {ratio}%')
    
    return data, total_misalligned, faulty



if __name__ == '__main__':
    check_alignment('data/processed_test.json')

#to_spacy('data/processed_data_ts.json', 'test_data_1.spacy')