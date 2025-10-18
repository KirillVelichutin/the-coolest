import json

import spacy


nlp = spacy.load("ru_core_news_sm")
def transmute(dict, key):

    new_dict = {key: []}

    try:
        for item in dict[key]:
            new_dict[key].append((item[0], item[1], item[2]))
    except:
        print('incorrect data format')

    return new_dict

def Parse(path):

    with open(path, 'r') as f:
        data = json.load(f)
        training_data = []

        for item in data:
            text = item['text']
            entities = transmute(item, 'entities')
            training_data.append((text, entities))

    return training_data # [(text, {'entities': [()]})]
                         # to use as spacy Example: examples = [Example.from_dict(nlp.make_doc(text), example) for text, example in data]