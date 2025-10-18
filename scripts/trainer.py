import spacy
import json
import random
from spacy.util import minibatch, compounding
from spacy.training import Example


def read_data():
    with open("../data/proccessed_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "entities" in data:
        data = data["entities"]


    train_data = []
    for item in data:
        text = item["text"]
        entities = [(start, end, label) for start, end, label in item["entities"]]
        train_data.append((text, {"entities": entities}))
        
    return train_data


def training(train_data: list, model_name: str, num_epochs: int):
    if model_name and model_name != "blank":
        nlp = spacy.load(model_name)
        print(f"Загружена модель: {model_name}")
    else:
        nlp = spacy.blank("ru")
        print("Создана новая модель")

    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")



    existing_labels = set(ner.labels)
    new_labels = set()

    for _, annotations in train_data:
        for ent in annotations.get("entities", []):
            if ent[2] not in existing_labels:
                new_labels.add(ent[2])

    for label in new_labels:
        ner.add_label(label)


    optimizer = nlp.begin_training()

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):
        for epoch in range(num_epochs):
            random.shuffle(train_data)
            losses = {}

            max_batch_size = 32
            batch_size = compounding(4, max_batch_size, 1.001)
            batches = minibatch(train_data, size=batch_size)

            for batch in batches:
                    examples = []
                    for text, annotations in batch:
                            doc = nlp.make_doc(text)
                            example = Example.from_dict(doc, annotations)
                            examples.append(example)

            drop = 0.3 * (1 - epoch / num_epochs)
            nlp.update(examples, drop=drop, sgd=optimizer, losses=losses)

            print(f"Epoch {epoch}, Losses: {losses}")
            
            
    nlp.to_disk("../models/last_model")




if __name__ == '__main__':
    training(train_data = read_data(), model_name = "", num_epochs = 300)