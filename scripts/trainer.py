import spacy
import json
import random
from spacy.util import minibatch, compounding
from spacy.training import Example


# Чтение файла с тренировачными данными
def read_training_data(eval_data_path):
    with open(f"{eval_data_path}", "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "entities" in data:
        data = data["entities"]

    train_data = []
    for item in data:
        text = item["text"]
        entities = [(start, end, label) for start, end, label in item["entities"]]
        train_data.append((text, {"entities": entities}))
        
    return train_data


# Чтение файла с валидационными данными
def read_validation_data(train_data_path):
    with open(f"{train_data_path}", "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "entities" in data:
        data = data["entities"]

    eval_data = []
    for item in data:
        text = item["text"]
        entities = [(start, end, label) for start, end, label in item["entities"]]
        eval_data.append((text, {"entities": entities}))
        
    return eval_data


def training(train_data: list,eval_data: list, model_name: str, num_epochs: int):
    # Загрузка модели
    if model_name and model_name != "blank":
        nlp = spacy.load(model_name)
        print(f"Загружена модель: {model_name}")
    else:
        nlp = spacy.blank("ru")
        print("Создана новая модель")


    # Добавление компонента NER
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")


    # Добавление новых ярлыков, если они отсутствуют в модели
    existing_labels = set(ner.labels)
    new_labels = set()

    for _, annotations in train_data:
        for ent in annotations.get("entities", []):
            if ent[2] not in existing_labels:
                new_labels.add(ent[2])

    for label in new_labels:
        ner.add_label(label)
        
    
    # Преобразование валидационных данных в необходимый формат
    eval_examples = []
    for text, annotations in eval_data:
        example = Example.from_dict(nlp.make_doc(text), annotations)
        eval_examples.append(example)


    # Тренировка модели
    best_f1_score = 0.0
    best_model_path = None
    
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

            # Оценка модели на валидационных данных
            current_f1 = evaluate_model(nlp, eval_examples)
            
            
            # Сохранение лучшей модели
            if current_f1 > best_f1_score:
                best_f1_score = current_f1
                if best_model_path:
                    # Удаляем предыдущую лучшую модель
                    import shutil
                    shutil.rmtree(best_model_path)
                
                # Сохраняем новую лучшую модель
                best_model_path = "../models/best_model"
                nlp.to_disk(best_model_path)
                print(
                    f"Новая лучшая модель сохранена: {best_model_path}", 
                    f"Iteration {epoch}, Losses: {losses}, F1: {current_f1:.3f}", 
                      "-" * 15, sep="\n"
                    )
                
                
# Функция для оценки модели
def evaluate_model(nlp, eval_examples):
    """Оценка модели на валидационных данных"""
    scorer = nlp.evaluate(eval_examples)
    return scorer["ents_f"]


if __name__ == '__main__':
    train_data_path = "../data/proccessed_data.json"
    eval_data_path = "../data/processed_validation_data.json"
    model_path = "../models/best_model"
    
    training(
            train_data = read_training_data(train_data_path), 
            eval_data = read_validation_data(eval_data_path), 
            model_name = model_path, 
            num_epochs = 300
            )