import spacy
import random
from spacy.util import minibatch, compounding
from spacy.training import Example
from history_tracking import TrainingHistory, plot_training_history
from reader import read_train_data, read_val_data


def training(train_data: list,eval_data: list, model_name: str, num_epochs: int):
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
        
    
    eval_examples = []
    for text, annotations in eval_data:
        example = Example.from_dict(nlp.make_doc(text), annotations)
        eval_examples.append(example)


    best_f1 = 0.0
    best_model_path = None
    
    history = TrainingHistory()
    
    optimizer = nlp.begin_training()

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):
        for epoch in range(num_epochs):
            random.shuffle(train_data)
            losses = {}

            max_batch_size = 32.0
            batch_size = compounding(4.0, max_batch_size, 1.001)
            batches = minibatch(train_data, size=batch_size)

            for batch in batches:
                    examples = []
                    for text, annotations in batch:
                            doc = nlp.make_doc(text)
                            example = Example.from_dict(doc, annotations)
                            examples.append(example)

            drop = 0.3 * (1 - epoch / num_epochs)
            nlp.update(examples, drop=drop, sgd=optimizer, losses=losses)

            scores = evaluate_model(nlp, eval_examples)

            current_f1 = scores["ents_f"]
            
            
            if current_f1 > best_f1 and current_f1 - best_f1 > 0.002:
                best_f1 = current_f1
                if best_model_path:
                    import shutil
                    shutil.rmtree(best_model_path)
                    
                best_model_path = "../models/best_model"
                nlp.to_disk(best_model_path)
                print(
                    f"Новая лучшая модель сохранена: {best_model_path}",
                    f"Iteration {epoch}, Losses: {losses}",
                    "\nМетрики:",
                    f"F1: {current_f1:.3f}",
                    f"Precision: {scores['ents_p']:.3f}",
                    f"Recall: {scores['ents_r']:.3f}",
                    "-" * 25, sep="\n"
                    )
            
                
            history.update(epoch, losses, scores)
            
    history.save()
    plot_training_history()

                
                
def evaluate_model(nlp, eval_examples):
    scorer = nlp.evaluate(eval_examples)
    return scorer


if __name__ == '__main__':
    train_data_path = "../data/train_data.json"
    val_data_path = "../data/val_data.json"
    model_path = ""
    
    training(
            train_data = read_train_data(train_data_path), 
            eval_data = read_val_data(val_data_path), 
            model_name = model_path, 
            num_epochs = 100
            )