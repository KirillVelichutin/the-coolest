import spacy
from spacy.scorer import Scorer
from spacy.training import Example
from reader import read_data

from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt


def evaluate_ner_model(model_path, test_data):
    nlp = spacy.load(model_path)
    
    scorer = Scorer()
    
    examples = []
    for text, annotations in test_data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        example.predicted = nlp(example.reference.text)
        examples.append(example)
    
    scores = scorer.score(examples)
    
    print( 
            "Метрики модели:", 
            "Точность (Precision): {scores['ents_p']:.3f}",
            "Полнота (Recall): {scores['ents_r']:.3f}",
            "F-мера (F1-score): {scores['ents_f']:.3f}",
            sep = '\n'            
        )
    
    print("\nМетрики по сущностям")
    for entity_type, metrics in scores['ents_per_type'].items():
        print(f"{entity_type}: P={metrics['p']:.3f}, R={metrics['r']:.3f}, F1={metrics['f']:.3f}")
    
    return scores



def create_ner_confusion_matrix(model_path, test_data):
    nlp = spacy.load(model_path)
    
    
    true_labels = []
    pred_labels = []
    
    for text, annotations in test_data:
        doc = nlp(text)
        
        true_entities = {(start, end): label for start, end, label in annotations["entities"]}
        
        token_true_labels = []
        token_pred_labels = []
        
        for token in doc:
            true_label = "O"
            for (start, end), label in true_entities.items():
                if start <= token.idx < end:
                    true_label = label
                    break
            
            token_true_labels.append(true_label)
            
            pred_label = "O"
            for ent in doc.ents:
                if ent.start_char <= token.idx < ent.end_char:
                    pred_label = ent.label_
                    break
            
            token_pred_labels.append(pred_label)
        
        true_labels.extend(token_true_labels)
        pred_labels.extend(token_pred_labels)
    
    labels = sorted(set(true_labels) | set(pred_labels))
    cm = confusion_matrix(true_labels, pred_labels, labels=labels)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=labels, yticklabels=labels)
    plt.title('Матрица ошибок для NER')
    plt.xlabel('Предсказанные метки')
    plt.ylabel('Истинные метки')
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()
    
    return cm, labels


TEST_DATA = read_data("../data/json_format/val_nofaulty.json")
evaluate_ner_model("../models/model-best", TEST_DATA)
cm, labels = create_ner_confusion_matrix("../models/model-best", TEST_DATA)