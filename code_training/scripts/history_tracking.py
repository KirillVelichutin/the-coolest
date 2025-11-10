import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

class TrainingHistory:
    def __init__(self):
        self.history = {
            'epochs': [],
            'losses': {'ner': []},
            'scores': {'ents_f': [], 'ents_p': [], 'ents_r': []},
            'timestamps': []
        }
    
    def update(self, epoch, losses, scores):
        """Обновление истории с конвертацией float32"""
        self.history['epochs'].append(epoch)
        
        self.history['losses']['ner'].append(float(losses.get('ner', 0)))
        
        for metric in ['ents_f', 'ents_p', 'ents_r']:
            value = scores.get(metric, 0)
            self.history['scores'][metric].append(float(value))
        
        self.history['timestamps'].append(datetime.now().isoformat())
    
    def save(self, filename="../history/training_history.json"):
        safe_history = self._make_json_safe(self.history)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(safe_history, f, indent=2, ensure_ascii=False)
        print(f"История сохранена в {filename}")
    
    def _make_json_safe(self, obj):
        if isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, dict):
            return {key: self._make_json_safe(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_safe(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj
        

def load_training_history(filename="../history/training_history.json"):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            history = json.load(f)
        return history
    except Exception as e:
        print(f"Ошибка загрузки истории: {e}")
        return None

def plot_training_history(history_file="../history/training_history.json"):
    
    history = load_training_history(history_file)
    if history is None:
        return
    
    epochs = history['epochs']
    
    fig, ((ax1, ax2)) = plt.subplots(2, figsize=(15, 10))
    
    ax1.plot(epochs, history['losses']['ner'], 'r-', linewidth=2, label='NER Loss')
    ax1.set_title('Training Losses', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(epochs, history['scores']['ents_f'], 'g-', linewidth=3, label='F1-score')
    ax2.plot(epochs, history['scores']['ents_p'], 'b--', linewidth=2, label='Precision')
    ax2.plot(epochs, history['scores']['ents_r'], 'r--', linewidth=2, label='Recall')
    ax2.set_title('NER scores', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Score')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 1)
    
    
    plt.tight_layout()
    plt.savefig('../history/training_history.png', dpi=300, bbox_inches='tight')
    plt.show()